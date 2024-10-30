from ratemyprofessor.database import RateMyProfessor, Teacher
from util.types import Json, TypedClass
from util.print import pprint
from typing import List, Optional, Any
import json


School_ID = "U2Nob29sLTk5OQ=="
RateMyProfessor_API = RateMyProfessor()


class MeetingTime(TypedClass):
    beginTime: str
    building: Optional[str]
    buildingDescription: Optional[str]
    campus: Optional[str]
    campusDescription: Optional[str]
    category: str
    courseReferenceNumber: str
    creditHourSession: float
    endDate: str
    endTime: str
    friday: bool
    hoursWeek: float
    meetingScheduleType: str
    meetingType: str
    meetingTypeDescription: str
    monday: bool
    room: Optional[str]
    saturday: bool
    startDate: str
    sunday: bool
    term: str
    thursday: bool
    tuesday: bool
    wednesday: bool


class Faculty(TypedClass):
    bannerId: str
    category: Optional[str]
    courseReferenceNumber: str
    displayName: str
    emailAddress: str
    primaryIndicator: bool
    term: str


class Meeting(TypedClass):
    category: str
    courseReferenceNumber: str
    faculty: List[Any]
    meetingTime: MeetingTime
    term: str


class Status(TypedClass):
    select: bool
    sectionOpen: bool
    timeConflict: bool
    restricted: bool
    sectionStatus: bool


class ReservedSeatSummary(TypedClass):
    courseReferenceNumber: str
    maximumEnrollmentReserved: int
    maximumEnrollmentUnreserved: int
    seatsAvailableReserved: int
    seatsAvailableUnreserved: int
    termCode: str
    waitAvailableReserved: int
    waitAvailableUnreserved: int
    waitCapacityReserved: int
    waitCapacityUnreserved: int


class Bookstore(TypedClass):
    url: str
    label: str


class CourseSection(TypedClass):
    id: int
    term: str
    termDesc: str
    courseReferenceNumber: str
    partOfTerm: str
    courseNumber: str
    subject: str
    subjectDescription: str
    sequenceNumber: str
    campusDescription: str
    scheduleTypeDescription: str
    courseTitle: str
    creditHours: Optional[float]
    maximumEnrollment: int
    enrollment: int
    seatsAvailable: int
    waitCapacity: int
    waitCount: int
    waitAvailable: int
    crossList: Optional[str]
    crossListCapacity: Optional[int]
    crossListCount: Optional[int]
    crossListAvailable: Optional[int]
    creditHourHigh: Optional[float]
    creditHourLow: int
    creditHourIndicator: Optional[str]
    openSection: bool
    linkIdentifier: Optional[str]
    isSectionLinked: bool
    subjectCourse: str
    faculty: List[Faculty]
    meetingsFaculty: List[Meeting]
    status: Status
    reservedSeatSummary: Optional[ReservedSeatSummary]
    sectionAttributes: List[Any]
    instructionalMethod: str
    instructionalMethodDescription: str
    bookstores: List[Bookstore]
    feeAmount: Optional[float]

    def get_teachers(self) -> list[Teacher]:
        def is_teacher(t: Teacher, f: Faculty):
            return f"{t.firstName} {t.lastName}" == f.displayName

        return [
            teacher
            for faculty in self.faculty
            for teacher in RateMyProfessor_API.get_teachers(faculty.displayName, School_ID)
            if is_teacher(teacher, faculty)
        ]


