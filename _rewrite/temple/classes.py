from ratemyprofessor.database import RateMyProfessor, Teacher
from typing import List, Optional, Any
from pydantic import BaseModel


School_ID = "U2Nob29sLTk5OQ=="
RateMyProfessor_API = RateMyProfessor()


class MeetingTime(BaseModel):
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


class Faculty(BaseModel):
    bannerId: str
    category: Optional[str]
    courseReferenceNumber: str
    displayName: str
    emailAddress: str
    primaryIndicator: bool
    term: str


class Meeting(BaseModel):
    category: str
    courseReferenceNumber: str
    faculty: List[Any]
    meetingTime: MeetingTime
    term: str


class Status(BaseModel):
    select: bool
    sectionOpen: bool
    timeConflict: bool
    restricted: bool
    sectionStatus: bool


class ReservedSeatSummary(BaseModel):
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


class Bookstore(BaseModel):
    url: str
    label: str


class CourseSection(BaseModel):
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

    def get_teachers(self) -> List[Teacher]:
        return [
            teacher
            for faculty in self.faculty
            for teacher in RateMyProfessor_API.get_teachers(faculty.displayName, School_ID)
            if teacher.get_name() == faculty.displayName
        ]
