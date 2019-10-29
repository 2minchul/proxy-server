import asyncio
from asyncio import StreamReader, StreamWriter
from contextlib import closing
from typing import Awaitable, Callable

import async_timeout

import proxy.protocol as protocol
from proxy.context import SessionContext
from proxy.exceptions import *
from proxy.parser import RawHTTPParser
from proxy.type_hints import StreamPair, T_Server, Address

__all__ = ['Proxy']


def callback_decorator(callback: Awaitable):
    def decorator(f: Callable[..., Awaitable]):
        async def wrapped_coroutine(*args, **kwargs):
            try:
                result = await f(*args, **kwargs)
            except:
                await callback
                raise

            await callback
            return result

        return wrapped_coroutine

    return decorator


def timeout_decorator(context: SessionContext, timeout: int):
    def decorator(f: Callable[..., Awaitable]):
        async def wrapped_coroutine(*args, **kwargs):
            try:
                return await asyncio.wait_for(f(*args, **kwargs), timeout)
            except asyncio.TimeoutError:
                context.exception = ProxyTimeout()

        return wrapped_coroutine

    return decorator


class Proxy(T_Server):
    host: str
    port: int
    addr: Address

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def run_server(self):
        server = await asyncio.start_server(
            self.main_handler, self.host, self.port
        )
        self.addr = server.sockets[0].getsockname()
        await self.on_server_start()

        async with server:
            await server.serve_forever()

    async def run_client_once(self):
        stream_pair: StreamPair = await asyncio.open_connection(self.host, self.port)
        await self.on_server_start()
        task = await self.main_handler(*stream_pair)
        await asyncio.wait(task)

    async def main_handler(self, reader: StreamReader, writer: StreamWriter, timeout=30):
        context = SessionContext(reader, writer)

        def raise_exception(exception: Exception):
            context.exception = exception
            raise exception

        @callback_decorator(self.on_close(context))
        @timeout_decorator(context, timeout)
        async def session():
            await self.on_connect(context)
            try:
                with closing(writer):
                    data = await protocol.recv_request(reader)
                    print(f"Received {data} from {context.addr!r}")
                    request = context.request = RawHTTPParser(data)
                    await self.on_receive(context)

                    if request.is_parse_error:
                        raise_exception(ParseError())

                    elif request.method == 'CONNECT':  # https
                        await self.https_handler(context)
                    else:
                        raise_exception(MethodNotSupport())
            except ProxyException:
                pass

        return asyncio.create_task(session())

    async def https_handler(self, context: SessionContext):
        request = context.request
        remote_reader, remote_writer = await asyncio.open_connection(request.host, request.port)
        with closing(remote_writer):
            await protocol.send_established(context.writer)
            await self.on_received_https(context)
            await protocol.relay_stream_until_close((context.reader, context.writer),
                                                    (remote_reader, remote_writer))

    async def on_server_start(self):
        pass

    async def on_close(self, context: SessionContext):
        pass

    async def on_connect(self, context: SessionContext):
        pass

    async def on_receive(self, context: SessionContext):
        pass

    async def on_received_https(self, context: SessionContext):
        pass
