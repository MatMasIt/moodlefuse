import re

import requests

# a minimalistic moodle api wrapper, just for the purpose of this project
# it's not meant to be complete
# it's not meant to be efficient
# it's not meant to be pythonic
# it's not meant to be a good moodle api wrapper


class Category:
    def __init__(self, id_i: int, name: str, courses: list):
        self.id = id_i
        self.name = name
        self.courses = courses


class Course:
    def __init__(self, id_i: int, shortname: str, fullname: str, enrolled_user_count: int):
        self.shortname = shortname
        self.fullname = fullname
        self.id = id_i
        self.enrolled_user_count = enrolled_user_count


class Section:
    def __init__(self, id_i: int, name: str, htmlcontent: str, modules: list):
        self.id = id_i
        self.autoName = False
        if len(re.sub(r'\W+', '', name)) == 0:
            name = "Section " + str(id_i)
            self.autoName = True
        self.name = name
        self.htmlcontent = htmlcontent
        self.modules = modules


class Label:
    def __init__(self, id_i: int, htmlcontent: str):
        self.id = id_i
        self.htmlcontent = htmlcontent
        self.name = "Label" + str(id_i)


class Url:
    def __init__(self, id_i: int, name: str, description: str, url: str):
        self.id = id_i
        self.name = name
        self.description = description
        self.url = url


class MoodleUser:
    def __init__(self, username: str, fullname: str, user_picture_url: str):
        self.username = username
        self.fullname = fullname
        self.user_picture_url = user_picture_url


class Folder:
    def __init__(self, id_i: int, name: str, files: list):
        self.id = id_i
        self.name = name
        self.files = files


class File:
    def __init__(self, filename: str, filesize: int, fileurl: str):
        self.filename = filename
        self.name = filename
        self.filesize = filesize
        self.fileurl = fileurl


class Moodle:
    def __init__(self, site_url, username, password):
        self.user_id = None
        self.token = None
        self.private_token = None
        self.site_url = site_url
        self.username = username
        self.password = password

    def login(self) -> None:
        url = self.site_url + "/login/token.php?username=" + self.username + "&password=" + self.password + "&service=moodle_mobile_app"
        response = requests.post(url)
        r = response.json()
        if "error" in r.keys():
            raise Exception(r["error"])
        self.token = r["token"]
        self.private_token = r["privatetoken"]
        self.get_user()

    def get_user(self) -> MoodleUser:
        url = self.site_url + "/webservice/rest/server.php?moodlewsrestformat=json"
        re = requests.post(url, data={"wstoken": self.token, "wsfunction": "core_webservice_get_site_info"})
        r = re.json()
        self.user_id = r["userid"]
        self.userpictureurl = r["userpictureurl"]
        self.fullname = r["fullname"]
        return MoodleUser(self.username, self.fullname, self.userpictureurl)

    def get_enrolled_categories(self) -> list[Category]:
        url = self.site_url + "/webservice/rest/server.php?moodlewsrestformat=json"
        re = requests.post(url, data={"wstoken": self.token, "wsfunction": "core_enrol_get_users_courses",
                                      "userid": self.user_id})
        r = re.json()
        categories = {}
        for course in r:
            if course["category"] not in categories.keys():
                categories[course["category"]] = []
            categories[course["category"]].append(
                Course(course["id"], course["shortname"], course["fullname"], course["enrolledusercount"]))
        lret = []
        for category_id in categories.keys():
            c = self.get_category_by_id(category_id)
            c.courses = categories[category_id]
            lret.append(c)
        return lret

    def get_enrolled_courses(self) -> Category:
        url = self.site_url + "/webservice/rest/server.php?moodlewsrestformat=json"
        re = requests.post(url, data={"wstoken": self.token, "wsfunction": "core_enrol_get_users_courses",
                                      "userid": self.user_id})
        return re.json()

    def get_category_by_id(self, category_id: int) -> Category:
        url = self.site_url + "/webservice/rest/server.php?moodlewsrestformat=json"
        re = requests.post(url, data={"wstoken": self.token, "wsfunction": "core_course_get_categories",
                                      "criteria[0][key]": "id", "criteria[0][value]": category_id})
        r = re.json()
        return Category(r[0]["id"], r[0]["name"], [])

    def get_course_content(self, course_id: int) -> list[Section]:
        url = self.site_url + "/webservice/rest/server.php?moodlewsrestformat=json"
        re = requests.post(url, data={"wstoken": self.token, "wsfunction": "core_course_get_contents",
                                      "courseid": course_id})
        r = re.json()
        sections = []
        for section in r:
            modules = []
            for module in section["modules"]:
                if module["modname"] == "label":
                    modules.append(Label(module["id"], module["description"]))
                elif module["modname"] == "url":
                    modules.append(Url(module["id"], module["name"],
                                       (module["description"] if "description" in module.keys() else ""),
                                       module["url"]))
                elif module["modname"] == "folder":
                    modules.append(self.__folder_rec_exploder(module))
                elif module["modname"] == "file":
                    modules.append(File(module["fileurl"], module["filename"], module["filesize"], module["fileurl"]))

            sections.append(Section(section["id"], section["name"], section["summary"], modules))
        return sections

    def __folder_rec_exploder(self, folder_module: dict) -> Folder:
        f = Folder(folder_module["id"], folder_module["name"], [])
        for file in folder_module["contents"]:
            if file["type"] == "file":
                f.files.append(File(file["filename"], file["filesize"], file["fileurl"]))
            else:
                f.files.append(self.__folder_rec_exploder(file))
        return f
