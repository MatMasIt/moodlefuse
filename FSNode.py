import stat
import sys
import time

import requests
from markdownify import markdownify as md

from moodle import Category, Course, Moodle, Section, Folder, File, Label, Url

import unicodedata
import re


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    s = value.rsplit(".", 1)  # split into name and extension
    ext = ""
    if len(s) == 2:
        value = s[0]
        ext = "." + slugify(s[1])
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    res = re.sub(r'[-\s]+', '-', value).strip('-_')
    file = res + ext
    return file


class LinkTo:
    pass


class UrlLink(LinkTo):
    def __init__(self, url: str):
        self.url = url


class FileLink(LinkTo):
    def __init__(self, url: str):
        self.url = url


class HTMLContentMap(LinkTo):
    def __init__(self):
        self.htmlMap = {}

    def add(self, html: str, label_id: int):
        self.htmlMap[label_id] = md(html)

    def sort(self):
        self.htmlMap = dict(sorted(self.htmlMap.items()))

    def markdown_make(self) -> str:
        return "\n".join([self.htmlMap[key] for key in self.htmlMap])


fileCache = {}


# Virtual Filesystem node
class FSNode:
    def __init__(self, name: str, parent, is_dir=True):
        self.name = slugify(name)
        self.parent = parent
        self.children = []
        self.is_dir = is_dir
        self.size = 0
        self.linkTo = None

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

    def find_child_by_name(self, name: str):
        for el in self.children:
            if el.name == name:
                return el
        return None

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
    def from_category(c: Category, parent, m: Moodle):
        f = FSNode(c.name, parent, True)
        for course in c.courses:
            f.children.append(FSNode.from_course(course, f, m))
        return f

    @staticmethod
    def from_course(c: Course, parent, m: Moodle):
        f = FSNode(c.shortname, parent, True)
        for s in m.get_course_content(c.id):
            f.children.append(FSNode.from_section(s, f, m))
        return f

    @staticmethod
    def from_section(s: Section, parent, m: Moodle):
        f = FSNode(s.name, parent, True)
        if len(s.htmlcontent):
            m = FSNode("README.md", f, False)
            m.linkTo = HTMLContentMap()
            m.linkTo.add(s.htmlcontent, s.id)
            m.size = len(m.linkTo.markdown_make())
            f.children.append(m)
        for mo in s.modules:
            el = FSNode.from_module(mo, f, m)
            if el is not None:
                f.children.append(el)
        if s.autoName: # Heuristic name generation
            q = f.find_child_by_name(slugify("README.md"))
            if q is not None:
                md = q.linkTo.markdown_make()
                lines = md.split("\n")
                line = lines[0]
                i = 1
                while not len(re.sub(r'\W+', '', line)) and i < len(lines):
                    line = lines[i]
                    i += 1
                if i != len(lines):
                    title = slugify(line)
                    # truncate title to 30 chars
                    title = title[:30]
                    f.name = title
        return f

    @staticmethod
    def from_module(mo, parent, m: Moodle):
        if isinstance(mo, Folder):
            f = FSNode(mo.name, parent, True)
            for el in mo.files:
                r = FSNode.from_module(el, f, m)
                if r is not None:
                    f.children.append(r)
            return f
        elif isinstance(mo, File):
            return FSNode.from_file(mo, parent, m)
        elif isinstance(mo, Label):
            FSNode.from_label(mo, parent, m)
        elif isinstance(mo, Url):
            return FSNode.from_url(mo, parent, m)
        return None

    @staticmethod
    def from_file(el: File, parent, m: Moodle):
        f = FSNode(el.name, parent, False)
        f.size = el.filesize
        f.linkTo = FileLink(el.fileurl)
        return f

    @staticmethod
    def hash_link_to(a: LinkTo):
        if isinstance(a, UrlLink):
            return "url#" + a.url
        elif isinstance(a, FileLink):
            return a.url
        elif isinstance(a, HTMLContentMap):
            return "html#" + str(a.htmlMap.keys())
        return None

    def read(self, size, offset, mo: Moodle):
        global fileCache
        if sys.getsizeof(fileCache) > 3 * 100000000 and len(fileCache) > 2:
            d = {k: v for k, v in sorted(fileCache.items(), key=lambda item: item["datetime"])}
            for k in list(d.keys())[:len(d) // 2]:
                del fileCache[k]
            del d
        link_hash = FSNode.hash_link_to(self.linkTo)
        if link_hash not in fileCache.keys():
            if isinstance(self.linkTo, HTMLContentMap):
                fileCache[self.linkTo] = {"datetime": time.time(), "content": self.linkTo.markdown_make().encode()}
            elif isinstance(self.linkTo, UrlLink):
                fileCache[self.linkTo] = {"datetime": time.time(), "content": self.linkTo.url.encode()}
            elif isinstance(self.linkTo, FileLink):
                r = requests.get(self.linkTo.url + "&token=" + mo.token)
                fileCache[self.linkTo] = {"datetime": time.time(), "content": r.content}
        return fileCache[self.linkTo]["content"][offset:offset + size]

    @staticmethod
    def from_moodle(moodle: Moodle):
        f = FSNode("/", None, True)
        for cat in moodle.get_enrolled_categories():
            f.children.append(FSNode.from_category(cat, f, moodle))
        return f

    @staticmethod
    def from_label(mo: Label, parent, m) -> None:
        f = parent.find_child_by_name(slugify("README.md"))
        if f is not None:
            f.linkTo.add(mo.htmlcontent, mo.id)
        else:
            f = FSNode(slugify("README.md"), parent, False)
            f.linkTo = HTMLContentMap()
            f.linkTo.add(mo.htmlcontent, mo.id)
            f.size = len(f.linkTo.markdown_make())
            parent.children.append(f)
        return None

    @staticmethod
    def from_url(mo: Url, parent, m):
        f = FSNode(mo.name, parent, False)
        f.size = len(mo.url)
        f.linkTo = UrlLink(mo.url)
        return f
