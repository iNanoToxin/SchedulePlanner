from ratemyprofessor.database import RateMyProfessor, Teacher
from util.namespace import namespace
from util.types import Json
from typing import Any

School_ID = "U2Nob29sLTk5OQ=="
RateMyProfessor_API = RateMyProfessor()




class Class:
    def __init__(self, _class: Json) -> None:
        self._info = namespace(_class)

    def __getattr__(self, key) -> Any:
        return self._info.__getattribute__(key)

    def get_teachers(self) -> list[Teacher]:
        teachers = []

        any()

        for teacher in self.faculty:
            for found_teacher in RateMyProfessor_API.get_teachers(teacher.displayName, School_ID):
                full_name = " ".join((found_teacher.first_name, found_teacher.last_name))
                if full_name == teacher.displayName:
                    teachers.append(found_teacher)
                    break
        return teachers




a = Class({
    "id": 4,
    "name": "MATH101",
})

print(a.id)