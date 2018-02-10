"""Defines lecture data structures."""

import json



def decode(dct):
    """Decodes an arbitrary JSON dictionary into a class."""
    def dec_lecture(dct):
        """Returns Lecture object from deserialized dictionary data."""
        return Lecture(dct['name'], dct['date'], dct['time'], dct['dllink'], dct['filename'])
    
    def dec_course(dct):
        """Returns Course oect from deserialized dictionary data."""
        return Course(dct['name'], dct['courselink'], dct['year'], dct['semester'], dct['lectures'])

    if 'date' in dct:
        return dec_lecture(dct)

    return dec_course(dct)

class Encoder(json.JSONEncoder):
    """Encodes classes into JSON compatible strings."""
    def default(self, o): # pylint: disable=E0202
        if isinstance(o, Lecture):
            return {
                "name": o.name,
                "date": o.date,
                "time": o.time,
                "dllink": o.dllink,
                "filename": o.filename,
            }
        elif isinstance(o, Course):
            return {
                "name": o.name,
                "courselink": o.courselink,
                "year": o.year,
                "semester": o.semester,
                "lectures": o.lectures,
            }

        # Else: Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, o)

class Lecture(object):
    """Defines 'Lecture' data class."""

    def __init__(self, name, date, time, dllink, filename=''):
        self.name = name
        self.date = date
        self.time = time
        self.dllink = dllink
        self.filename = filename


    def __repr__(self):
        return "<{0} object at {1}>".format(
            self.__class__.__name__,
            hex(id(self))
        )
    
    def __str__(self):
        return "{3} '{0}' at {1} on {2}".format(
            self.name,
            self.time,
            self.date,
            "Found" if self.filename else "Missing"
        )
    
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name and \
            self.date == other.date and \
            self.time == other.time
        return False

class Course(object):
    """Defines 'Course' data class."""

    def __init__(self, name="", courselink="", year="", semester=0, lectures=None):
        self.name = name
        self.courselink = courselink
        self.year = year
        self.semester = semester
        self.lectures = []

        if lectures:
            for lect in lectures:
                self.lectures.append(lect)

    def __repr__(self):
        return "<{0} object at {1}>".format(
            self.__class__.__name__,
            hex(id(self))
        )

    def __str__(self):
        return "'{0}', {1}.{2}, with {3} lectures".format(
            self.name,
            self.year,
            self.semester,
            len(self.lectures)
        )

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.name == other.name and \
            self.year == other.year and \
            self.semester == other.semester and \
            self.courselink == other.courselink
        return False
