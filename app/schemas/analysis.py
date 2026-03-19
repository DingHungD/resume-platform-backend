from pydantic import BaseModel
from typing import List, Optional

class EducationItem(BaseModel):
    school: str
    degree: str
    date: str

class ExperienceItem(BaseModel):
    company: str
    position: str
    date: str
    achievements: List[str]

class ResumeAnalysisResult(BaseModel):
    name: str
    email: str
    phone: str
    education: List[EducationItem]
    experience: List[ExperienceItem]
    skills: List[str]
    summary: str