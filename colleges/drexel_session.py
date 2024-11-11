from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from school.session import SchoolSession
from school.courses import CourseSection, Term
from functools import cache
from typing import List, Optional


class DUPage:
    pass


class DUSession(SchoolSession):
    @property
    def id(self) -> str:
        return "U2Nob29sLTE1MjE="

    def login(
        self,
        *,
        username: Optional[str] = None,
        password: Optional[str] = None,
        disable_gui: bool = False,
    ):
        raise NotImplementedError

    @cache
    def get_course_sections(self, _course: str, *, term: int) -> List[CourseSection]:
        raise NotImplementedError

    @cache
    def get_terms(self, *, max: int) -> List[Term]:
        raise NotImplementedError
