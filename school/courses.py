from ratemyprofessor.database import RateMyProfessor, Teacher
from school.week_schedule import WeekSchedule, WeekTime, Day
from typing import List, Optional, Any
from pydantic import BaseModel, field_validator
from datetime import time


School_ID = "U2Nob29sLTk5OQ=="
RateMyProfessor_API = RateMyProfessor()


class MeetingTime(BaseModel):
    beginTime: Optional[time]
    building: Optional[str]
    buildingDescription: Optional[str]
    campus: Optional[str]
    campusDescription: Optional[str]
    category: str
    courseReferenceNumber: str
    creditHourSession: float
    endDate: str
    endTime: Optional[time]
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

    @field_validator("beginTime", "endTime", mode="before")
    def _parse_time(cls, _value: str):
        if _value is None:
            return _value
        elif isinstance(_value, str) and len(_value) == 4:
            return time(
                hour=int(_value[:2]),
                minute=int(_value[2:]),
            )
        raise ValueError("Invalid time format")


class Faculty(BaseModel):
    bannerId: str
    category: Optional[str]
    courseReferenceNumber: str
    displayName: str
    emailAddress: str
    primaryIndicator: bool
    term: str

    def get_name(self) -> str:
        return self.displayName


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
    feeAmount: Optional[str]

    def get_schedule(self) -> WeekSchedule:
        class_schedule = WeekSchedule()

        if self.instructionalMethod == "CLAS":
            for meeting in self.meetingsFaculty:
                for day in Day.names():
                    if getattr(meeting.meetingTime, day):
                        class_schedule.add_range(
                            WeekTime(
                                Day.by_name(day),
                                meeting.meetingTime.beginTime.hour,
                                meeting.meetingTime.beginTime.minute,
                            ),
                            WeekTime(
                                Day.by_name(day),
                                meeting.meetingTime.endTime.hour,
                                meeting.meetingTime.endTime.minute,
                            ),
                        )
        return class_schedule

    def overlaps(self, _other: "CourseSection") -> bool:
        return self.get_schedule().overlaps(_other.get_schedule())

    def get_teachers(self) -> List[Teacher]:
        return [
            teacher
            for faculty in self.faculty
            for teacher in RateMyProfessor_API.get_teachers(faculty.get_name().lower(), School_ID)
            if teacher.get_name().lower() == faculty.get_name().lower()
        ]
