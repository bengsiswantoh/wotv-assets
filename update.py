import os
import json
from lib import API, download_all, update_version

ROOT = os.path.dirname(os.path.realpath(__file__))

APK = {
	"global" : "com.square_enix.android_googleplay.WOTVffbeww",
	"japan"  : "com.square_enix.WOTVffbejp"
}

for ver in ["global", "japan"]:
	extract = os.path.join(ROOT, ver)
	assets  = extract+"_raw"

	os.makedirs(extract, exist_ok=True)
	os.makedirs(assets, exist_ok=True)

	try:
		with open(os.path.join(assets, "version.json"), "rt", encoding="utf8") as f:
			HOST, VERSION = list(json.load(f).values())

		environment = API(api = HOST.split('://',1)[1][:-1]).pass_enviroment(VERSION)
	except (KeyError, FileNotFoundError):
		HOST, VERSION = update_version(APK[ver], assets)
		environment = API(api = HOST.split('://',1)[1][:-1]).pass_enviroment(VERSION)

	download_all(environment, assets, extract)
