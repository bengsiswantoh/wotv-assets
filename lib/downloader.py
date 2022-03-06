import json
from urllib.request import urlopen
import UnityPy
import os
from .api import API
from .asset_extractor import extract_assets
from .version import update_version
import sys

url = "{host}{version}/{system}/{package}/{id}"
SYSTEM = "android"

main_id = 2705996037
sub_id = 515017172


def download_all(environment, asset_dir, extract_dir, version_overwrite = None):
    host = environment["dlc_url"]
    version = environment["dlc_ver"] if version_overwrite == None else version_overwrite

    # fetch the main package that holds meta-data about all sub dirs
    main = download(
        package="main", id=main_id, host=host, version=version, system=SYSTEM
    )
    os.makedirs(asset_dir, exist_ok=True)
    with open(os.path.join(asset_dir, str(main_id)), "wb") as f:
        f.write(main)

    main = get_container(main)["infos"]

    # iterate over all sub dirs
    for info in main:
        name = info["name"]
        # ignore the voice overs for now
        if name[:2] == "vo":
            continue
        sub = download(
            package=name, id=sub_id, host=host, version=version, system=SYSTEM
        )

        dst = os.path.join(asset_dir, name)
        os.makedirs(dst, exist_ok=True)
        with open(os.path.join(dst, str(sub_id)), "wb") as f:
            f.write(sub)

        # download the sub sub dirs
        sub = get_container(sub)
        os.makedirs(dst, exist_ok=True)
        for type_info in sub["type_infos"]:
            for asset in type_info["ab_infos"]:
                a_name = asset["ab_name"]
                fp = os.path.join(dst, *a_name.split("/"))
                os.makedirs(os.path.dirname(fp), exist_ok=True)
                # ignore existing files that already have the correct size
                if os.path.exists(fp) and os.path.getsize(fp) == asset["size"]:
                    continue
                print(a_name)
                data = download(
                    package=name, id=a_name, host=host, version=version, system=SYSTEM
                )
                with open(fp, "wb") as f:
                    f.write(data)

                try:
                    extract_assets(data, extract_dir, debug=True)
                except:
                    print(sys.exc_info()[2])


def download(**kwargs):
    print(url.format(**kwargs))
    return urlopen(url.format(**kwargs)).read()


def get_container(data):
    am = UnityPy.load(data)
    for obj in am.container.values():
        return json.loads(obj.read().text)
