import asyncio
from asyncio import StreamWriter, StreamReader

from proxy.type_hints import StreamPair

__all__ = ['send_established', 'recv_request', 'forward_stream', 'relay_stream_until_close']


async def send_established(writer: StreamWriter):
    writer.write(b'HTTP/1.1 200 Connection Established\r\n\r\n')
    await writer.drain()


async def recv_request(reader: StreamReader):
    return await reader.readuntil(b'\r\n\r\n')


async def forward_stream(reader: StreamReader, writer: StreamWriter, event: asyncio.Event):
    buffer_size, timeout = 1024, 1
    while not event.is_set():
        try:
            data = await asyncio.wait_for(reader.read(buffer_size), timeout)
        except asyncio.TimeoutError:
            continue

        if data == b'':  # when it closed
            event.set()
            break

        writer.write(data)  # TODO: The case of writer is the closed stream
        await writer.drain()


async def relay_stream_until_close(local_stream: StreamPair, remote_stream: StreamPair):
    local_reader, local_writer = local_stream
    remote_reader, remote_writer = remote_stream

    close_event = asyncio.Event()

    await asyncio.gather(
        forward_stream(local_reader, remote_writer, close_event),
        forward_stream(remote_reader, local_writer, close_event)
    )  # 둘중 하나가 close 되면 나머지 하나도 중단함
