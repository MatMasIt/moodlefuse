import logging

from fuse import FUSE

from moodle import Moodle
from moodlefs import MoodleFS

# do something with the filesystem

if not hasattr(__builtins__, 'bytes'):
    bytes = str



import os
from dotenv import load_dotenv

load_dotenv()

SITE = os.getenv('SITE')
MOODLE_USERNAME = os.getenv('MOODLE_USERNAME')
PASSWORD = os.getenv('PASSWORD')
MOUNT = os.getenv('MOUNT')

print(SITE, MOODLE_USERNAME, PASSWORD, MOUNT)
m = Moodle(SITE, "mattia.mascarello", PASSWORD)
m.login()
print(m.get_user().__dict__)
"""
# print(m.get_category_by_id(402))

cont = m.get_course_content(2528)
for c in cont:
    print(c.name)
"""
logging.basicConfig(level=logging.DEBUG)
if __name__ == '__main__':
    FUSE(MoodleFS(m), "/home/mattia/moodle", foreground=True, allow_other=True)
