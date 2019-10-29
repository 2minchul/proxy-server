from asyncio.streams import StreamReader, StreamWriter
from typing import Tuple, TypeVar, Generic

__all__ = ['StreamPair', 'Address', 'Server', 'T_Server']

StreamPair = Tuple[StreamReader, StreamWriter]
Address = Tuple[str, int]
Server = TypeVar('Server')
T_Server = Generic[Server]
