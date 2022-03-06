import os
from lib import encryption_helper, load_version_consts

encrypted_dirs = [
    ["map", "collabo", "set", "encrypted"],
    ["map", "lapis", "set", "encrypted"],
    ["param", "ai", "encrypted"],
    ["param", "task", "encrypted"],
    ["param", "masterparam", "sheet"]
]

ROOT = os.path.dirname(os.path.realpath(__file__))
for version in ["global", "japan", "china"]:
    print(f"{version}")
    _,_, encryption_helper.a_shared_key = load_version_consts(os.path.join(ROOT, f"{version}_raw"))
    for dir_name in encrypted_dirs:
        dir_path = os.path.join(ROOT, version, *dir_name)
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)

                with open(file_path, "rt", encoding="utf8") as f:
                    text = f.read().strip()
                try:
                    text = encryption_helper.deserialize_fromBase64_string(text, file[:-4])
                except Exception as e:
                    print(f"{file_path} -> {e}")
                    continue
                
                if "encrypted" in dir_name:
                    new_file_path = file_path.replace("encrypted", "decrypted")
                else: #masterparam sheet
                    new_file_path = file_path.replace("sheet", "sheet_decrypted")
                
                os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
                with open(new_file_path, "wb") as f:
                    f.write(text)
                # print(new_file_path)