# moodlefuse - FUSE filesystem for Moodle
[![CodeFactor](https://www.codefactor.io/repository/github/matmasit/moodlefuse/badge/main)](https://www.codefactor.io/repository/github/matmasit/moodlefuse/overview/main)

This is a FUSE filesystem for Moodle. It allows you to mount your Moodle site as a filesystem and access your Moodle files as if they were local files.

It is a concept that has been around for a while, but I have not found any implementations that I could get to work, or that were not abandoned.
This is my attempt at creating one.

## Windows binary

You can easily grab a Windows binary in the _realeases_ section, it behaves as the program with all dependencies already resolved in a single file (thanks, pyinstaller), make sure to place the env file alongside it with the correct credentials.

</u>**You need to install [Winsfp](https://winfsp.dev/) to run the program on Windows.**</u>

## Installation

First, you need to create a `.env` file with the following variables:

```bash
SITE=https://moodle.example.com
MOODLE_USERNAME=yourusername
PASSWORD=yourpassword
MOUNT=/path/to/mountpoint
```

Then, just run the python script with the requirements installed. You can use a virtual environment if you want.

```bash
pip install -r requirements.txt
python moodlefuse.py
```

This works on Linux and Windows. I have not tested it on Mac OS, but it could work there too.

> Q: Why is _refuse_ in the project root?
> It's alpha software with some errors, I managed to make it fit for this project for now


### Requirements

* Python 3.6 or newer
* refuse - cross platform FUSE bindings
* requests - HTTP library for Python
* python-dotenv - Python library for reading .env files

### Features

* Read-only filesystem to read your Moodle files and announcements
* In-memory file caching mechanism
* Automatic html-to-markdown conversion for announcements

### Future enhancements
* Fix invisible top-level files
* Better memory handling (customizable), expecially for large files (chunking)
* Forum viewing support
* Persistent tree cache (currently it is built at every mount)
* Better error handling
* Better logging
* Better documentation


### Demo

![Demo](preview.gif)
