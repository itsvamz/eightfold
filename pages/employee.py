import streamlit as st
import urllib.parse
from data import EMPLOYEES, OPEN_ROLES, COURSES, LEARNING_WEEKS
from scoring import compute_full, get_upskill_courses, gen_recommendation, gen_msg, llm_call, TALENT_SENDER
from styles import fmt_inr, score_color, bar_html, initials, pills, page_header, topbar, footer, show_email

def render_employee(emp):
    # apply any in-session profile updates
    upd = st.session_state.profile_updates.get(emp["id"], {})
    for k, v in upd.items():
        emp[k] = v

    gh = emp.get("github_data", {})
    apps = st.session_state.applications.get(emp["id"], [])

    # ── sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style="padding:20px 8px 24px;border-bottom:1px solid #1A2B6B;margin-bottom:16px;text-align:center">
          <div class="sb-av">{initials(emp['name'])}</div>
          <div class="sb-name">{emp['name']}</div>
          <div class="sb-role">{emp['current_role']} · {emp['department']}</div>
        </div>
        """, unsafe_allow_html=True)
        page = st.radio("", [
            "Dashboard", "Open Roles", "Match Scores", "Skill Courses", "My Profile"
        ], label_visibility="collapsed")
        st.markdown("---")
        if st.button("Sign out", use_container_width=True):
            st.session_state.role    = None
            st.session_state.user_id = None
            st.rerun()

    topbar(f"Employee Portal &nbsp;·&nbsp; {emp['name']}")
    st.markdown('<div class="tglow"></div>', unsafe_allow_html=True)

    # ── DASHBOARD ─────────────────────────────────────────────────────────────
    if page == "Dashboard":
        page_header("Employee Portal", f"Welcome back, {emp['name'].split()[0]}", f"{emp['current_role']} · {emp['department']} · {emp['years_exp']} years experience")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Skills listed",      len(emp["skills"]))
        c2.metric("Commits / 6 mo",     gh.get("commits_6mo", 0))
        c3.metric("OSS pull requests",  gh.get("open_source_prs", 0))
        c4.metric("Applications sent",  len(apps))

        st.markdown("<br>", unsafe_allow_html=True)
        left, right = st.columns([3, 2])

        with left:
            st.markdown('<span class="slabel">Role alerts</span>', unsafe_allow_html=True)
            found = False
            for role in OPEN_ROLES:
                res = compute_full(emp, role)
                if res["total"] < 40:
                    continue
                found = True
                applied  = role["role_id"] in apps
                urg_col  = "#EF4444" if role["urgency"] == "High" else "#F59E0B"
                mp       = pills(res["matched"][:4], "p-g")
                applied_badge = '&nbsp;<span class="badge bg-g">Applied</span>' if applied else ""
                st.markdown(f"""
                <div class="notif">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div>
                      <div class="notif-title">{role['title']}{applied_badge}</div>
                      <div class="notif-sub">{role['department']} &nbsp;·&nbsp;
                        <span style="color:{urg_col}">{role['urgency']} urgency</span>
                      </div>
                      <div style="margin-top:8px">{mp}</div>
                    </div>
                    <div style="text-align:right">
                      <div class="score-md" style="color:{score_color(res['total'])}">{res['total']}</div>
                      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#7B8BB2">/ 100</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

            if not found:
                st.markdown('<div class="card-sm" style="color:#7B8BB2;font-size:13px">No strong matches right now — keep your skills updated!</div>', unsafe_allow_html=True)

        with right:
            st.markdown('<span class="slabel">Your skills</span>', unsafe_allow_html=True)
            st.markdown(f'<div class="card">{pills(emp["skills"], "p-b")}</div>', unsafe_allow_html=True)
            st.markdown('<span class="slabel">GitHub activity</span>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card" style="font-size:13px;color:#7B8BB2;line-height:2">
              {gh.get('total_repos',0)} repositories &nbsp;·&nbsp; {gh.get('commits_6mo',0)} commits / 6 months<br>
              {gh.get('open_source_prs',0)} open-source pull requests &nbsp;·&nbsp; avg {gh.get('avg_repo_stars',0)} stars<br>
              {gh.get('streak_days',0)}-day contribution streak<br>
              <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#00C9A7">
                {', '.join(gh.get('top_languages', []))}
              </span>
            </div>""", unsafe_allow_html=True)

            if apps:
                st.markdown('<span class="slabel">Your applications</span>', unsafe_allow_html=True)
                for rid in apps:
                    role = next((r for r in OPEN_ROLES if r["role_id"] == rid), None)
                    if role:
                        st.markdown(f'<div class="card-sm"><div style="font-size:13px;color:#86efac;font-weight:500">{role["title"]}</div><div style="font-size:11px;color:#7B8BB2">{role["department"]} · Submitted</div></div>', unsafe_allow_html=True)

    # ── OPEN ROLES ────────────────────────────────────────────────────────────
    elif page == "Open Roles":
        page_header("Opportunities", "Open Roles", "Internal openings matched to your profile.")

        for role in OPEN_ROLES:
            res      = compute_full(emp, role)
            applied  = role["role_id"] in apps
            urg_col  = "#EF4444" if role["urgency"] == "High" else "#F59E0B"

            with st.expander(f"{role['title']}  ·  {res['total']}/100 match{'  ·  Applied' if applied else ''}"):
                cL, cR = st.columns([3, 1])
                with cL:
                    urg_badge = f'<span class="badge bg-r">{role["urgency"]} urgency</span>' if role["urgency"] == "High" else f'<span class="badge bg-a">{role["urgency"]} urgency</span>'
                    st.markdown(f"""
                    <div style="font-size:18px;font-family:'Libre Baskerville',serif;font-weight:700;color:#F0F4FF">{role['title']}</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#00C9A7;text-transform:uppercase;letter-spacing:0.1em;margin:4px 0 10px">
                      {role['department']} &nbsp;·&nbsp; Posted {role['posted_date']}
                    </div>
                    <div style="font-size:13px;color:#7B8BB2;line-height:1.65;margin-bottom:12px">{role['description']}</div>
                    {urg_badge}
                    <div style="margin-top:14px">
                      <span class="slabel">Skill match</span>
                      {pills(res['matched'],'p-g')}
                      {pills(res['missing'],'p-r')}
                      {''.join(f'<span class="pill p-a">{a["skill"]} via {a["bridge"]}</span>' for a in res['adjacent'])}
                    </div>
                    """, unsafe_allow_html=True)
                with cR:
                    st.markdown(f"""
                    <div style="text-align:center;padding:20px;background:#0B1437;border-radius:12px;border:1px solid #1A2B6B">
                      <div class="score-hero" style="color:{score_color(res['total'])}">{res['total']}</div>
                      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#7B8BB2">/ 100 match</div>
                      <div style="font-size:12px;color:#22C55E;margin-top:8px">Saves {fmt_inr(res['budget']['saving'])}</div>
                      <div style="font-size:11px;color:#7B8BB2">vs ext. hire</div>
                    </div>""", unsafe_allow_html=True)

                # courses
                if res["missing"] or res["adjacent"]:
                    st.markdown('<span class="slabel" style="margin-top:16px;display:block">Courses to bridge the gap</span>', unsafe_allow_html=True)
                    shown = set()
                    for skill in res["missing"] + [a["skill"] for a in res["adjacent"]]:
                        if skill in shown or skill not in COURSES:
                            continue
                        shown.add(skill)
                        cr  = COURSES[skill]
                        adj = next((a for a in res["adjacent"] if a["skill"] == skill), None)
                        wks = LEARNING_WEEKS.get(adj["distance"], cr["weeks"]) if adj else cr["weeks"]
                        cost_tag = '<span class="tag-free">Free</span>' if cr["cost"] == 0 else f'<span class="tag-paid">₹{cr["cost"]}</span>'
                        note     = f'via {adj["bridge"]} · {adj["reason"]}' if adj else "required skill"
                        st.markdown(f"""
                        <div class="cc">
                          <div>
                            <div class="cc-title">{skill} — {cr['course']}</div>
                            <div class="cc-meta">{cr['platform']} · {wks} weeks · {note}</div>
                          </div>
                          <div style="display:flex;gap:8px;align-items:center;flex-shrink:0">
                            {cost_tag}
                            <a href="{cr['url']}" target="_blank" class="open-btn">Open course</a>
                          </div>
                        </div>""", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                if applied:
                    st.markdown("""
                    <div class="app-banner">
                      <span style="font-size:16px;font-weight:700">&#10003;</span>
                      <div>
                        <div style="font-weight:600">Application submitted</div>
                        <div style="font-size:12px;opacity:0.8">The talent team has been notified and will reach out.</div>
                      </div>
                    </div>""", unsafe_allow_html=True)
                else:
                    ca, cb = st.columns(2)
                    with ca:
                        if st.button("Apply for this role", key=f"apply_{role['role_id']}", type="primary"):
                            if emp["id"] not in st.session_state.applications:
                                st.session_state.applications[emp["id"]] = []
                            if role["role_id"] not in st.session_state.applications[emp["id"]]:
                                st.session_state.applications[emp["id"]].append(role["role_id"])
                            from datetime import datetime
                            st.session_state.admin_notifs.append({
                                "emp_id":     emp["id"],
                                "emp_name":   emp["name"],
                                "role_id":    role["role_id"],
                                "role_title": role["title"],
                                "score":      res["total"],
                                "time":       datetime.now().strftime("%H:%M"),
                            })
                            st.rerun()
                    with cb:
                        if st.button("Get AI insight", key=f"ai_{role['role_id']}"):
                            with st.spinner("Generating..."):
                                rec = gen_recommendation(res, role)
                            st.info(rec or "Add a Groq API key in scoring.py to enable AI insights.")

    # ── MATCH SCORES ─────────────────────────────────────────────────────────
    elif page == "Match Scores":
        page_header("Your Performance", "Match Scores", "How your profile ranks against every open role.")
        for role in OPEN_ROLES:
            res     = compute_full(emp, role)
            b       = res["breakdown"]
            applied = role["role_id"] in apps
            st.markdown(f"""
            <div class="card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div>
                  <div style="font-size:18px;font-family:'Libre Baskerville',serif;font-weight:700;color:#F0F4FF">{role['title']}</div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#00C9A7;text-transform:uppercase;letter-spacing:0.1em;margin-top:3px">
                    {role['department']}{"&nbsp;·&nbsp;<span class='badge bg-g'>Applied</span>" if applied else ""}
                  </div>
                </div>
                <div style="text-align:right">
                  <div class="score-lg" style="color:{score_color(res['total'])}">{res['total']}<span style="font-size:15px;color:#7B8BB2">/100</span></div>
                </div>
              </div>
              <div class="ss">
                <div class="si"><div class="sn">{b['skill']}</div><div class="sl">Skill</div></div>
                <div class="si"><div class="sn">{b['semantic']}</div><div class="sl">Semantic</div></div>
                <div class="si"><div class="sn">{b['github']}</div><div class="sl">GitHub</div></div>
                <div class="si"><div class="sn">{res['ttp']}w</div><div class="sl">Time-to-prod</div></div>
              </div>
              <div style="margin-top:10px">
                {pills(res['matched'],'p-g')}{pills(res['missing'],'p-r')}
              </div>
              <div style="margin-top:8px"><span class="badge bg-g">Bias check passed</span></div>
            </div>""", unsafe_allow_html=True)

    # ── SKILL COURSES ─────────────────────────────────────────────────────────
    elif page == "Skill Courses":
        page_header("Learning Path", "Skill Courses", "Personalised recommendations based on your gaps across all open roles.")
        all_missing, all_adjacent, seen = set(), [], set()
        for role in OPEN_ROLES:
            res = compute_full(emp, role)
            for s in res["missing"]:
                if s not in seen: all_missing.add(s); seen.add(s)
            for a in res["adjacent"]:
                if a["skill"] not in seen: all_adjacent.append(a); seen.add(a["skill"])

        if all_missing:
            st.markdown('<span class="slabel">Required — missing from open roles</span>', unsafe_allow_html=True)
            for skill in all_missing:
                cr = COURSES.get(skill)
                if not cr: continue
                cost_tag = '<span class="tag-free">Free</span>' if cr["cost"] == 0 else f'<span class="tag-paid">₹{cr["cost"]}</span>'
                st.markdown(f"""
                <div class="cc">
                  <div>
                    <div class="cc-title">{skill} — {cr['course']}</div>
                    <div class="cc-meta">{cr['platform']} · {cr['weeks']} weeks ·
                      <span style="color:#EF4444">Missing from open roles</span>
                    </div>
                  </div>
                  <div style="display:flex;gap:8px;align-items:center;flex-shrink:0">
                    {cost_tag}
                    <a href="{cr['url']}" target="_blank" class="open-btn">Open course</a>
                  </div>
                </div>""", unsafe_allow_html=True)

        if all_adjacent:
            st.markdown('<span class="slabel" style="margin-top:22px;display:block">Fast learnable — you already know adjacent skills</span>', unsafe_allow_html=True)
            for a in all_adjacent:
                cr = COURSES.get(a["skill"])
                if not cr: continue
                wks      = LEARNING_WEEKS.get(a["distance"], 12)
                cost_tag = '<span class="tag-free">Free</span>' if cr["cost"] == 0 else f'<span class="tag-paid">₹{cr["cost"]}</span>'
                st.markdown(f"""
                <div class="cc">
                  <div>
                    <div class="cc-title">{a['skill']} — {cr['course']}</div>
                    <div class="cc-meta">{cr['platform']} · ~{wks} weeks ·
                      <span style="color:#F59E0B">You know {a['bridge']} — {a['reason']}</span>
                    </div>
                  </div>
                  <div style="display:flex;gap:8px;align-items:center;flex-shrink:0">
                    {cost_tag}
                    <a href="{cr['url']}" target="_blank" class="open-btn">Open course</a>
                  </div>
                </div>""", unsafe_allow_html=True)

        if not all_missing and not all_adjacent:
            st.success("You already meet all skill requirements for current open roles — keep an eye out for new postings.")

    # ── MY PROFILE ────────────────────────────────────────────────────────────
    elif page == "My Profile":
        page_header("Account", "My Profile", "Keep this updated — the talent team sees changes in real time.")
        left, right = st.columns([2, 3])

        with left:
            certs_html = "".join(f'<div style="font-size:12px;color:#7B8BB2;margin:4px 0">— {c}</div>' for c in emp.get("certifications", []))
            st.markdown(f"""
            <div class="card">
              <div style="display:flex;gap:16px;align-items:center;margin-bottom:18px">
                <div class="av av-lg">{initials(emp['name'])}</div>
                <div>
                  <div class="prof-name">{emp['name']}</div>
                  <div class="prof-role">{emp['current_role']} · {emp['department']}</div>
                  <div class="prof-detail">{'Female' if emp['gender']=='F' else 'Male'} · {emp['years_exp']}y exp · {emp['tenure_years']}y tenure</div>
                </div>
              </div>
              <hr>
              <span class="slabel">About</span>
              <div style="font-size:13px;color:#7B8BB2;line-height:1.65">{emp.get('bio','')}</div>
              <span class="slabel">Education</span>
              <div style="font-size:13px;color:#7B8BB2">{emp.get('education','')}</div>
              <span class="slabel">Certifications</span>
              {certs_html or '<div style="font-size:12px;color:#4a5568">None listed</div>'}
              <hr>
              <div style="font-size:13px;color:#7B8BB2;margin-bottom:8px">{emp['email']}</div>
              <div style="display:flex;gap:16px">
                <a href="{emp.get('github_url','')}" target="_blank">GitHub</a>
                <a href="{emp.get('linkedin','')}" target="_blank">LinkedIn</a>
              </div>
            </div>""", unsafe_allow_html=True)

            gh = emp.get("github_data", {})
            st.markdown(f"""
            <div class="card">
              <span class="slabel">GitHub signals</span>
              <div class="ss">
                <div class="si"><div class="sn">{gh.get('commits_6mo',0)}</div><div class="sl">Commits</div></div>
                <div class="si"><div class="sn">{gh.get('open_source_prs',0)}</div><div class="sl">OSS PRs</div></div>
                <div class="si"><div class="sn">{gh.get('avg_repo_stars',0)}</div><div class="sl">Stars</div></div>
                <div class="si"><div class="sn">{gh.get('streak_days',0)}d</div><div class="sl">Streak</div></div>
              </div>
              <div style="font-size:11px;color:#7B8BB2;margin-top:8px">{', '.join(gh.get('top_languages',[]))}</div>
            </div>""", unsafe_allow_html=True)

        with right:
            st.markdown('<div style="font-size:22px;font-family:Libre Baskerville,serif;font-weight:700;color:#F0F4FF;margin-bottom:16px">Edit profile</div>', unsafe_allow_html=True)
            with st.form("profile_form"):
                nb  = st.text_area("About",                value=emp.get("bio", ""),                          height=90)
                ns  = st.text_input("Skills (comma-separated)", value=", ".join(emp.get("skills", [])))
                ne  = st.text_input("Education",           value=emp.get("education", ""))
                ng  = st.text_input("GitHub URL",          value=emp.get("github_url", ""))
                nl  = st.text_input("LinkedIn URL",        value=emp.get("linkedin", ""))
                nc  = st.text_area("Certifications (one per line)", value="\n".join(emp.get("certifications", [])), height=80)
                al  = st.checkbox("Enable role match alerts", value=emp.get("alerts_enabled", True))
                if st.form_submit_button("Save changes", type="primary", use_container_width=True):
                    sk = [x.strip() for x in ns.split(",") if x.strip()]
                    ct = [x.strip() for x in nc.split("\n") if x.strip()]
                    upd = {"bio":nb,"education":ne,"github_url":ng,"linkedin":nl,"certifications":ct,"skills":sk,"alerts_enabled":al}
                    st.session_state.profile_updates[emp["id"]] = upd
                    for k, v in upd.items(): emp[k] = v
                    st.success("Profile updated — talent team can see your changes now.")

    footer()
