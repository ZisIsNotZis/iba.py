from struct import pack, unpack
from typing import Iterable, IO
from datetime import datetime


def decadr(b: int) -> int:
    """
    This function decodes the encrypted address (channel_offset:Oxxxxxxxx) to real address.
    This is the hardest part of ibaAnalyzer file. It uses wired complex address (pointer) encryption.
    Currently only uint32 (i.e. < 2**32, 4G) address are cracked, not sure does it even support int64 address.

    :param b: The encrypted address
    :return: The real address
    """
    b0, b1, b2, b3, b4, b5, b6, b7 = b.to_bytes(8, 'little')
    a0, a1, a2 = b6 ^ b0, b5 ^ b4 ^ b3, b7 ^ b1
    return a0 | a1 << 8 | a2 << 16


def encadr(a: int, b7=0, b6=3, b5=72, b4=97) -> int:
    """
    This is even more wired than above, because the encrypted address space is "underdetermined". Any choice of b7~b4 would decode to the same address.
    And iba uses (probably) cryptologic PRNG to generate part of the address, which is very hard to crack.
    Currently, b7~b4 are carefully choosen to work most of the time. The address is probably different from what real iba dll would generate,
    but it does not error most of the time. No guarantee that it would always work.

    :param a: The real address
    :param b7: magic number
    :param b6: magic number
    :param b5: magic number
    :param b4: magic number
    :return: The encrypted address
    """
    a0, a1, a2 = a.to_bytes(3, 'little')
    b0, b1, b2, b3 = a0 ^ b6, a2 ^ b7, a1 ^ b5 ^ b4, a1 ^ b5 ^ b4
    return b0 | b1 << 8 | b2 << 16 | b3 << 24 | b4 << 32 | b5 << 40 | b6 << 48 | b7 << 56


def encrle(A: Iterable[float | bool], maxrun=255, maxchunk=5000) -> Iterable[list[tuple[int, float | bool]]]:
    """
    Encode run length encoding.
    Iba uses one bytes to encode run length and 1/4 bytes to encode the value bool/float.
    It uses two bytes to encode max chunk size of 5000, though technically that can be 65536.

    :param A: The data
    :param maxrun: max run
    :param maxchunk: max chunk
    :return: Run length encoded data
    """
    b = n = 0
    m = []
    for a in A:
        if a == b:
            n += 1
        if a != b or n == maxrun:
            if n:
                m.append((n, b))
                if len(m) == maxchunk:
                    yield m
                    m = []
            b = a
            n = 1
    if n:
        m.append((n, b))
    if m:
        yield m


def enc(f: str | IO[bytes], begin: str | datetime | None, interval: float, chVals: dict[str, list[float | bool]]) -> None:
    """
    Encode iba file.

    :param f: filename
    :param begin: begin
    :param interval: interval in seconds
    :param chVals: data
    :return: None
    """
    iChValss = [(i + (i & 0xffe0) | isinstance(vals[0], bool) << 5, ch, list(encrle(vals))) for i, (ch, vals) in enumerate(chVals.items())]
    iChValss.sort(key=lambda i: isinstance(i[2][0][0][1], bool))
    n = 8 + 4 + 20
    f = open(f, 'wb') if isinstance(f, str) else f
    f.write(b'PDA2\x3E\xC2\x8F\x9D')
    f.write((n + sum(2 + 4 + (2 if isinstance(vals[0][1], bool) else 5) * len(vals) for i, ch, valss in iChValss for vals in valss)).to_bytes(4, 'little'))
    f.write(b'\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0\0')
    adrs: list[int] = []
    for i, ch, valss in iChValss:
        adrs.append(n)
        for nxt, vals in zip(range(len(valss))[::-1], valss):
            n += 2 + 4 + (2 if isinstance(vals[0][1], bool) else 5) * len(vals)
            f.write(len(vals).to_bytes(2, 'little'))
            f.write((n if nxt else 0).to_bytes(4, 'little'))
            for ct, val in vals:
                f.write(ct.to_bytes(1, 'little'))
                f.write((b'\xC0' if val else b'\x40') if isinstance(val, bool) else pack('f', val))
    f.write(b'beginheader:\r\nstarttime:')
    f.write((datetime.fromisoformat(begin) if isinstance(begin, str) else datetime.now() if begin is None else begin).strftime('%d.%m.%Y %H:%M:%S').encode())
    f.write(b'.0000\r\nclk:')
    f.write(str(interval).encode())
    f.write(b'\r\nibaFiles:3.2\r\ntyp:int16\r\nframes:' if all(isinstance(valss[0][0][1], bool) for i, ch, valss in iChValss) else b'\r\nibaFiles:3.2\r\ntyp:real\r\nframes:')
    f.write(str(sum(c for val in iChValss[0][2] for c, v in val)).encode())
    f.write(b'\r\nendheader:\r\n')
    for (i, ch, valss), adr in zip(iChValss, adrs):
        f.write(b'beginchannel:')
        f.write(str(i).encode())
        f.write(b'\r\nname:')
        f.write(ch.encode())
        f.write(b'\r\nchannel_offset:O')
        f.write(hex(encadr(adr))[2:].encode())
        f.write(b'\r\ndigchannel:\r\nendchannel:\r\n' if isinstance(valss[0][0][1], bool) else b'\r\nendchannel:\r\n')


def dec(f: str | IO[bytes]) -> tuple[datetime, float, dict[str, list[float | bool]]]:
    """
    Decode iba file.

    :param f: filename
    :return: begin, interval in seconds, data
    """
    f = open(f, 'rb') if isinstance(f, str) else f
    f.read(8)
    f.seek(int.from_bytes(f.read(4), 'little'))
    _ = f.read()
    t = datetime.strptime(_.split(b'\r\nstarttime:')[1].split(b'.0000')[0].decode(), '%d.%m.%Y %H:%M:%S')
    clk = float(_.split(b'\r\nclk:')[1].split()[0])
    chVals: dict[str, list[float | bool]] = {}
    for i in _.split(b'\r\nname:')[1:]:
        name = i.split()[0]
        dig = b'\r\ndigchannel:' in i
        nxt = decadr(int(i.split(b'\r\nchannel_offset:O')[1].split()[0], 16))
        vals: list[float | bool] = []
        chVals[name.decode()] = vals
        while nxt:
            f.seek(nxt)
            n = int.from_bytes(f.read(2), 'little')
            nxt = int.from_bytes(f.read(4), 'little')
            for _ in range(n):
                c = int.from_bytes(f.read(1), 'little')
                v = [f.read(1) == b'\xC0'] if dig else unpack('f', f.read(4))
                vals += v * c
    return t, clk, chVals