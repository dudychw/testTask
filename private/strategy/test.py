import asyncio
import datetime
import os

from system.services.logger.logger import Logger
from system.market.crypto.cex.binance.ws.ws_binance_api import WSBinance
from system.market.crypto.cex.binance.ws.metrics_collector import MetricsCollector
from system.market.crypto.cex.binance.ws.metrics_server import MetricsHTTPServer


class Test:
    def __init__(self):
        self.logg = Logger()
        self.file_name = os.path.basename(__file__)[:-3]
        self.symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'SOLUSDT']

    async def start(self):
        start_time = datetime.datetime.now()
        self.logg.logger(
            path=self.file_name,
            status='INFO',
            text=f"Script started at {start_time}"
        )

        try:
            ws_binance = WSBinance(self.symbols)
            metrics_collector = MetricsCollector(self.symbols)
            metrics_server = MetricsHTTPServer(metrics_collector)

            asyncio.create_task(metrics_server.run())

            for symbol in self.symbols:
                asyncio.create_task(
                    metrics_collector.writer_task(symbol, ws_binance.queues[symbol], ws_binance.metrics)
                )

            self.logg.logger(
                path=self.file_name,
                status='INFO',
                text=f"Start"
            )

            await ws_binance.start(strategy=self.file_name)

        except Exception as e:
            self.logg.err_logg(
                path=self.file_name,
                status='MAIN_RUN_ERROR',
                err=e
            )
        finally:
            dlt = datetime.datetime.now() - start_time
            self.logg.logger(
                path=self.file_name,
                status='INFO',
                text=f"Finish. Time worked: {dlt}"
            )
