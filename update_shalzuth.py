import os
import json
from lib import API, download_all, update_version

from urllib.request import urlopen
import re

commits = json.loads(
    urlopen("https://api.github.com/repos/shalzuth/wotv-ffbe-dump/commits").read()
)

VERSION = [
    (
        "global",
        "com.square_enix.android_googleplay.WOTVffbeww",
        next(
            commit["commit"]["message"]
            for commit in commits
            if "/" not in commit["commit"]["message"]
        ),
    ),
    (
        "japan",
        "com.square_enix.WOTVffbejp",
        next(
            commit["commit"]["message"]
            for commit in commits
            if "/" in commit["commit"]["message"]
        ),
    ),
]

ROOT = os.path.dirname(os.path.realpath(__file__))

for ver, apk, commit in VERSION:
    extract = os.path.join(ROOT, ver)
    assets = extract + "_raw"

    os.makedirs(extract, exist_ok=True)
    os.makedirs(assets, exist_ok=True)

    try:
        with open(os.path.join(assets, "version.json"), "rt", encoding="utf8") as f:
            HOST, app_ver = list(json.load(f).values())

        environment = API(api=HOST.split("://", 1)[1][:-1]).pass_enviroment(app_ver)
    except (KeyError, FileNotFoundError):
        HOST, VERSION = update_version(apk, assets)
        environment = API(api=HOST.split("://", 1)[1][:-1]).pass_enviroment(app_ver)

    download_all(environment, assets, extract, commit)
