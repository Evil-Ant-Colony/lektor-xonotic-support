# Copyright (c) 2018 Sebastian Schmidt
# MIT License (see License)

import os
from zipfile import ZipFile
import io
from PIL import Image
from lektor.pluginsystem import Plugin


def listpackages(folder):
    return list(filter(lambda f: f.endswith(".pk3") ,os.listdir(folder)))


class XonoticSupportPlugin(Plugin):
    name = 'Xonotic Support Plugin'
    description = 'Plugin to work with Xonotic packages'

    def on_setup_env(self, **extra):
        self.env.jinja_env.globals["get_mapinfo"] = self.get_mapinfo
        self.env.jinja_env.globals["get_pk3s"] = self.get_pk3s
        self.env.jinja_env.globals["get_content"] = self.get_content

    def get_mapinfo(self, mapname, pk3=None):
        info = {"name": mapname, "author": "", "description": "",
                "gametypes": []}
        if not pk3:
            pk3 = mapname + ".pk3"
        folder = self.get_pk3_folder()
        f = os.path.join(folder, pk3)
        if os.path.isfile(f):
            with ZipFile(f, "r") as zf:
                mapinfo_file = "maps/" + mapname + ".mapinfo"
                if mapinfo_file in zf.namelist():
                    mapinfo = zf.read(mapinfo_file).decode("utf-8")
                    for line in mapinfo.splitlines():
                        # strip comments
                        temp = line.split("//", 1)[0].strip()
                        if not temp:
                            continue
                        temp = temp.split(None, 1)
                        if len(temp) != 2:
                            continue
                        a, b = temp
                        if a.lower() == "title":
                            info["name"] = b
                        elif a.lower() == "author":
                            info["author"] = b
                        elif a.lower() == "description":
                            info["description"] = b
                        elif a.lower() == "gametype":
                            info["gametypes"].append(b)
        return info

    def get_pk3_folder(self):
        return self.get_config().get("xonotic-support.folder", None)

    def get_pk3s(self):
        folder = self.get_pk3_folder()
        if not folder:
            return []
        return listpackages(folder)

    def get_content(self, pk3):
        folder = self.get_pk3_folder()
        f = os.path.join(folder, pk3)
        if not os.path.isfile(f):
            return []
        with ZipFile(f, "r") as zf:
            return zf.namelist()

    def on_before_build_all(self, builder, **extra):
        if not self.get_config().get_bool("xonotic-support.extract-mapshots",
                                          False):
            return
        pk3_folder = self.get_pk3_folder()
        mapshot_dir = os.path.join(self.env.root_path, "assets", "images",
                                   "mapshots")
        os.makedirs(mapshot_dir, exist_ok=True)
        mapshots_to_clean = os.listdir(mapshot_dir)
        image_suffixes = ["jpeg", "jpg", "png", "tga"]
        for pk3 in self.get_pk3s():
            with ZipFile(os.path.join(pk3_folder, pk3), "r") as zf:
                for f in zf.namelist():
                    temp = f.split("/")
                    if len(temp) != 2:
                        continue
                    if temp[0] != "maps":
                        continue
                    if not any([temp[1].endswith(suffix) for suffix in
                                image_suffixes]):
                        continue
                    img_name = temp[1].rsplit(".", 1)[0] + ".jpg"
                    if img_name in mapshots_to_clean:
                        mapshots_to_clean.remove(img_name)
                        continue
                    out_name = os.path.join(mapshot_dir, img_name)
                    if os.path.isfile(out_name):
                        # the same mapshot can be in different pk3s
                        continue
                    src = io.BytesIO(zf.read(f))
                    try:
                        img = Image.open(src)
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                        img.save(os.path.join(mapshot_dir, img_name), "JPEG")
                    except Exception as e:
                        print("Error when extracting {}: {}".format(f, e))
        for f in mapshots_to_clean:
            os.remove(os.path.join(mapshot_dir, f))
