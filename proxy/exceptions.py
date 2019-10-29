import asyncio

__all__ = ['ProxyException', 'ProtocolException', 'ParseError', 'MethodNotSupport', 'ProxyTimeout']


class ProxyException(Exception):
    pass


class ProtocolException(ProxyException):
    pass


class ParseError(ProtocolException):
    pass


class MethodNotSupport(ProtocolException):
    pass


class ProxyTimeout(ProxyException, TimeoutError, asyncio.TimeoutError):
    pass
