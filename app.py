from __future__ import annotations

import hashlib
import uuid
from urllib.parse import urlparse

import pandas as pd
import plotly.express as px
import streamlit as st

from autoapply_ai.analytics import learning_roadmap, market_skills
from autoapply_ai.database import init_db
from autoapply_ai.demo_data import DEMO_JOBS
from autoapply_ai.job_sources import fetch_jobs
from autoapply_ai.job_crawler import crawl_job_links
from autoapply_ai.models import ResumeProfile
from autoapply_ai.prep import make_prep_packet, save_prep_packet
from autoapply_ai.profile_store import DEFAULT_PROFILE, list_profiles, load_profile, save_profile
from autoapply_ai.relevance import build_queries
from autoapply_ai.resume_parser import extract_text_from_upload, extract_skills
from autoapply_ai.searches import save_search, recent_searches
from autoapply_ai.tailoring import ats_keyword_coverage, tailored_resume_bullets, interview_questions, follow_up_message
from autoapply_ai.storage import ranked_jobs, score_all_jobs, update_status, upsert_jobs, mark_apply_opened
from autoapply_ai.auth import create_or_get_user
from autoapply_ai.alerts import create_alert, list_alerts
from autoapply_ai.resume_sections import extract_sections
from autoapply_ai.filters import passes_user_filters