t = CourseSection({
    "id": 860006,
    "term": "202503",
    "termDesc": "2025 Spring",
    "courseReferenceNumber": "53096",
    "partOfTerm": "1",
    "courseNumber": "1068",
    "subject": "CIS",
    "subjectDescription": "Computer &amp; Information Science",
    "sequenceNumber": "007",
    "campusDescription": "Main",
    "scheduleTypeDescription": "Lecture and Lab",
    "courseTitle": "Program Design and Abstraction",
    "creditHours": None,
    "maximumEnrollment": 30,
    "enrollment": 4,
    "seatsAvailable": 26,
    "waitCapacity": 200,
    "waitCount": 0,
    "waitAvailable": 200,
    "crossList": "TV",
    "crossListCapacity": 300,
    "crossListCount": 40,
    "crossListAvailable": 260,
    "creditHourHigh": None,
    "creditHourLow": 4,
    "creditHourIndicator": None,
    "openSection": True,
    "linkIdentifier": None,
    "isSectionLinked": False,
    "subjectCourse": "CIS1068",
    "faculty": [
        Faculty({
            "bannerId": "175364",
            "category": None,
            "className": "",
            "courseReferenceNumber": "53096",
            "displayName": "John Fiore",
            "emailAddress": "jfiore@temple.edu",
            "primaryIndicator": True,
            "term": "202503",
        }),
    ],
    "meetingsFaculty": [
        Meeting({
            "category": "01",
            "className": "",
            "courseReferenceNumber": "53096",
            "faculty": [],
            "meetingTime": MeetingTime({
                "beginTime": "0930",
                "building": "SERC",
                "buildingDescription": "Science Ed and Research Ctr",
                "campus": "MN",
                "campusDescription": "Main",
                "category": "01",
                "courseReferenceNumber": "53096",
                "creditHourSession": 4.0,
                "endDate": "05/06/2025",
                "endTime": "1050",
                "friday": False,
                "hoursWeek": 2.66,
                "meetingScheduleType": "LL",
                "meetingType": "LEC",
                "meetingTypeDescription": "Lecture",
                "monday": False,
                "room": "110AB",
                "saturday": False,
                "startDate": "01/13/2025",
                "sunday": False,
                "term": "202503",
                "thursday": True,
                "tuesday": True,
                "wednesday": False,
            }),
            "term": "202503",
        }),
        Meeting({
            "category": "02",
            "className": "",
            "courseReferenceNumber": "53096",
            "faculty": [],
            "meetingTime": MeetingTime({
                "beginTime": "1100",
                "building": None,
                "buildingDescription": None,
                "campus": None,
                "campusDescription": None,
                "category": "02",
                "courseReferenceNumber": "53096",
                "creditHourSession": 0.0,
                "endDate": "05/06/2025",
                "endTime": "1250",
                "friday": True,
                "hoursWeek": 1.83,
                "meetingScheduleType": "LL",
                "meetingType": "LAB",
                "meetingTypeDescription": "Laboratory",
                "monday": False,
                "room": None,
                "saturday": False,
                "startDate": "01/13/2025",
                "sunday": False,
                "term": "202503",
                "thursday": False,
                "tuesday": False,
                "wednesday": False,
            }),
            "term": "202503",
        }),
    ],
    "status": Status({
        "select": False,
        "sectionOpen": True,
        "timeConflict": False,
        "restricted": False,
        "sectionStatus": True,
    }),
    "reservedSeatSummary": ReservedSeatSummary({
        "className": "",
        "courseReferenceNumber": "53096",
        "maximumEnrollmentReserved": 22,
        "maximumEnrollmentUnreserved": 8,
        "seatsAvailableReserved": 18,
        "seatsAvailableUnreserved": 8,
        "termCode": "202503",
        "waitAvailableReserved": 100,
        "waitAvailableUnreserved": 100,
        "waitCapacityReserved": 100,
        "waitCapacityUnreserved": 100,
    }),
    "sectionAttributes": [],
    "instructionalMethod": "CLAS",
    "instructionalMethodDescription": "Classroom In-Person",
    "bookstores": [
        Bookstore({
            "url": "https://www.bkstr.com/webApp/discoverView?bookstore_id-1=2360&amp;term_id-1=202503&amp;crn-1=53096",
            "label": "View Course Materials",
        }),
    ],
    "feeAmount": None,
})


pprint(t.get_teachers())
