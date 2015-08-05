import urllib.request, re
import subprocess
import sys, os, tempfile, logging
import urllib.request as urllib2
import urllib.parse as urlparse
import zipfile
import platform

surl = "https://builder.blender.org/download/"
burl = "https://builder.blender.org"

# USER CONFIG
# Change this paths if you want Blender in a different directory
mac_path = "/Applications/Blender"
linux_path = "/usr/local/Blender"
win_path = "C:\\Program Files\\Blender"

# Set the number accordingly to the distro you want to download: 1 for Blender, 2 for Goose, 3 for both
# This could be a prompt, if you want that replace the variable 'choice' with this 'input('1 for Blender, 2 for Goose, 3 for both and press Enter: ')'
choice = 1

# This will automatically set your platform
get_arch = [line for line in (platform.architecture())][0]
outpath = ''
lookfor = ''
arch = ''

# This will automatically set the variables according to your OS
# MAC
if platform.system() == 'Darwin' and get_arch == '32bit':
    outpath = mac_path
    lookfor = 'OSX'
    arch = 'i386'   
if platform.system() == 'Darwin' and get_arch == '64bit':
    outpath = mac_path
    lookfor = 'OSX'
    arch = 'x86_64'
# LINUX
elif platform.system() == 'Linux' and get_arch == '32bit':
    outpath = linux_path
    lookfor = 'linux'
    arch = 'i686'
elif platform.system() == 'Linux' and get_arch == '64bit':
    outpath = linux_path
    lookfor = 'linux'
    arch = 'x86_64'
# WINDOWS
elif platform.system() == 'Windows' and get_arch == '32bit':
    outpath = win_path
    lookfor = 'win32'
elif platform.system() == 'Windows' and get_arch == '64bit':
    outpath = win_path
    lookfor = 'win64'

# Change this for release type
only_base = "blender"
only_goose = "gooseberry"
both_releases = ""

releases = {1:'blender', 2:'gooseberry', 3:''}

def extract_file(filename):
    print("\nExtracting archive {0}\n\n".format(filename))
    fh = open(filename, 'rb')
    z = zipfile.ZipFile(fh)
    outpath = "C:\\Blender Foundation\\"
    for name in z.namelist():
        print("Extracting {0}".format(name))
        z.extract(name, outpath)

def download_file(url, desc=None):
    scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
    filename = os.path.basename(path)
    
    try:
        open(filename)
        print("Already got this one!\n")
        return False
    except FileNotFoundError:
        print("This is new. Let's rock!")

    try:
        u = urllib2.urlopen(url)
    except urllib.error.HTTPError as err:
        print("ERROR: Something is amiss and it is {0}. Aborting this file.\n".format(err))
        return False

    if not filename:
        filename = 'downloaded.file'
    if desc:
        filename = os.path.join(desc, filename)

    with open(filename, 'wb') as f:
        meta = u.info()
        meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
        meta_length = meta_func("Content-Length")
        file_size = None
        if meta_length:
            file_size = int(meta_length[0])
        print("Downloading: {0} Bytes: {1}".format(url, file_size))

        file_size_dl = 0
        block_sz = 8192 * 16
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break

            file_size_dl += len(buffer)
            f.write(buffer)

            status = "{0:16}".format(file_size_dl)
            if file_size:
                status += "   [{0:6.2f}%]\n".format(file_size_dl * 100 / file_size)
            status += chr(13)
            print(status, end="")
        print()

    # check for death in-flight

    # if filesize is OK
    if file_size == os.stat(filename).st_size:
       return filename
    else:
       print("Something broke, blatting and restarting...")
       os.remove(filename)
       # recursion!
       download_file(url)
       return False

matcher = re.compile("""<a[^>]* href="(.*?)">""")

print("Reading {0} for latest builds...\n".format(surl))

response = urllib.request.urlopen(surl)
data = response.read()
body = data.decode("utf-8")

downloadables = []

for line in body.split("\n"):
    if choice == 1:
        if lookfor in line and arch in line and not releases[2] in line:
            matchy = matcher.search(line)
            if matchy:
                downloadables.append(matchy.group(1))
    else:
        if lookfor in line and arch in line and releases[int(choice)] in line:
            matchy = matcher.search(line)
            if matchy:
                downloadables.append(matchy.group(1))

if len(downloadables) > 0:
    print("Found shinies : {0}\n".format(downloadables))

for durl in downloadables:
   print("Processing {0}\n".format(durl))
   if durl[0:1] == "/":
     print("Trying {0}".format(burl+durl))
     fn = download_file(burl+durl)
   else:
     print("Trying {0}".format(surl+durl))
     fn = download_file(surl+durl)
   if fn:
     extract_file(fn)

print("All finished! Blend on.\n")
subprocess.call('explorer "'+outpath+'"', shell=True)
