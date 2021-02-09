import re
import http.client
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import os
import zipfile
import io
import json
import os

reHost = re.compile(b"\x00(http[^\x00]+?)\x00")
reVersion = re.compile(b"\x00([^\x00]+?:googleplay)\x00")

def update_version(id, path = ""):
    # download & save latest apk from QooApp
    apk_buf =download_QooApp_apk(id)

    fp = os.path.join(path, id)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp,"wb") as f:
        f.write(apk_buf.read())
        apk_buf.seek(0)
    
    # extract the version
    z = zipfile.ZipFile(apk_buf)

    for f in z.namelist():
        if f[:16] == 'assets/bin/Data/':
            data = z.open(f).read()
            host = reHost.findall(data)
            version = reVersion.findall(data)

            if host and version:
                break
    
    HOST = host[0].decode("utf8")
    VERSION = version[0].decode("utf8")

    # save it
    fp = os.path.join(path, "version.json")
    with open(fp, "wt", encoding="utf8") as f:
        json.dump({"host":HOST, "version":VERSION}, f, ensure_ascii=False, indent="\t")

    return HOST, VERSION

def download_QooApp_apk(apk):
    query = urlencode({
        "supported_abis"	:	"x86,armeabi-v7a,armeabi",
        "device"	:	"beyond1q",
        "base_apk_version"	:	"0",
        "locale"	:	"en",
        "opengl"	:	"196609",
        "rooted"	:	"true",
        "screen"	:	"900,1600",
        "userId"	:	"58009610",
        "device_model"	:	"SM-G973N",
        "sdk_version"	:	"22",
        "base_apk_md5"	:	"null",
        "user_id"	:	"58009610",
        "version_code"	:	"317",
        "version_name"	:	"8.1.7",
        "os"	:	"android+5.1.1",
        "adid"	:	"64d6639f-55fe-4a86-86fa-a5ea31b2adc7",
        "type"	:	"app",
        "uuid"	:	"7e86a27e-db1c-4072-a5cc-e4b9b08e0672",
        "device_id"	:	"80e65e35094bedcc",
        "package_id"	:	"com.qooapp.qoohelper",
        "otome"	:	"0",
        "token"	:	"049b1432e342d571a01235ec1d6a91f61fc1db2e",
        "android_id"	:	"80e65e35094bedcc",
        "sa_distinct_id"	:	"80e65e35094bedcc",
        "patch_code"	:	"48",
        "density"	:	"320",
        "system_locale"	:	"en_DE",
    })
    res = urlopen(Request(
        url = f"https://api.qoo-app.com/v6/apps/{apk}/download?{query}",
        headers = {
            "accept-encoding": "gzip",
            "user-agent": "QooApp 8.1.7",
            "device-id": "80e65e35094bedcc"
        },
        method = "GET"
    ))
    # con = http.client.HTTPSConnection('api.qoo-app.com')
    # con.connect()
    # con.request("GET", f'/v6/apps/{apk}/download?supported_abis=x86,Carmeabi-v7a,Carmeab')
    # res = con.getresponse()
    # con.close()
    # download_url = res.headers['Location']
    data =  download_with_bar(res.url)
    return data

def download_with_bar(url):
    print(url)
    resp = urlopen(url)
    length = resp.getheader('content-length')
    if length:
        length = int(length)
        blocksize = max(4096, length // 100)
    else:
        blocksize = 1000000  # just made something up
    
    # print(length, blocksize)
    
    buf = io.BytesIO()
    size = 0
    while True:
        buf1 = resp.read(blocksize)
        if not buf1:
            break
        buf.write(buf1)
        size += len(buf1)
        if length:
            print(' {:.2f}\r'.format(size / length), end = '')
    print()
    buf.seek(0)
    return buf