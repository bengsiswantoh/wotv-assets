import os
import re
import shutil
from PIL import Image

ROOT = os.path.dirname(os.path.realpath(__file__))
DEST = os.path.join(ROOT, "images")
reImgPath = re.compile(".+[\\/]+(.+?)[\\/]+(.+?)[\\/]+(.+?)[\\/]+(.+)")

DESTS = {
    "job" : "",
    "unit icon" : "",
    "unit": "",
    "esper icon" : "",
    "gear" : "",
    "item" : "",
    "vision" : "",
    "vision icon" : "",
}
for key in DESTS.keys():
    folder = os.path.join(DEST, key)
    os.makedirs(folder, exist_ok=True)
    DESTS[key] = folder

def main():
    for ver in ["global", "japan"]:
        copy(os.path.join(ROOT, ver))

def copy(src):
    # Unit Folder
    path = os.path.join(src, "unit")
    IGNOR = ["_angry","_sad","_smile","_surprised","_alt"]
    for root, _, files in os.walk(path):
        for f in files:
            match = reImgPath.match(root)
            if match[4] != "icon":
                continue
            sfp = os.path.join(root, f)
            # generate name
            indicator = ""
            if match[2] == "job":
                indicator == "job"
            elif match[2] == "unit":
                indicator = f[-6:-3]
                if indicator == "_m.":
                    indicator = "unit icon"
                elif indicator == "_s.":
                    indicator = "esper icon"
                elif any(x in f for x in IGNOR):
                    continue
                else:
                    indicator = "unit"

            if not indicator:
                continue

            dfp = os.path.join(DESTS[indicator], f)

            if not os.path.exists(dfp):
                if indicator == "unit":
                    auto_crop(sfp, dfp)
                else:
                    shutil.copy(sfp, dfp)

    # Artifacts
    path = os.path.join(src, "artifact")
    for root, _, files in os.walk(path):
        for f in files:
            sfp = os.path.join(root, f)
            dfp = os.path.join(DESTS["gear"], f)
            if not os.path.exists(dfp):
                shutil.copy(sfp, dfp)

    # Items
    path = os.path.join(src, "itemicon")
    for root, _, files in os.walk(path):
        for f in files:
            sfp = os.path.join(root, f)
            dfp = os.path.join(DESTS["item"], f)
            if not os.path.exists(dfp):
                shutil.copy(sfp, dfp)

    # Vision Cards
    path = os.path.join(src, "vision")
    for root, _, files in os.walk(path):
        for f in files:
            sfp = os.path.join(root, f)
            dfp = os.path.join(DESTS["vision icon" if f[-6:-3] == "_m." else "vision"], f)
            if not os.path.exists(dfp):
                shutil.copy(sfp, dfp)

def auto_crop(file_path, dst_path = None):
    # open an image file
    img = Image.open(file_path)

    left, upper = img.size
    right, lower = 0, 0

    alpha = img.getdata(3)
    pixels = [
        (x,y)
        for y in range(img.height)
        for x in range(img.width)
        if alpha[y*img.width + x] != 0
    ]
    left  = min(pixels, key=lambda x: x[0])[0]
    right = max(pixels, key=lambda x: x[0])[0]
    upper = min(pixels, key=lambda x: x[1])[1]
    lower = max(pixels, key=lambda x: x[1])[1]
    # crop the image
    img = img.crop(((left, upper, right, lower)))
    if dst_path:
        img.save(dst_path)
    return img

if __name__ == "__main__":
    main()