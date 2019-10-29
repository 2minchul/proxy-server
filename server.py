import asyncio

from proxy import Proxy, SessionContext
from proxy.exceptions import ParseError, MethodNotSupport, ProxyTimeout


class MyProxy(Proxy):
    async def on_server_start(self):
        print(f'Serving on {self.addr}')

    async def on_close(self, context: SessionContext):
        if context.exception:
            try:
                raise context.exception
            except ParseError:
                print('Parse Error')
            except MethodNotSupport:
                print(f'{context.request.method} method is not supported')
            except ProxyTimeout:
                print('Timeout')

        print(f'Closed connection')

    async def on_connect(self, context: SessionContext):
        print(f"Connected from {context.addr!r}")

    async def on_receive(self, context: SessionContext):
        print(f'Request: {str(context.request)}')

    async def on_received_https(self, context: SessionContext):
        print('HTTPS connection established')


if __name__ == '__main__':
    asyncio.run(MyProxy('127.0.0.1', 8888).run_server())
