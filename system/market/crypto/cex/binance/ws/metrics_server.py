import asyncio

from aiohttp import web
from system.services.logger.logger import Logger


class MetricsHTTPServer:
    def __init__(self, metrics_collector):
        self.metrics_collector = metrics_collector
        self.logg = Logger()
        self.strategy = 'metrics_http_server'

        self.app = web.Application()
        self.app.router.add_get('/health', self.health_handler)
        self.app.router.add_get('/metrics', self.metrics_handler)

    async def health_handler(self, request):
        try:
            healthy = all(
                lag < 10
                for lag in self.metrics_collector.metrics['data_lag_seconds'].values()
            )
            status = 'OK' if healthy else 'FAIL'

            self.logg.logger(
                path=self.strategy,
                status='INFO',
                text=f'Health check; status={status}'
            )

            return web.Response(text=status)
        except Exception as e:
            self.logg.err_logg(
                path=self.strategy,
                status='HEALTH_HANDLER_ERROR',
                err=e
            )
            return web.Response(status=500, text='ERROR')

    async def metrics_handler(self, request):
        try:
            metrics = []
            for symbol in self.metrics_collector.symbols:
                metrics.append(
                    f'data_messages_total{{symbol="{symbol}"}} {self.metrics_collector.metrics["data_messages_total"][symbol]}'
                )
                metrics.append(
                    f'data_lag_seconds{{symbol="{symbol}"}} {self.metrics_collector.metrics["data_lag_seconds"][symbol]:.3f}'
                )
                metrics.append(
                    f'last_price{{symbol="{symbol}"}} {self.metrics_collector.metrics["last_price"][symbol]:.8f}'
                )
            metrics.append(f'reconnects_total {self.metrics_collector.metrics["reconnects_total"]}')
            metrics.append(f'errors_total {self.metrics_collector.metrics["errors_total"]}')

            self.logg.logger(
                path=self.strategy,
                status='INFO',
                text=f'/metrics check'
            )

            return web.Response(text='\n'.join(metrics))
        except Exception as e:
            self.logg.err_logg(
                path=self.strategy,
                status='METRICS_HANDLER_ERROR',
                err=e
            )
            return web.Response(status=500, text='ERROR')

    async def run(self):
        try:
            port = 8000
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()

            self.logg.logger(
                path=self.strategy,
                status='INFO',
                text=f'Metrics HTTP server started on port {port}'
            )

            while True:
                await asyncio.sleep(60 * 60)
        except Exception as e:
            self.logg.err_logg(
                path=self.strategy,
                status='SERVER_RUN_ERROR',
                err=e
            )
