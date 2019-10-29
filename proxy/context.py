from asyncio import StreamReader, StreamWriter
from proxy.parser import RawHTTPParser
from proxy.type_hints import Address

__all__ = ['SessionContext']


class SessionContext:
    reader: StreamReader
    writer: StreamWriter
    exception: Exception = None
    addr: Address
    request: RawHTTPParser

    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.reader = reader
        self.writer = writer
        self.addr = writer.get_extra_info('peername')
