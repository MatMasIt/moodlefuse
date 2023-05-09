import logging
import sys
from refuse.high import FUSE

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

m = Moodle(SITE, MOODLE_USERNAME, PASSWORD)
m.login()
#logging.basicConfig(level=logging.DEBUG)
if __name__ == '__main__':
    FUSE(MoodleFS(m), MOUNT, foreground=True, allow_other=True)
