from __future__ import annotations
import re
SECTION_NAMES=['summary','education','experience','projects','skills','certifications','publications']

def extract_sections(text: str) -> dict[str,str]:
    text=text or ''
    matches=[]
    for name in SECTION_NAMES:
        for m in re.finditer(rf'(?im)^\s*{name}\s*:?\s*$', text): matches.append((m.start(), name, m.end()))
    matches=sorted(matches)
    if not matches: return {'raw': text}
    sections={}
    for i,(start,name,end) in enumerate(matches):
        next_start=matches[i+1][0] if i+1<len(matches) else len(text)
        sections[name]=text[end:next_start].strip()
    sections['raw']=text
    return sections
