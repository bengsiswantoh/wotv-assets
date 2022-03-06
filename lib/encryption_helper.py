from enum import IntEnum
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util import Padding
from PIL import Image, ImageOps
from base64 import b64decode

a_shared_key = b""


class DecryptOptions(IntEnum):
    None_ = 0
    IsFile = 1
    ExtraKeySaltAT = 2
    ExtraKeySaltATDI = 3


def deserialize_fromBase64_string(base64text: str, keySalt: str):
    # base64text = stored as TextAsset
    # keySalt = paramName
    return decrypt(b64decode(base64text), keySalt)


def decrypt(
    data: bytes, keySalt: str, requestId: str = None, customKey: bytes = None
) -> bytes:
    # CBC & PKCS7 padding
    # keysize & blocksize 128

    iv = data[:0x10]

    pre_key = a_shared_key + shake_key_salt(keySalt)
    if requestId:
        pre_key += requestId.encode("ascii")

    #  pre_key += Gsc_Auth_ISession_TypeInfo
    key = SHA256.SHA256Hash(pre_key).digest()[:0x10]

    managed = AES.new(key, iv=iv, mode=AES.MODE_CBC)

    return Padding.unpad(managed.decrypt(data[0x10:]), block_size=0x10, style="pkcs7")


def get_shared_key(texture: Image) -> bytes:
    keyImageAsset = ImageOps.flip(texture)

    bit_count = 0
    index = 0
    num = 0

    key = bytearray(16)
    data = keyImageAsset.tobytes()
    for color_val in data:
        num = (num << 1) + (color_val & 1)
        bit_count += 1

        if bit_count % 8 == 0:
            num = reverse_bits(num)
            if num:
                key[index] = num
                index += 1
            else:
                return key


def init_shared_key(texture_fp: Image):
    global a_shared_key
    img = Image.open(texture_fp)
    a_shared_key = get_shared_key(img)
    img.close()


def shake_key_salt(keySalt: str):
    return keySalt.encode("ascii")[::-1]


def reverse_bits(num):
    result = 0
    for _ in range(8):
        result = (result << 1) + (num & 1)
        num >>= 1
    return result
