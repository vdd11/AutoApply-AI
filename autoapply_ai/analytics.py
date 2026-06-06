from collections import Counter
import pandas as pd
from .relevance import DATA_SKILLS
def market_skills(df: pd.DataFrame) -> pd.DataFrame:
    counts=Counter()
    for _,row in df.iterrows():
        text=f"{row.get('title','')} {row.get('description','')}".lower()
        for skill in DATA_SKILLS:
            if skill in text: counts[skill]+=1
    return pd.DataFrame([{"skill":k,"count":v} for k,v in counts.most_common(20)])
def learning_roadmap(missing_series):
    counts=Counter()
    for item in missing_series.dropna().astype(str):
        for skill in [x.strip() for x in item.split(',') if x.strip()]: counts[skill]+=1
    return [f"Build a small project or notebook using {skill} and add it to your GitHub/resume." for skill,_ in counts.most_common(6)] or ["Your profile matches current jobs well. Focus on applying and project polish."]
