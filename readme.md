# War of the Visions ~ Assets

This git contains scripts to download and extract all assets of the game [War of the Visions](https:https://wotvffbe.com/) by gumi.


Small guide for people who don't know how to run Python scripts.

1. install [Python](https://www.python.org/downloads/) (version 3.6 and above)
2. install pip (option in the Python installer)
3. install the python module UnityPy (open a console (e.g. cmd) and enter ``pip install UnityPy==1.7.39``)
4. run update.py (downloads all missing or outdated assets and unpacs them)
5. to decrypt the encrypted data files run decrypt_all.py afterwards (``pip install pycryptodome`` is required)

PS:
If you're upgrading your scripts from an older version,
you have to delete ``/{version}_raw/version.json`` and update your UnityPy ``pip install -U UnityPy``
