"""Builds and updates register file by scraping echo360 for lecture recordings."""

import json                     # parses syllabus json data
from lxml import html           # parses html
import re                       # string parsing

from .echo360login import Echo360login
from .data import Course, Lecture
from .register import Register

def start(arguments, options):
    # Module takes no options
    LectureSpider(arguments[0]).run()

class LectureSpider(Echo360login):
    def __init__(self, regname):
        super().__init__()
        self.regname = regname

    def run(self):
        if not self.login():
            return
        
        self.scrape_courselist()

        for indx, course in enumerate(Register(self.regname)):
            print("Scraping lectures for '{}'...".format(course.name))
            self.scrape_course_lectures(indx)

        Register(self.regname).docket()

    def scrape_courselist(self):
        """Scrapes links to all courses with available lectures."""

        def scrape_course_data():
            """Scrapes metadata for echo360 course."""
            # Get course name, year, and semesters
            title = row.xpath(".//div[@class='info-main']")[0]
            
            coursename = title.xpath("./h2/text()")[0]

            # Teaching period needs to be parsed i.e. "3720 - 2017 Semester 1"
            teachingperiod = title.xpath("./h3/text()")[0]
            groups = re.search(r"\d+ - (\d+) Semester (\d)", teachingperiod)
            courseyear = int(groups.group(1))
            coursesemester = int(groups.group(2))

            courseSyllabusLink = "https://echo360.org.au" + re.sub('home', 'syllabus', row.xpath("./div/a/@href")[0])

            # Create a Course object and write to file using Register class
            return Course(
                coursename,
                courseSyllabusLink,
                courseyear,
                coursesemester
            )

        print("Scraping course metadata...")

        # Request list of courses
        response = self.sesh.get("https://echo360.org.au/home")
        tree = html.fromstring(response.text)

        rows = tree.xpath(".//div[@class='home-content-main']/div")

        for row in rows:
            # Scrape course information into Course object
            course = scrape_course_data()

            with Register(self.regname) as reg:
                reg.appendIfMissing(course)

    def scrape_course_lectures(self, courseindx):
        """Downloads JSON structure containing lecture metadata and download links."""
        # Download JSON encoded syllabus for the course
        link = Register(self.regname)[courseindx].courselink
        response = self.sesh.get(link)
        
        syllabus_json = json.loads(response.text)

        for lect_syllabus in syllabus_json["data"]:
            try:
                start_time = lect_syllabus["lesson"]["lesson"]["timing"]["start"]
            except KeyError:
                # Lecture has no start date or time
                date = None
                time = None
            else:
                # Times looks like this (2017-07-24)T(16:12):00.000
                times = re.search(r'(\d+-\d{2}-\d{2})T(\d{2}:\d{2}):\d+.\d+', start_time)
                date = re.sub('-', '/', times.group(1))
                time = times.group(2)

            # Scrape download link for largest file size video
            try:
                links = lect_syllabus["lesson"]["video"]["media"]["media"]["current"]['primaryFiles']
            except KeyError:
                # Lecture has no video, skip
                continue

            size = 0
            for link in links:
                if link["size"] > size:
                    link["size"] = size
                    dllink = link["s3Url"]

            lect = Lecture(
                lect_syllabus["lesson"]["lesson"]["displayName"],
                date,
                time,
                dllink
            )

            with Register(self.regname) as reg:
                if lect not in reg[courseindx].lectures:
                    reg[courseindx].lectures.append(lect)


