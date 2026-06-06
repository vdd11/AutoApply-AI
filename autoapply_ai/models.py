from dataclasses import dataclass, asdict
@dataclass
class ResumeProfile:
    session_id: str
    name: str = "Candidate"
    email: str = ""
    raw_text: str = ""
    skills: str = ""
    target_roles: str = "Data Analyst, Data Scientist, Business Intelligence Analyst, Research Analyst"
    preferred_location: str = "Remote"
    seniority: str = "Entry-Level / Junior"
    def to_dict(self): return asdict(self)
@dataclass
class Job:
    source_job_id: str
    title: str
    company: str
    location: str
    source: str
    url: str
    description: str
    employment_type: str = ""
    salary: str = ""
    date_posted: str = ""
