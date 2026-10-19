#!/usr/bin/env python3
"""
Minimal PNG reader (stdlib only).

Chrome's `--screenshot` writes 8-bit PNGs; this reads them back so a
rendered artifact or a reference screenshot can be measured without any
image dependency.

Supports bit depth 8, colour types 0 (grey), 2 (RGB), 3 (palette),
4 (grey+alpha) and 6 (RGBA), non-interlaced.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class PngError(Exception):
    pass


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _unfilter(raw: bytes, width: int, height: int, bpp: int) -> bytearray:
    stride = width * bpp
    out = bytearray(height * stride)
    pos = 0
    prev = bytearray(stride)
    for y in range(height):
        if pos >= len(raw):
            break
        ft = raw[pos]
        pos += 1
        line = bytearray(raw[pos: pos + stride])
        if len(line) < stride:
            line.extend(b"\x00" * (stride - len(line)))
        pos += stride
        if ft == 1:      # Sub
            for i in range(bpp, stride):
                line[i] = (line[i] + line[i - bpp]) & 0xFF
        elif ft == 2:    # Up
            for i in range(stride):
                line[i] = (line[i] + prev[i]) & 0xFF
        elif ft == 3:    # Average
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + ((left + prev[i]) >> 1)) & 0xFF
        elif ft == 4:    # Paeth
            for i in range(stride):
                left = line[i - bpp] if i >= bpp else 0
                up = prev[i]
                ul = prev[i - bpp] if i >= bpp else 0
                line[i] = (line[i] + _paeth(left, up, ul)) & 0xFF
        elif ft != 0:
            raise PngError(f"unsupported filter type {ft}")
        out[y * stride:(y + 1) * stride] = line
        prev = line
    return out


def read_png(path: str | Path) -> tuple[int, int, list[tuple[int, int, int]]]:
    """Return (width, height, pixels) where pixels is a list of (r, g, b)."""
    data = Path(path).read_bytes()
    if data[:8] != PNG_SIGNATURE:
        raise PngError("not a PNG file")

    pos = 8
    width = height = depth = ctype = interlace = 0
    idat = bytearray()
    palette = b""
    trns = b""
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos: pos + 4])[0]
        ctype_name = data[pos + 4: pos + 8]
        body = data[pos + 8: pos + 8 + length]
        pos += 12 + length
        if ctype_name == b"IHDR":
            width, height, depth, ctype, _comp, _filt, interlace = struct.unpack(
                ">IIBBBBB", body[:13]
            )
        elif ctype_name == b"PLTE":
            palette = body
        elif ctype_name == b"tRNS":
            trns = body
        elif ctype_name == b"IDAT":
            idat.extend(body)
        elif ctype_name == b"IEND":
            break

    if not width or not height:
        raise PngError("missing IHDR")
    if depth != 8:
        raise PngError(f"unsupported bit depth {depth} (only 8 is supported)")
    if interlace:
        raise PngError("interlaced PNGs are not supported")

    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(ctype)
    if channels is None:
        raise PngError(f"unsupported colour type {ctype}")

    raw = zlib.decompress(bytes(idat))
    stride = width * channels
    flat = _unfilter(raw, width, height, channels)

    pixels: list[tuple[int, int, int]] = []
    if ctype == 3:
        pal = []
        for i in range(0, len(palette), 3):
            pal.append((palette[i], palette[i + 1], palette[i + 2]))
        for y in range(height):
            row = flat[y * stride:(y + 1) * stride]
            for x in range(width):
                idx = row[x]
                pixels.append(pal[idx] if idx < len(pal) else (0, 0, 0))
    elif ctype == 0:
        for y in range(height):
            row = flat[y * stride:(y + 1) * stride]
            for x in range(width):
                v = row[x]
                pixels.append((v, v, v))
    elif ctype == 4:
        for y in range(height):
            row = flat[y * stride:(y + 1) * stride]
            for x in range(width):
                v = row[x]
                pixels.append((v, v, v))
    elif ctype == 2:
        for y in range(height):
            row = flat[y * stride:(y + 1) * stride]
            for x in range(width):
                o = x * 3
                pixels.append((row[o], row[o + 1], row[o + 2]))
    else:  # 6 — RGBA
        for y in range(height):
            row = flat[y * stride:(y + 1) * stride]
            for x in range(width):
                o = x * 4
                pixels.append((row[o], row[o + 1], row[o + 2]))

    return width, height, pixels


def png_size(path: str | Path) -> tuple[int, int] | None:
    """Read width/height from the IHDR header without decoding pixels."""
    try:
        head = Path(path).read_bytes()[:24]
    except OSError:
        return None
    if len(head) < 24 or head[:8] != PNG_SIGNATURE:
        return None
    return struct.unpack(">II", head[16:24])


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(__doc__.strip())
        sys.exit(2)
    w, h, px = read_png(sys.argv[1])
    print(f"{w}x{h} — {len(px)} pixels")
