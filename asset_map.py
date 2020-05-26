import os
import UnityPy
import json

ROOT = os.path.dirname(os.path.realpath(__file__))
for v in ["global","japan"]:
    ASSETS = {}
    for root, dirs, files in os.walk(os.path.join(ROOT, v+"_raw")):
        for fp in files:
            env = UnityPy.load(os.path.join(root, fp))

            path = os.path.join(root, fp)
            ASSETS["/".join(path.split("\\")[-3:])] = list(env.container.keys())
    with open(v+"_map.json", "wb") as f:
        f.write(json.dumps(ASSETS, indent=4, ensure_ascii=False).encode("utf8"))