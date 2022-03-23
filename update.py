from base64 import b64decode
import os
import json
from lib import API, download_all, update_version, encryption_helper
from lib.version import load_version_consts

ROOT = os.path.dirname(os.path.realpath(__file__))

VERSION = [
    ("global", "com.square_enix.android_googleplay.WOTVffbeww",),
    #("japan", "com.square_enix.WOTVffbejp",),
    ("china", "com.seasun.WOTVffbecn.aligames")
]

for ver, apk in VERSION:
    extract = os.path.join(ROOT, ver)
    assets = extract + "_raw"

    os.makedirs(extract, exist_ok=True)
    os.makedirs(assets, exist_ok=True)

    try:
        HOST, VERSION, SHARED_KEY = load_version_consts(assets)
        encryption_helper.a_shared_key = SHARED_KEY
        environment = API(api=HOST.split("://", 1)[1][:-1]).pass_enviroment(VERSION)
    except (KeyError, FileNotFoundError):
        HOST, VERSION, SHARED_KEY = update_version(apk, assets)
        encryption_helper.a_shared_key = SHARED_KEY
        environment = API(api=HOST.split("://", 1)[1][:-1]).pass_enviroment(VERSION)

    download_all(environment, assets, extract)
