import os
import UnityPy
from collections import Counter
import sys

TYPES = [
    "MeshRenderer",
    "SkinnedMeshRenderer",
    "Renderer",
    "Sprite",
    "Texture2D",
    "TextAsset",
    "AudioClip",
    #"Mesh", - replaced by Renderer export
    "Font",
    "Shader",
]
IGNOR_DIR_COUNT = 2


def extract_assets(src, dst, debug=False):
    # load source
    am = UnityPy.load(src)

    # iterate over assets
    for asset in am.assets:
        # assets without container / internal path will be ignored for now
        if not asset.container:
            continue

        # check which mode we will have to use
        num_cont = sum(1 for obj in asset.container.values() if obj.type.name in TYPES)
        num_objs = sum(1 for obj in asset.get_objects() if obj.type.name in TYPES)

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

            for obj in asset.get_objects():
                if obj.path_id not in extracted:
                    extracted.extend(
                        export_obj(obj, local_path, append_name=True, debug=True)
                    )


def export_obj(obj, fp: str, append_name: bool = False, debug=False) -> list:
    try:
        if obj.type.name not in TYPES:
            return []
        data = obj.read()
        type_name = obj.type.name

        if "Renderer" in type_name:
            if append_name and data.m_GameObject:
                name = os.path.join(fp, data.m_GameObject.read().name)
                if os.path.split(fp)[-1] != name:
                    fp = os.path.join(fp, name)
            data.export(fp)
            return [obj.path_id]
        
        if append_name:
            fp = os.path.join(fp, data.name)

        fp, extension = os.path.splitext(fp)
        os.makedirs(os.path.dirname(fp), exist_ok=True)

        if type_name == "TextAsset":
            if not extension:
                extension = ".txt"
            fp = f"{fp}{extension}"

            with open(fp, "wb") as f:
                f.write(data.script)

            if debug and not os.path.exists(fp):
                print(fp)

        elif type_name == "Sprite":
            extension = ".png"
            fp = f"{fp}{extension}"
            print("Saving Sprite to: ", fp)
            data.image.save(fp)
            if debug and not os.path.exists(fp):
                print(fp)

            return [
                obj.path_id,
                data.m_RD.texture.path_id,
                getattr(data.m_RD.alphaTexture, "path_id", None),
            ]

        elif type_name == "Texture2D":
            extension = ".png"
            fp = f"{fp}{extension}"
            if not os.path.exists(fp):
                print("Saving Texture2D to: ", fp)
                data.image.save(fp)
            if debug and not os.path.exists(fp):
                print(fp)

        elif type_name == "AudioClip":
            for name, bdata in data.samples.items():
                extension = ".wav"
                fp = f"{fp}_{name}{extension}"
                with open(fp, "wb") as f:
                    f.write(bdata)

        elif type_name == "Mesh":
            extension = ".obj"
            fp = f"{fp}{extension}"
            with open(fp, "wt", encoding="utf8", newline="") as f:
                f.write(data.export())

        elif type_name == "Font":
            if data.m_FontData:
                extension = ".ttf"
                if data.m_FontData[0:4] == b"OTTO":
                    extension = ".otf"
                with open(f"{fp}{extension}", "wb") as f:
                    f.write(data.m_FontData)

        elif type_name == "Shader":
            extension = ".txt"
            with open(f"{fp}{extension}", "wt", encoding="utf8", newline="") as f:
                f.write(data.export())

        return [obj.path_id]
    except:
        print(sys.exc_info())
