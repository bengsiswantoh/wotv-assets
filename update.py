import os
from lib import API, download_all, update_version, encryption_helper
from lib.version import extract_version

ROOT = os.path.dirname(os.path.realpath(__file__))

VERSION = [
    ("global", "com.square_enix.android_googleplay.WOTVffbeww",),
    # ("japan", "com.square_enix.WOTVffbejp",),
    # ("china", "com.seasun.WOTVffbecn.aligames")
]

for ver, apk_name in VERSION:
    extract_dir = os.path.join(ROOT, ver)
    assets_dir = extract_dir + "_raw"

    os.makedirs(extract_dir, exist_ok=True)
    os.makedirs(assets_dir, exist_ok=True)

    try:
        HOST, VERSION, SHARED_KEY = extract_version(apk_name, assets_dir)
        encryption_helper.a_shared_key = SHARED_KEY
        environment = API(api=HOST.split("://", 1)[1][:-1]).pass_enviroment(VERSION)
    except (KeyError, FileNotFoundError):
        HOST, VERSION, SHARED_KEY = update_version(apk_name, assets_dir)
        encryption_helper.a_shared_key = SHARED_KEY
        environment = API(api=HOST.split("://", 1)[1][:-1]).pass_enviroment(VERSION)

    download_all(environment, assets_dir, extract_dir)
