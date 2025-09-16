import asyncio
import datetime
from system.services.logger.logger import Logger


class MetricsCollector:
    def __init__(self, symbols):
        self.logg = Logger()
        self.symbols = symbols

        self.metrics = {
            'data_messages_total': {symbol: 0 for symbol in symbols},
            'data_lag_seconds': {symbol: 0 for symbol in symbols},
            'last_price': {symbol: 0 for symbol in symbols},
            'reconnects_total': 0,
            'errors_total': 0,
        }

    async def writer_task(self, symbol, queue: asyncio.Queue, shared_metrics: dict):
        strategy = 'metrics_collector_writer'
        while True:
            try:
                msg = await queue.get()
                timestamp = datetime.datetime.utcnow()
                event_time = msg.get('E') / 1000

                self.metrics['data_messages_total'][symbol] += 1
                self.metrics['data_lag_seconds'][symbol] = max(0, timestamp.timestamp() - event_time)

                price = float(msg.get('c', 0))
                self.metrics['last_price'][symbol] = price

                # self.logg.logger(
                #     path=strategy,
                #     status='INFO',
                #     text=f'Processed {symbol}: price={price}, total_messages={self.metrics["data_messages_total"][symbol]}'
                # )

                queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as err:
                self.metrics['errors_total'] += 1
                self.logg.err_logg(
                    path=strategy,
                    status=f'{symbol}_METRICS_ERROR',
                    err=err
                )
