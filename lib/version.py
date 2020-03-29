import re
import http.client
import urllib.request
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
    con = http.client.HTTPSConnection('api.qoo-app.com')
    con.connect()
    con.request("GET", f'/v6/apps/{apk}/download')
    res = con.getresponse()
    con.close()
    download_url = res.headers['Location']
    data =  download_with_bar(download_url)
    return data

def download_with_bar(url):
    resp = urllib.request.urlopen(url)
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
            print(' {:.2f}\r{}'.format(size / length, url), end = '')
    print()
    buf.seek(0)
    return buf