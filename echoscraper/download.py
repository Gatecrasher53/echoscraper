"""Uses register file to download missing recordings.
    Options:
        -y: Automatically selects [y]es to begin downloading without prompt after login
        -c: Allows user to [c]hoose what courses to download"""

import re       # Parses lots of strings
import signal   # Captures SIGINT
import sys      # Exits program after capturing SIGINT twice
import os       # Creates directory to store downloaded lectures

import requests.exceptions as rEx   # Import request exceptions to catch disconnects
from clint.textui import progress   # Used for dynamic progress bars
from datetime import datetime       # Logs time of downloader crash

from.echo360login import Echo360login   # Logs into echo360
from .register import Register          # R/Ws to Register file

def start(arguments, options):
    """Begins downloader"""
    LectureDownloader(arguments[0]).run(options)

class LectureDownloader(Echo360login):
    def __init__(self, regname):
        super().__init__()
        self.regname = regname
        self.numDownloaded = 0
        self.__HALT = False
        signal.signal(signal.SIGINT, self.interrupt_handler)

    def run(self, options):
        coursesToDownload = self.listCoursesToDownload(options)
        
        # Login to echo360
        if not self.login():
            return

        if 'y' not in options:
            # Ask before continuing
            begin = input('Begin downloading? (y/n): ')
            begin = begin.lower()

            if begin != 'y':
                return

        # Else begin downloading
        for indx, course in enumerate(Register(self.regname)):
            if self.__HALT:
                break
            elif indx not in coursesToDownload:
                continue

            print("Downloading '{}'".format(course.name))
            self.downloadCourseLectures(indx)
    
        print("{0} lecture{1} downloaded.".format(
            self.numDownloaded, 's' if self.numDownloaded != 1 else '')
        )

    def listCoursesToDownload(self, options):
        if 'c' in options:
            # Ask user to choose what courses to download
            return self.chooseCoursesToDownload()

        return list(range(len(Register(self.regname))))

    def chooseCoursesToDownload(self):
        """Lets user choose what courses to download."""
        Register(self.regname).docket()
        print("\nWhat numbered courses would you like to download?")
        courseNums = []

        while(True):
            num = input()
            try:
                num = int(num)
            except ValueError:
                break

            if num >= 0 and num < len(Register(self.regname)):
                if num not in courseNums:
                    courseNums.append(num)
                else:
                    print("'{}' will already be downloaded.".format(Register(self.regname)[num].name))
            else:
                break

        return courseNums

    def downloadCourseLectures(self, courseindx):
        """Downloads all remaining lectures for a given course."""
        for lectureIndx, lecture in enumerate(Register(self.regname)[courseindx].lectures):
            # If downloads haven't been halted
            if self.__HALT:
                break
            # If lecture hasn't been downloaded yet and has a download link.                
            elif lecture.dllink and not lecture.filename:
                print("Downloading... {}".format(lecture))
                filepath = self.downloadLecture(courseindx, lectureIndx)

                if filepath:
                    # Download completed succesfully, write filepath to register                    
                    with Register(self.regname) as reg:
                        reg[courseindx].lectures[lectureIndx].filename = filepath
                    
                    # Add number of lectures downloaded to total for this session
                    self.numDownloaded = self.numDownloaded + 1

    def downloadLecture(self, cIndx, lIndx):
        """Downloads a specific lecture from a given course."""
        # Read course and lecture metadata from register
        course = Register(self.regname)[cIndx]
        lecture = course.lectures[lIndx]

        # Create lecture path and filename
        path, filename = self.directory(course, lecture)
        filepath = path + '/' + filename

        # Create directory from path if it doesn't already exist
        if not os.path.exists(path):
            os.makedirs(path)

        # Start streaming data
        # stream=True parameter ensures page is streamed to reduce memory usage
        resp = self.sesh.get(lecture.dllink, stream=True)

        # Get total file size for loading bar
        total_size = int(resp.headers.get('content-length', 0))

        # Create and write to file
        with open(filepath, 'wb') as fd:
            try:
                for chunk in progress.bar(
                        resp.iter_content(chunk_size=1024), expected_size=(total_size/1024) + 1):
                    if chunk: # filter out keep-alive new chunks
                        fd.write(chunk)
            except  rEx.ChunkedEncodingError:
                # Raised an error during download, probably 104
                # Download was not complete
                print('Download Error at %s' %datetime.now().time())
                print('Halting.')
                self.__HALT = True
                return ''

        return filepath

    @staticmethod
    def directory(course, lecture):
        """Returns lecture filepath as tuple: (path, filename)."""

        def sanitizeFileName(string):
            """Removes a bunch of crud from course names."""
            return re.sub(r" ?[^a-zA-Z0-9\(\) &_-]", '', string)
        
        def sanitizeCourseName(course):
            s = re.sub(r" ?UG & PG| ?Combined| ?\(.*\)", '', course.name)
            return sanitizeFileName(s)

        def sanitizeLectureName(lecture):
            """Constructs unique filename from lecture metadata."""
            d = re.sub('/', '', lecture.date) if lecture.date else ''
            t = re.sub(':', '', lecture.time) if lecture.time else ''
            return "{0}-{1} {2}".format(d, t, sanitizeFileName(lecture.name))

        path = ['lectures']

        path.append(str(course.year))
        path.append("semester{}".format(course.semester))
        path.append(sanitizeCourseName(course))

        return ('/'.join(path), sanitizeLectureName(lecture))

    def interrupt_handler(self, *args):
        """Captures SIGINT signal to terminate downloader inbetween downloads gracefully."""
        if not self.__HALT:
            # ^C pressed once
            self.__HALT = True
            print("\nHalting. Program will terminate after current download finishes.")
            print("Press ^C again to force quit - This may corrupt any currently open files!")
        else:
            # ^C pressed twice, force quitting
            print("\nQuitting...")
            sys.exit(1)
