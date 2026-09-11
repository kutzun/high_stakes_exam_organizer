# models.py
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Building:
    id: int
    name: str
    supervisor_id: Optional[int] = None

@dataclass
class Classroom:
    id: int
    building_id: int
    name: str           # e.g., "A101"
    capacity: int
    is_reserve: bool = False

@dataclass
class Proctor:
    id: int
    full_name: str
    department: str
    languages: List[str] = field(default_factory=list)
    preferred_building_id: Optional[int] = None
    can_be_supervisor: bool = True
    is_reserve: bool = False

@dataclass
class BuildingSupervisor:
    id: int
    full_name: str
    building_id: int
    proctor_id: Optional[int] = None   # if supervisor is also a proctor

@dataclass
class Student:
    id: int
    full_name: str
    faculty: str
    department: str
    exam_id: int   # which exam the student takes
    language: Optional[str] = None

@dataclass
class Exam:
    id: int
    name: str
    date: str
    time: str
    language: Optional[str] = None
    proctors_per_classroom_default: int = 2
    distribution_strategy: str = 'random'
    session_group: str = ''
    split_by_language: bool = False

@dataclass
class Assignment:
    id: int
    exam_id: int
    classroom_id: int
    proctor_ids: List[int] = field(default_factory=list)
    student_ids: List[int] = field(default_factory=list)
    is_reserve: bool = False
    building_supervisor_id: Optional[int] = None