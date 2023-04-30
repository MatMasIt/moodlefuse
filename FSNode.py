import stat
import sys
import time

import requests
from markdownify import markdownify as md

from moodle import Category, Course, Moodle, Section, Folder, File, Label, Url

fileCache = {}

# Virtual Filesystem node
class FSNode:
    def __init__(self, name: str, is_dir=True):
        self.name = name
        self.children = []
        self.is_dir = is_dir
        self.size = 0
        self.url = None

    def to_stat_struct(self):
        if self.is_dir:
            return dict(
                st_mode=(stat.S_IFDIR | 0o755),
                st_ctime=time.time(),
                st_mtime=time.time(),
                st_atime=time.time(),
                st_nlink=2,

            )
        else:
            return dict(
                st_mode=(stat.S_IFREG | 0o755),
                st_ctime=time.time(),
                st_mtime=time.time(),
                st_atime=time.time(),
                st_nlink=2,
                st_size=self.size
            )

    def resolve_path(self, path: str):
        if path == "/":
            return self
        path_el = path.split("/")[1:]
        return self._recurse_path_traverse(path_el)

    def _recurse_path_traverse(self, path_arr: list[str]):
        if len(path_arr) == 0:
            return self
        for child in self.children:
            if child.name == path_arr[0]:
                return child._recurse_path_traverse(path_arr[1:])
        return None

    @staticmethod
    def from_category(c: Category, m: Moodle):
        f = FSNode(c.name, True)
        for course in c.courses:
            f.children.append(FSNode.from_course(course, m))
        return f

    @staticmethod
    def from_course(c: Course, m: Moodle):
        f = FSNode(c.shortname, True)
        for s in m.get_course_content(c.id):
            f.children.append(FSNode.from_section(s, m))
        return f

    @staticmethod
    def from_section(s: Section, m: Moodle):
        f = FSNode(s.name, True)
        for mo in s.modules:
            f.children.append(FSNode.from_module(mo, m))
        if len(s.htmlcontent):
            m = FSNode("README.md", False)
            m.size = len(s.htmlcontent)
            m.url = "html#" + s.htmlcontent
            f.children.append(m)
        return f

    @staticmethod
    def from_module(mo, m: Moodle):
        if isinstance(mo, Folder):
            f = FSNode(mo.name, True)
            for el in mo.files:
                r = FSNode.from_module(el, m)
                if r is not None:
                    f.children.append(r)
            return f
        elif isinstance(mo, File):
            return FSNode.from_file(mo, m)
        elif isinstance(mo, Label):
            return FSNode.from_label(mo, m)
        elif isinstance(mo, Url):
            return FSNode.from_url(mo, m)
        return None

    @staticmethod
    def from_file(el: File, m: Moodle):
        f = FSNode(el.name, False)
        f.size = el.filesize
        f.url = el.fileurl
        return f

    def read(self, size, offset, mo: Moodle):
        global fileCache
        if sys.getsizeof(fileCache) > 3 * 100000000 and len(fileCache) > 2:
            d = {k: v for k, v in sorted(fileCache.items(), key=lambda item: item["datetime"])}
            for k in list(d.keys())[:len(d) // 2]:
                del fileCache[k]
            del d
        if self.url not in fileCache.keys():
            if self.url.startswith("html#"):
                fileCache[self.url] = {"datetime": time.time(), "content": md(self.url[5:]).encode()}
            elif self.url.startswith("url#"):
                fileCache[self.url] = {"datetime": time.time(), "content": self.url[4:].encode()}
            else:
                r = requests.get(self.url + "&token=" + mo.token)
                fileCache[self.url] = {"datetime": time.time(), "content": r.content}
        return fileCache[self.url]["content"][offset:offset + size]

    @staticmethod
    def from_moodle(moodle: Moodle):
        f = FSNode("/", True)
        for cat in moodle.get_enrolled_categories():
            f.children.append(FSNode.from_category(cat, moodle))
        return f

    @staticmethod
    def from_label(mo: Label, m):
        f = FSNode(mo.name, False)
        f.size = len(mo.htmlcontent)
        f.url = "html#" + mo.htmlcontent
        return f

    @staticmethod
    def from_url(mo: Url, m):
        f = FSNode(mo.name, False)
        f.size = len(mo.url)
        f.url = "url#" + mo.url
        return f
