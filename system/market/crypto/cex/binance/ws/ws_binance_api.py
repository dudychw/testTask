import asyncio
import random
import time
from binance import AsyncClient, BinanceSocketManager
from system.services.logger.logger import Logger


RECONNECT_BASE_DELAY = 1
RECONNECT_MAX_DELAY = 32


class WSBinance:
    def __init__(self, symbols):
        self.logg = Logger()
        self.ex_name = self.__class__.__name__.upper()

        self.symbols = symbols
        self.queues = {symbol: asyncio.Queue() for symbol in symbols}
        self.metrics = {
            'data_messages_total': {symbol: 0 for symbol in symbols},
            'reconnects_total': 0,
            'errors_total': 0,
            'last_message_time': {symbol: 0 for symbol in symbols}
        }

    async def subscribe_symbol(self, client, symbol, strategy='base'):
        reconnect_delay = RECONNECT_BASE_DELAY
        while True:
            try:
                bsm = BinanceSocketManager(client)
                stream = bsm.symbol_ticker_socket(symbol.lower())

                async with stream as ws:
                    while True:
                        msg = await ws.recv()
                        self.metrics['data_messages_total'][symbol] += 1
                        self.metrics['last_message_time'][symbol] = time.time()

                        await self.queues[symbol].put(msg)

                reconnect_delay = RECONNECT_BASE_DELAY
            except Exception as err:
                self.metrics['errors_total'] += 1
                self.logg.err_logg(path=strategy, status=f"{self.ex_name}_{symbol}_ERROR", err=err)

            jitter = random.uniform(0, 1)
            wait_time = min(reconnect_delay + jitter, RECONNECT_MAX_DELAY)
            self.logg.logger(path=strategy, status='WARNING', text=f'Reconnecting {symbol} in {wait_time:.2f}s')
            await asyncio.sleep(wait_time)
            reconnect_delay = min(reconnect_delay * 2, RECONNECT_MAX_DELAY)
            self.metrics['reconnects_total'] += 1

    async def start(self, strategy='base'):
        client = None
        retry_delay = 1

        while not client:
            try:
                client = await AsyncClient.create()
            except Exception as err:
                self.logg.err_logg(path=strategy, status='ASYNC_CLIENT_CREATE_ERROR', err=err)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 2, 32)

        tasks = []
        for symbol in self.symbols:
            tasks.append(asyncio.create_task(self.subscribe_symbol(client, symbol, strategy)))

        await asyncio.gather(*tasks)
        await client.close()
