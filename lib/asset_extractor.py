import os
import UnityPy
from collections import Counter
import zipfile

TYPES = ["Sprite", "Texture2D", "TextAsset"]
IGNOR_DIR_COUNT = 2


def extract_assets(src, dst, debug=False):
    # load source
    am = UnityPy.load(src)

    # iterate over assets
    for asset in am.assets.values():
        # assets without container / internal path will be ignored for now
        if not asset.container:
            continue

        # check which mode we will have to use
        num_cont = sum(1 for obj in asset.container.values() if obj.type in TYPES)
        num_objs = sum(1 for obj in asset.objects.values() if obj.type in TYPES)

        # check if container contains all important assets, if yes, just ignore the container
        if num_objs <= num_cont * 2:
            for asset_path, obj in asset.container.items():
                fp = os.path.join(dst, *asset_path.split("/")[IGNOR_DIR_COUNT:])
                export_obj(obj, fp, debug=True)

        # otherwise use the container to generate a path for the normal objects
        else:
            extracted = []
            # find the most common path
            occurence_count = Counter(
                os.path.splitext(asset_path)[0] for asset_path in asset.container.keys()
            )
            local_path = os.path.join(
                dst, *occurence_count.most_common(1)[0][0].split("/")[IGNOR_DIR_COUNT:]
            )

            for obj in asset.objects.values():
                if obj.path_id not in extracted:
                    extracted.extend(
                        export_obj(obj, local_path, append_name=True, debug=True)
                    )


def export_obj(obj, fp: str, append_name: bool = False, debug=False) -> list:
    try:
        if obj.type not in TYPES:
            return []
        data = obj.read()
        if append_name:
            fp = os.path.join(fp, data.name)

        fp, extension = os.path.splitext(fp)
        os.makedirs(os.path.dirname(fp), exist_ok=True)

        if obj.type == "TextAsset":
            if not extension:
                extension = ".txt"
            fp = f"{fp}{extension}"
            with open(fp, "wb") as f:
                f.write(data.script)

            if debug and not os.path.exists(fp):
                print(fp)

        elif obj.type == "Sprite":
            extension = ".png"
            fp = f"{fp}{extension}"
            data.image.save(fp)
            if debug and not os.path.exists(fp):
                print(fp)

            return [
                obj.path_id,
                data.m_RD.texture.path_id,
                getattr(data.m_RD.alphaTexture, "path_id", None),
            ]

        elif obj.type == "Texture2D":
            extension = ".png"
            fp = f"{fp}{extension}"
            if not os.path.exists(fp):
                try:
                    data.image.save(fp)
                except EOFError:
                    pass
            if debug and not os.path.exists(fp):
                print(fp)
        return [obj.path_id]
    except Exception as e:
        print(e, fp)
        return []