st.set_page_config(
    page_title="AutoApply AI Pro v9",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

DARK_CSS = """
<style>
:root {
  --bg: #0b1020;
  --panel: #111827;
  --panel2: #151f32;
  --text: #f9fafb;
  --muted: #9ca3af;
  --border: rgba(255,255,255,.10);
  --accent: #8b5cf6;
  --accent2: #22c55e;
  --danger: #ef4444;
  --warning: #f59e0b;
}
.block-container { padding-top: 1.1rem; max-width: 1450px; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0f172a 0%, #111827 100%); }
.main-title {font-size: 2.2rem; font-weight: 800; margin-bottom: .15rem;}
.subtitle {color: var(--muted); font-size: 1.02rem; margin-bottom: 1rem;}
.workflow-card, .job-card, .profile-card {
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.0rem 1.1rem;
  margin-bottom: .9rem;
  background: linear-gradient(180deg, rgba(17,24,39,.98), rgba(15,23,42,.98));
  box-shadow: 0 8px 24px rgba(0,0,0,.20);
}
.job-card h3 {margin: 0 0 .25rem 0; font-size: 1.25rem;}
.badge {
  display: inline-block;
  padding: .18rem .55rem;
  border-radius: 999px;
  background: rgba(139,92,246,.20);
  border: 1px solid rgba(139,92,246,.35);
  color: #ddd6fe;
  font-size: .82rem;
  font-weight: 700;
}
.badge-green {background: rgba(34,197,94,.16); border-color: rgba(34,197,94,.30); color: #bbf7d0;}
.badge-red {background: rgba(239,68,68,.16); border-color: rgba(239,68,68,.30); color: #fecaca;}
.badge-yellow {background: rgba(245,158,11,.16); border-color: rgba(245,158,11,.30); color: #fde68a;}
.small-muted {color: var(--muted); font-size: .92rem;}
hr {border-color: var(--border);}
.stButton > button {border-radius: 12px;}
.apply-link {display:block;text-align:center;text-decoration:none;border-radius:12px;padding:.52rem .75rem;background:#7c3aed;color:white!important;font-weight:800;border:1px solid rgba(255,255,255,.15);}
.apply-link:hover {background:#6d28d9;color:white!important;text-decoration:none;}
[data-testid="stMetricValue"] {font-weight: 800;}
</style>
"""
st.markdown(DARK_CSS, unsafe_allow_html=True)


def session_from_email(email: str, fallback: str | None = None) -> str:
    if email.strip():
        return "user-" + hashlib.sha1(email.strip().lower().encode()).hexdigest()[:12]
    return fallback or "session-" + str(uuid.uuid4())[:8]


def valid_url(url: object) -> str:
    if url is None or pd.isna(url):
        return ""
    url = str(url).strip()
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return url
    return ""


def priority_badge(priority: str) -> str:
    if priority == "High":
        return "badge badge-green"
    if priority == "Reject":
        return "badge badge-red"
    if priority == "Medium":
        return "badge badge-yellow"
    return "badge"


if "session_id" not in st.session_state:
    st.session_state.session_id = session_from_email(DEFAULT_PROFILE.email)
    save_profile(DEFAULT_PROFILE)
if "profile_ready" not in st.session_state:
    st.session_state.profile_ready = False

st.markdown("<div class='main-title'>🎯 AutoApply AI Pro v9</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Create a candidate profile, upload a resume, fetch live job postings, rank them by fit, track applications, and open the external application page.</div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Workflow")
    st.caption("Session-safe profile mode for local and deployed demos.")
    st.markdown("1. Create/load profile  ")
    st.markdown("2. Upload resume  ")
    st.markdown("3. Fetch jobs  ")
    st.markdown("4. Review matches  ")
    st.markdown("5. Apply externally  ")
    st.divider()

    profiles = list_profiles()
    labels = [f"{p.get('name') or 'Candidate'} — {p.get('email') or p.get('session_id')}" for p in profiles]
    session_lookup = {label: p["session_id"] for label, p in zip(labels, profiles)}
    if labels:
        selected = st.selectbox("Load saved profile", labels, index=0)
        if st.button("Load Selected Profile", use_container_width=True):
            st.session_state.session_id = session_lookup[selected]
            st.session_state.profile_ready = True
            st.success("Profile loaded.")

    st.divider()
    st.subheader("Job Fetch Settings")
    sources = st.multiselect("Sources", ["Remotive", "Arbeitnow", "RemoteOK"], default=["Remotive", "Arbeitnow", "RemoteOK"])
    strict_mode = st.toggle("Strict data/analytics filter", value=True)
    min_score = st.slider("Minimum match score", 0, 100, 60)
    jobs_per_search = st.slider("Jobs per fetch", 10, 100, 50)
    show_count = st.slider("Cards to show", 5, 50, 15)
    crawl_url = st.text_input("Optional careers page URL", placeholder="https://company.com/careers")
    st.caption("Strict mode removes sales, support, teaching, recruiting, and unrelated roles before ranking. Add a careers URL to extract public job links from a company page.")
    remote_only = st.toggle("Remote only", value=True)
    us_only = st.toggle("US-friendly only", value=False)
    min_salary_filter = st.number_input("Minimum salary filter", min_value=0, max_value=250000, value=0, step=5000)
    employment_filter = st.selectbox("Employment type filter", ["Any", "Full-time", "Contract", "Part-time", "Internship"])
    blocked_companies_txt = st.text_area("Blocked companies", placeholder="One company per line", height=70)
    whitelisted_companies_txt = st.text_area("Whitelisted companies", placeholder="Optional: one company per line", height=70)

profile = load_profile(st.session_state.session_id)

with st.expander("Recent searches", expanded=False):
    recent = recent_searches(profile.session_id)
    if recent.empty:
        st.caption("No saved searches yet.")
    else:
        st.dataframe(recent[["query", "sources", "strict_mode", "min_score", "results_count", "created_at"]], use_container_width=True, hide_index=True)

step1, step2, step3 = st.columns([1.1, 1.2, 1.0])

with step1:
    st.markdown("<div class='workflow-card'>", unsafe_allow_html=True)
    st.subheader("1. Candidate Profile")
    with st.form("profile_form"):
        name = st.text_input("Name", value=profile.name if profile.name != "Candidate" else "")
        email = st.text_input("Email", value=profile.email)
        target_roles = st.text_area("Target roles", value=profile.target_roles, height=80)
        location = st.text_input("Preferred location", value=profile.preferred_location or "Remote")
        seniority = st.selectbox(
            "Seniority",
            ["Entry-Level / Junior", "Mid-Level", "Any"],
            index=["Entry-Level / Junior", "Mid-Level", "Any"].index(profile.seniority) if profile.seniority in ["Entry-Level / Junior", "Mid-Level", "Any"] else 0,
        )
        saved = st.form_submit_button("Save Profile", use_container_width=True)
        if saved:
            sid = session_from_email(email, st.session_state.session_id)
            st.session_state.session_id = sid
            user = create_or_get_user(email, name or "Candidate")
            sid = user.user_id
            st.session_state.session_id = sid
            profile = ResumeProfile(
                session_id=sid,
                name=name or "Candidate",
                email=email,
                raw_text=profile.raw_text,
                skills=profile.skills,
                target_roles=target_roles,
                preferred_location=location,
                seniority=seniority,
            )
            save_profile(profile)
            st.session_state.profile_ready = True
            st.success("Profile saved.")
    st.markdown("</div>", unsafe_allow_html=True)

with step2:
    st.markdown("<div class='workflow-card'>", unsafe_allow_html=True)
    st.subheader("2. Resume Upload")
    uploaded = st.file_uploader("Upload PDF or TXT resume", type=["pdf", "txt"])
    if uploaded is not None:
        if st.button("Parse Resume + Extract Skills", type="primary", use_container_width=True):
            text = extract_text_from_upload(uploaded)
            skills = ", ".join(extract_skills(text))
            profile = ResumeProfile(
                session_id=st.session_state.session_id,
                name=profile.name,
                email=profile.email,
                raw_text=text,
                skills=skills,
                target_roles=profile.target_roles,
                preferred_location=profile.preferred_location,
                seniority=profile.seniority,
            )
            save_profile(profile)
            st.session_state.profile_ready = True
            st.success(f"Resume parsed. Extracted {len([s for s in skills.split(',') if s.strip()])} skills.")
    st.text_area("Detected skills", value=profile.skills, height=115, disabled=True)
    if st.button("Use Recruiter Demo Profile", use_container_width=True):
        save_profile(DEFAULT_PROFILE)
        st.session_state.session_id = DEFAULT_PROFILE.session_id
        st.session_state.profile_ready = True
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with step3:
    st.markdown("<div class='workflow-card'>", unsafe_allow_html=True)
    st.subheader("3. Fetch Matching Jobs")
    profile = load_profile(st.session_state.session_id)
    suggested = build_queries(profile)
    search_mode = st.radio("Search mode", ["Auto from resume", "Custom query"], horizontal=True)
    custom_query = st.text_input("Custom query", value="junior data analyst python sql", disabled=search_mode == "Auto from resume")
    query_count = st.slider("Auto searches", 1, min(6, max(1, len(suggested))), min(3, len(suggested)))
    st.caption("Auto queries: " + "; ".join(suggested[:query_count]))
    if st.button("Fetch + Rank Jobs", type="primary", use_container_width=True):
        queries = suggested[:query_count] if search_mode == "Auto from resume" else [custom_query]
        saved = 0
        errors: list[str] = []
        with st.spinner("Fetching postings and matching them to your resume..."):
            for q in queries:
                jobs, errs = fetch_jobs(q, jobs_per_search, sources=sources, strict=strict_mode)
                if crawl_url.strip():
                    crawled, crawl_errs = crawl_job_links(crawl_url.strip(), limit=jobs_per_search, strict=strict_mode)
                    jobs.extend(crawled)
                    errs.extend(crawl_errs)
                saved += upsert_jobs(jobs)
                save_search(profile.session_id, q, ", ".join(sources) + (f", Crawl: {crawl_url.strip()}" if crawl_url.strip() else ""), strict_mode, min_score, len(jobs))
                errors.extend(errs)
            if saved == 0:
                saved += upsert_jobs(DEMO_JOBS)
                st.info("Live sources returned no new relevant jobs, so demo jobs were loaded for the interface.")
            scored = score_all_jobs(profile, min_score=min_score)
        st.success(f"Saved {saved} new postings and ranked {len(scored)} relevant matches.")
        for e in errors[:4]:
            st.warning(e)
    st.markdown("</div>", unsafe_allow_html=True)

profile = load_profile(st.session_state.session_id)
df = ranked_jobs(profile.session_id, min_score=min_score)
# User-configurable filters applied after ranking so users understand what was hidden.
if not df.empty:
    blocked_companies = [x.strip() for x in blocked_companies_txt.splitlines() if x.strip()] if "blocked_companies_txt" in globals() else []
    whitelisted_companies = [x.strip() for x in whitelisted_companies_txt.splitlines() if x.strip()] if "whitelisted_companies_txt" in globals() else []
    mask=[]
    filter_reasons=[]
    for _, r in df.iterrows():
        ok, reasons = passes_user_filters(r.to_dict(), remote_only=remote_only if "remote_only" in globals() else False, us_only=us_only if "us_only" in globals() else False, min_salary=min_salary_filter if "min_salary_filter" in globals() else 0, employment_type=employment_filter if "employment_filter" in globals() else "Any", blocked_companies=blocked_companies, whitelisted_companies=whitelisted_companies)
        mask.append(ok); filter_reasons.append(", ".join(reasons))
    df["filter_reasons"] = filter_reasons
    df = df[mask]

if df.empty:
    st.info("Create a profile, upload a resume, then click **Fetch + Rank Jobs**. You can also load demo data to preview the dashboard.")
    if st.button("Load polished demo jobs", use_container_width=True):
        upsert_jobs(DEMO_JOBS)
        score_all_jobs(profile, min_score=0)
        st.rerun()
    st.stop()

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Relevant Matches", len(df))
m2.metric("Average Match", f"{df['match_score'].mean():.0f}%")
m3.metric("High Priority", int((df["priority"] == "High").sum()))
m4.metric("Ready to Apply", int(df["url"].fillna("").astype(str).str.startswith("http").sum()))
m5.metric("Applied / Viewed", int(df["status"].isin(["Viewed", "Applied", "Interview"]).sum()))

st.divider()

tab_matches, tab_pipeline, tab_tailor, tab_analytics, tab_profile, tab_data = st.tabs([
    "🚀 Top Matches", "📌 Application Pipeline", "🧠 Tailor + Prep", "📊 Market Analytics", "👤 Profile", "🗄️ Data"
])

with tab_matches:
    f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
    search = f1.text_input("Search within results", "")
    priorities = sorted([p for p in df["priority"].dropna().unique()])
    statuses = sorted([s for s in df["status"].dropna().unique()])
    selected_priorities = f2.multiselect("Priority", priorities, default=[p for p in priorities if p != "Reject"] or priorities)
    selected_statuses = f3.multiselect("Status", statuses, default=[s for s in statuses if s != "Rejected"] or statuses)
    classifications = sorted([c for c in df["classification"].dropna().unique()])
    selected_classes = f4.multiselect("Class", classifications, default=[c for c in classifications if c != "Unrelated"] or classifications)

    view = df[df["priority"].isin(selected_priorities) & df["status"].isin(selected_statuses) & df["classification"].isin(selected_classes)].copy()
    if search:
        s = search.lower()
        view = view[view.apply(lambda r: s in f"{r['title']} {r['company']} {r['description']} {r['why_match']}".lower(), axis=1)]

    st.caption(f"Showing {min(show_count, len(view))} of {len(view)} filtered results.")
    for _, job in view.head(show_count).iterrows():
        url = valid_url(job.get("url"))
        badge_class = priority_badge(job.get("priority", ""))
        st.markdown(
            f"""
            <div class='job-card'>
              <h3>{job['title']} <span class='badge'>{job['match_score']:.0f}% match</span> <span class='{badge_class}'>{job['priority']}</span></h3>
              <div class='small-muted'><b>{job['company']}</b> • {job['location']} • {job['source']} • {job['classification']}</div>
              <br>
              <b>Why it matches:</b> {job['why_match']}<br>
              <b>Missing skills:</b> {job['missing_skills'] or 'None obvious'}<br>
              <b>Risk flags:</b> {job['risk_flags'] or 'None'}<br>
              <b>Job quality:</b> {job.get('job_quality_score', 0):.0f}/100 {(' — ' + str(job.get('quality_flags'))) if str(job.get('quality_flags','')).strip() else ''}
            </div>
            """,
            unsafe_allow_html=True,
        )
        a, b, c, d, e, f = st.columns([1.2, .9, .9, .9, 1.2, 1.5])
        if url:
            a.markdown(f"<a class='apply-link' href='{url}' target='_blank' rel='noopener noreferrer'>Apply on Website ↗</a>", unsafe_allow_html=True)
        else:
            a.button("No Apply URL", disabled=True, use_container_width=True)
        if b.button("Track Viewed", key=f"viewed_{job['id']}", use_container_width=True):
            mark_apply_opened(profile.session_id, int(job["id"]))
            st.rerun()
        if c.button("Applied", key=f"applied_{job['id']}", use_container_width=True):
            update_status(profile.session_id, int(job["id"]), "Applied")
            st.rerun()
        if d.button("Reject", key=f"reject_{job['id']}", use_container_width=True):
            update_status(profile.session_id, int(job["id"]), "Rejected")
            st.rerun()
        if e.button("Prep Packet", key=f"packet_{job['id']}", use_container_width=True):
            path = save_prep_packet(job.to_dict(), profile)
            st.success(f"Saved {path}")
        packet = make_prep_packet(job.to_dict(), profile)
        f.download_button("Download Prep", packet, file_name=f"prep_packet_{int(job['id'])}.md", use_container_width=True)
        with st.expander("ATS coverage + resume tailoring", expanded=False):
            coverage = ats_keyword_coverage(str(job.get("description", "")), profile.raw_text, profile.skills)
            st.metric("ATS keyword coverage", f"{coverage['coverage']:.0f}%")
            st.write("**Present keywords:** " + (", ".join(coverage["present"][:15]) or "None detected"))
            st.write("**Missing keywords:** " + (", ".join(coverage["missing"][:15]) or "None detected"))
            st.write("**Suggested resume bullets:**")
            for bullet in tailored_resume_bullets(job.to_dict(), profile):
                st.write("• " + bullet)

with tab_pipeline:
    st.subheader("Application Pipeline")
    pipeline = df.groupby("status").size().reset_index(name="count")
    st.plotly_chart(px.bar(pipeline, x="status", y="count", title="Jobs by status"), use_container_width=True)
    st.dataframe(df[["id", "match_score", "priority", "company", "title", "status", "url"]], use_container_width=True, hide_index=True)

with tab_tailor:
    st.subheader("Role-specific apply prep")
    selected_id = st.selectbox("Choose a job", df["id"].astype(int).tolist(), format_func=lambda jid: f"#{jid} — " + str(df.loc[df["id"] == jid, "title"].iloc[0])[:80])
    selected_job = df[df["id"] == selected_id].iloc[0].to_dict()
    c1, c2 = st.columns([1,1])
    with c1:
        st.markdown("### Resume tailoring bullets")
        for bullet in tailored_resume_bullets(selected_job, profile):
            st.write("• " + bullet)
        cov = ats_keyword_coverage(selected_job.get("description", ""), profile.raw_text, profile.skills)
        st.metric("Keyword coverage", f"{cov['coverage']:.0f}%")
        st.write("**Top missing keywords:** " + (", ".join(cov["missing"][:12]) or "None"))
    with c2:
        st.markdown("### Interview prep")
        for q in interview_questions(selected_job):
            st.write("• " + q)
        st.markdown("### Follow-up message")
        st.text_area("Copy-ready follow-up", follow_up_message(selected_job, profile), height=170)
    st.download_button("Download full prep packet", make_prep_packet(selected_job, profile), file_name=f"prep_packet_{int(selected_id)}.md", use_container_width=True)

with tab_analytics:
    left, right = st.columns(2)
    with left:
        st.subheader("Match Score Distribution")
        st.plotly_chart(px.histogram(df, x="match_score", nbins=12), use_container_width=True)
    with right:
        st.subheader("Most Requested Skills")
        skills = market_skills(df)
        if not skills.empty:
            st.plotly_chart(px.bar(skills.head(15), x="count", y="skill", orientation="h"), use_container_width=True)
        else:
            st.info("Not enough skill data yet.")
    st.subheader("Learning Roadmap")
    for item in learning_roadmap(df["missing_skills"]):
        st.write("✅ " + item)

with tab_profile:
    st.markdown("<div class='profile-card'>", unsafe_allow_html=True)
    st.subheader(profile.name or "Candidate")
    st.write(f"**Email:** {profile.email or 'Not set'}")
    st.write(f"**Target roles:** {profile.target_roles}")
    st.write(f"**Preferred location:** {profile.preferred_location}")
    st.write(f"**Seniority:** {profile.seniority}")
    st.write(f"**Skills:** {profile.skills or 'Upload a resume to extract skills.'}")
    st.markdown("</div>", unsafe_allow_html=True)
    with st.expander("Resume sections"):
        sections = extract_sections(profile.raw_text)
        for section_name, section_text in sections.items():
            if section_name != "raw":
                st.markdown(f"**{section_name.title()}**")
                st.write(section_text[:1200] or "No content detected.")
    with st.expander("Resume text used for matching"):
        st.text_area("Resume text", value=profile.raw_text, height=300)
    st.subheader("Job Alerts")
    alert_query = st.text_input("Alert query", value="junior data analyst python sql")
    alert_score = st.slider("Alert minimum score", 60, 95, 80)
    if st.button("Save alert", use_container_width=True):
        create_alert(profile.session_id, alert_query, alert_score)
        st.success("Alert saved. In production, connect this to a scheduled job/email provider.")
    alerts = list_alerts(profile.session_id)
    if alerts:
        st.dataframe(pd.DataFrame(alerts), use_container_width=True, hide_index=True)

with tab_data:
    st.subheader("Normalized Job Table")
    columns = ["id", "match_score", "priority", "classification", "company", "title", "location", "source", "status", "url"]
    st.dataframe(df[columns], use_container_width=True, hide_index=True)
    st.download_button("Download matches CSV", df.to_csv(index=False), file_name="autoapply_ranked_matches.csv", use_container_width=True)
