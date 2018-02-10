"""Defines register class for r/w to register file, and queries a given register.
    Options:
          : default counts the number of courses left to download
        -d: prints [d]ocket, a list of the courses on file
        -m: prints docket with [m]issing lectures for each course
        -f: prints [f]ull list of courses and lectures"""

import json

from .data import decode
from .data import Encoder

def start(arguments, options):
    """Interrogates a given register."""
    regname = arguments[0]
    r = Register(regname)
    
    if "d" in options:
        # Print [d]ocket
        if r.exists:
            r.docket()
    elif "m" in options:
        # Print docket with only [m]issing lectures
        if r.exists:
            r.docket(True, True)
    elif "f" in options:
        # Print [f]ull docket
        if r.exists:
            r.docket(True)
    else:
        # Count number of lectures to download
        if r.exists:
            total, missing = r.tally()
            if missing != 0:
                print("{0} lectures left to download from a total of {1}".format(missing, total))
            else:
                print("All {0} lectures downloaded.".format(total))

class Register(list):
    """List of Course objects, with functionality for r/w to file.
    
        usage:
            # Using 'with' syntax - changes are saved.
            with Register("name.json") as reg
                c = Course(
                    "Apple Bobbing 101",
                    "www.university.com",
                    2017, 2, []
                )
                # Make permanent changes to 'reg' and 'name.json'
                reg.append(c)

            # Using 'constructor' - changes aren't saved!
            reg = Register("name.json")
            c = Course(
                "Apple Bobbing 101",
                "www.abfb.com",
                2017, 2, []
            )
            # Make temporary changes to 'reg'
            reg.append(c)"""

    def __init__(self, name=None):
        # print("\tiniting...")

        self.filename = name

        if name:
            # If passed a filename
            try:
                # If file exists, read it.
                data = self._read()
            except FileNotFoundError:
                # File doesn't exist, init with empty data.
                print("'{}' not found.".format(self.filename))
                self.exists = False
                data = []
            else:
                self.exists = True
        else:
            # No filename passed, init with empty data.
            data = []

        super().__init__(data)

    # ---- Quality-of-Life functions ----

    def appendIfMissing(self, course):
        """Adds course to list if it doesn't already exist, else does nothing."""

        # Count number of courses in register that match the current course
        # Should only be 0 or 1
        exists = self.count(course) > 0

        # If course isn't already in register
        if not exists:
            self.append(course)

    def docket(self, listLectures=False, onlyMissing=False):
        print("Register '{}':".format(self.filename))
        for indx, course in enumerate(self):
            # Print course info
            print("  {0} - {1}.".format(indx, course))
            if len(course.lectures) > 0 and listLectures:
                # also print lectures
                for lect in course.lectures:
                    if not lect.filename or not onlyMissing:
                        print('\t'+str(lect))

    def tally(self):
        """Tallys number of lectures and how many are left to download.
            returns: (total, missing)"""
        missing = 0
        total = 0
        for course in self:
            for lecture in course.lectures:
                if lecture.dllink:
                    # If the lecture has a valid download link add to total
                    total = total + 1

                    if not lecture.filename:
                        # If the lecture isn't on file
                        missing = missing + 1
                
        return (total, missing)


    # NOTE: When called using 'with' keyword, register state is written to file.
    #       This is implemented using '__enter__' and '__exit__' functions,
    #       which are called using the 'with' keyword.

    def __enter__(self):
        # print("\tentering...")
        # When entering, check if filename is valid
        if not self.filename:
            # No valid filename, raise exception
            raise Exception("Can't write to file without valid filename.")

        # Filename is valid
        if not self.exists:
            # File doesn't exist on disk yet, so create it.
            print("Creating new register '{}'.".format(self.filename))
            self._write()
            self.exists = True

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # print("\texiting...")
        # When exiting, write register to file
        self._write()

    # NOTE: '_read', and '_write', implement the loading and saving to file.
    #       These private methods should never be called explicitly from external code.

    def _read(self):
        """Loads register from file."""
        # print("\t  read from '" + self.filename + "'")
        with open(self.filename) as regfile:
            decoded_json = json.load(regfile, object_hook=decode)
            if not isinstance(decoded_json, list):
                return [decoded_json]

            return decoded_json

    def _write(self):
        """Writes register to file."""
        # print("\t  write to '" + self.filename + "'")
        with open(self.filename, 'w') as regfile:
            json.dump(self, regfile, cls=Encoder)
