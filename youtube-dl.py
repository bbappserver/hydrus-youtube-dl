#!/uer/bin/env python3
import sys
import os
import tempfile
import json
import shutil
import time
import signal
from subprocess import Popen
from hydrus import Client,ImportStatus

debug=False
tdir=None

def warn(message,timeout=10):
    signal.alarm(timeout)
    ok="y"
    try:
        ok=input(message)
    except:
        pass
    signal.alarm(0)
    if ok != "y":
        exit(-1)


def run():
    tdir=None
    try:
        key=None
        if 'HYDRUS_YTDL_KEY' in os.environ:
            key = os.environ['HYDRUS_YTDL_KEY']
        else:
            key=input("hydrus access key (set HYDRUS_YTDL_KEY to supress this)")
        
        c=Client(access_key=key)
        if c.get_url_files(args[-1]).status == ImportStatus.Importable:

            tdir = tempfile.mkdtemp()
            os.chdir(tdir)
            
            args.insert(0,shutil.which("youtube-dl"))
            if "--write-info-json" not in args:
                args.insert(1,"--write-info-json") #add info json flag just before url
            print(args)
            p=Popen(args)
            p.wait()
            status = p.returncode

            if status == 0:
                #success
                
                for f in os.listdir("."):
                    if not f.endswith(".json"):
                        p=os.path.abspath(f)
                        r = c.add_file(p)
                        fhash=r["hash"]
                        p = p.replace(r"\.[^\.]*$",".info.json")
                        info={}
                        try:
                            with open(p) as f:
                                info = json.load(f)
                            source=info["webpage_url"]
                            title=info["title"]
                            uploader=info["uploader"]
                            tags=info["tags"]
                            tags.append("title:"+title)
                            tags.append("creator:"+uploader)

                            if "uploader_id" in info:
                                tags.append("creator:"+info["uploader_id"])
                            
                            c.associate_url([fhash], [source], [])
                            c.add_tags([fhash], services_to_tags={"public tag repository" : tags})
                        except json.JSONDecodeError:
                            print("The info json youtube-dl provided was an invalid format")
                        except KeyError:
                            print("Youtube dl did ot supply one ore more necessary keys")
                        except Exception as e:
                            if not debug:
                                print("Downloaded but failed to sendto hydrus")
                else:
                    exit(status)
    finally:
        shutil.rmtree(tdir)

def cancel():
    exit(-1)       

args= sys.argv[1:]
signal.signal(signal.SIGALRM, cancel)
if "--download-archive" not in args:
    print("!!Warning!! youtube-dl cannot currently use hydrus to avoid downloading playlist items multiple times")
    print("Please supply a --download-archive as a work around.")
    warn("Continue (y/n)?  (Auto continue in 10 seconds)")
    run()