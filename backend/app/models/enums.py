# app/models/enums.py
from enum import Enum

class SectionType(str, Enum):
    LECTURE = 'LECTURE'
    LAB = 'LAB'
    TUTORIAL = 'TUTORIAL'

class Term(str, Enum):
    FALL = 'FALL'
    WINTER = 'WINTER'

class BlockStatus(str, Enum):
    DRAFT = 'DRAFT'
    PUBLISHED = 'PUBLISHED'
    LOCKED = 'LOCKED'

class OfferingStatus(str, Enum):
    OPEN = 'OPEN'
    FULL = 'FULL'
    CANCELLED = 'CANCELLED'