import struct
import io

# 4 (int) - signature
# 4 (int) - tile count
# Tile:
#   4 (int) - x
#   4 (int) - y
#   4 (int) - h
#   2 (short) - text length
#   text

def parse_map(f):
    if isinstance(f, str):
        f = open(f, "rb")
    elif isinstance(f, (bytearray, bytes)):
        f = io.BytesIO(f)
    
    f.read(4)
    tile_count, = struct.unpack("<I", f.read(4))
    for _ in range(tile_count):
        x,y,h,tl = struct.unpack("<IIIH", f.read(14))
        map[(x,y)] = {
            "h" : h,
            "t" : f.read(tl).decode("ascii")
        }
    return map