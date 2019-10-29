import re
from typing import Optional

__all__ = ['RawHTTPParser']


def to_str(item: Optional[bytes]) -> Optional[str]:
    if item:
        return item.decode('charmap')


def to_int(item: Optional[bytes]) -> Optional[int]:
    if item:
        return int(item)


class RawHTTPParser:
    pattern = re.compile(
        br'(?P<method>[a-zA-Z]+) (?P<uri>(\w+://)?(?P<host>[^\s\'\"<>\[\]{}|/:]+)(:(?P<port>\d+))?[^\s\'\"<>\[\]{}|]*) ')
    uri: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    method: Optional[str] = None
    is_parse_error: bool = False

    def __init__(self, raw: bytes):
        rex = self.pattern.match(raw)
        if rex:
            self.uri = to_str(rex.group('uri'))
            self.host = to_str(rex.group('host'))
            self.method = to_str(rex.group('method'))
            self.port = to_int(rex.group('port'))
        else:
            self.is_parse_error = True

    def __str__(self):
        return str(dict(URI=self.uri, HOST=self.host, PORT=self.port, METHOD=self.method))
