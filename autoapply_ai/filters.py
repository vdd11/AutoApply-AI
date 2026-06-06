from __future__ import annotations
import re
BLOCKED_COMPANY_PATTERNS = ['crypto casino','commission only','pyramid','mlm']

def parse_salary_floor(salary: str) -> int | None:
    if not salary: return None
    nums=[int(x.replace(',','')) for x in re.findall(r'\$?([0-9][0-9,]{3,})', salary)]
    return min(nums) if nums else None

def passes_user_filters(job: dict, *, remote_only=False, us_only=False, min_salary=0, employment_type='Any', blocked_companies=None, whitelisted_companies=None) -> tuple[bool, list[str]]:
    reasons=[]; text=f"{job.get('title','')} {job.get('company','')} {job.get('location','')} {job.get('description','')}".lower()
    blocked=[c.lower().strip() for c in (blocked_companies or []) if c]
    whitelist=[c.lower().strip() for c in (whitelisted_companies or []) if c]
    company=str(job.get('company','')).lower()
    if whitelist and not any(w in company for w in whitelist): reasons.append('Not in company whitelist')
    if blocked and any(b in company for b in blocked): reasons.append('Blocked company')
    if any(p in company or p in text for p in BLOCKED_COMPANY_PATTERNS): reasons.append('Low quality company/source pattern')
    if remote_only and 'remote' not in text: reasons.append('Not remote')
    if us_only and not any(x in text for x in ['united states','us only','u.s.','usa','remote, us','remote us']):
        if 'worldwide' not in text and 'remote' in text: reasons.append('US eligibility unclear')
    if employment_type and employment_type != 'Any' and employment_type.lower() not in text: reasons.append(f'Not {employment_type}')
    floor=parse_salary_floor(str(job.get('salary','')))
    if min_salary and floor and floor < min_salary: reasons.append('Below salary minimum')
    return (len(reasons)==0, reasons)
