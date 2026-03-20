import streamlit as st
import urllib.parse
from datetime import datetime
from data import EMPLOYEES, OPEN_ROLES, COURSES, LEARNING_WEEKS
from scoring import compute_full, score_all, get_upskill_courses, gen_email, gen_recommendation, gen_msg, llm_call, TALENT_SENDER
from styles import fmt_inr, score_color, bar_html, initials, pills, page_header, topbar, footer, show_email

def render_admin():
    notif_count = len(st.session_state.get("admin_notifs", []))
    nb = f" ({notif_count})" if notif_count else ""

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:20px 8px 24px;border-bottom:1px solid #1A2B6B;margin-bottom:16px;text-align:center">
          <div style="font-family:'Libre Baskerville',serif;font-size:22px;font-weight:700;color:#F0F4FF;letter-spacing:-0.5px">TalentIQ</div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#00C9A7;text-transform:uppercase;letter-spacing:0.15em;margin-top:4px">Admin · Eightfold AI</div>
        </div>
        """, unsafe_allow_html=True)
        page = st.radio("", [
            "Analytics",
            "Find Candidates",
            "Employee Profiles",
            f"Applications{nb}",
            "Skill Gap Matrix",
            "Compare",
        ], label_visibility="collapsed")
        st.markdown("---")
        if st.button("Sign out", use_container_width=True):
            st.session_state.role = None
            st.rerun()

    topbar("Admin Panel &nbsp;·&nbsp; Talent Intelligence")
    st.markdown('<div class="tglow"></div>', unsafe_allow_html=True)

    # ── ANALYTICS ─────────────────────────────────────────────────────────────
    if page == "Analytics":
        page_header("Admin · Insights", "Workforce Analytics", "Real-time view across your internal talent pool.")

        total       = len(EMPLOYEES)
        female      = sum(1 for e in EMPLOYEES if e["gender"] == "F")
        avg_exp     = round(sum(e["years_exp"] for e in EMPLOYEES) / total, 1)
        avg_sal     = round(sum(e["current_salary"] for e in EMPLOYEES) / total / 100000, 1)
        total_commits = sum(e.get("github_data", {}).get("commits_6mo", 0) for e in EMPLOYEES)
        best_results  = [score_all(r, 1)[0] for r in OPEN_ROLES]
        total_saving  = sum(r["external_hire_cost"] for r in OPEN_ROLES) - sum(r["budget"]["offer"] for r in best_results)

        c1,c2,c3,c4,c5,c6 = st.columns(6)
        c1.metric("Employees",    total)
        c2.metric("Women",        f"{female} ({round(female/total*100)}%)")
        c3.metric("Avg experience", f"{avg_exp}y")
        c4.metric("Avg salary",   f"₹{avg_sal}L")
        c5.metric("Commits / 6mo", total_commits)
        c6.metric("Potential saving", fmt_inr(total_saving))

        st.markdown("<br>", unsafe_allow_html=True)
        left, right = st.columns(2)

        with left:
            st.markdown('<div class="card"><span class="slabel">Top skills across workforce</span>', unsafe_allow_html=True)
            freq = {}
            for e in EMPLOYEES:
                for s in e["skills"]: freq[s] = freq.get(s, 0) + 1
            top = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
            for sk, cnt in top:
                st.markdown(bar_html(sk, cnt, top[0][1]), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with right:
            st.markdown('<div class="card"><span class="slabel">GitHub activity ranking</span>', unsafe_allow_html=True)
            gh_sorted = sorted(EMPLOYEES, key=lambda e: e.get("github_data",{}).get("commits_6mo",0), reverse=True)[:8]
            mx2 = gh_sorted[0].get("github_data",{}).get("commits_6mo", 1)
            for e in gh_sorted:
                c = e.get("github_data",{}).get("commits_6mo", 0)
                st.markdown(bar_html(e["name"].split()[0], c, mx2, "#22C55E", " commits"), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        left2, right2 = st.columns(2)

        with left2:
            st.markdown('<div class="card"><span class="slabel">Department headcount & gender</span>', unsafe_allow_html=True)
            depts = {}
            for e in EMPLOYEES:
                d = e["department"]
                if d not in depts: depts[d] = {"total":0,"F":0,"M":0}
                depts[d]["total"] += 1; depts[d][e["gender"]] += 1
            mx3 = max(v["total"] for v in depts.values())
            for dept, data in sorted(depts.items(), key=lambda x: x[1]["total"], reverse=True):
                fp    = round(data["F"] / data["total"] * 100)
                color = "#EF4444" if fp < 25 else "#F59E0B" if fp < 40 else "#22C55E"
                st.markdown(bar_html(f"{dept} ({data['F']}F/{data['M']}M)", data["total"], mx3, color), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with right2:
            st.markdown('<div class="card"><span class="slabel">Best internal match per role</span>', unsafe_allow_html=True)
            for role, best in zip(OPEN_ROLES, best_results):
                st.markdown(f"""
                <div style="margin-bottom:14px">
                  <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                    <span style="font-size:12px;color:#CCD6F6">{role['title']}</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:11px;color:{score_color(best['total'])}">{best['emp']['name'].split()[0]} · {best['total']}/100</span>
                  </div>
                  {bar_html("", best['total'], 100, score_color(best['total']))}
                  <div style="font-size:11px;color:#7B8BB2;margin-top:3px">Saves {fmt_inr(best['budget']['saving'])} vs external</div>
                </div>""", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── FIND CANDIDATES ───────────────────────────────────────────────────────
    elif page == "Find Candidates":
        page_header("Admin · Search", "Find Candidates", "Score the entire talent pool against any role.")
        mode  = st.radio("", ["Preset roles", "Custom JD"], horizontal=True, label_visibility="collapsed")
        top_n = st.slider("Show top", 3, 10, 5, label_visibility="collapsed")

        if mode == "Preset roles":
            rt   = st.selectbox("", [r["title"] for r in OPEN_ROLES], label_visibility="collapsed")
            role = next(r for r in OPEN_ROLES if r["title"] == rt)
            st.markdown(f'<div style="margin:10px 0 16px">{pills(role["required_skills"],"p-b")}</div>', unsafe_allow_html=True)
            if st.button("Score all employees", type="primary"):
                with st.spinner("Scoring..."):
                    results = score_all(role, top_n)
                saving = sum(r["budget"]["saving"] for r in results)
                c1,c2,c3,c4 = st.columns(4)
                c1.metric("Top match",    f"{results[0]['total']}/100")
                c2.metric("Avg score",    f"{round(sum(r['total'] for r in results)/len(results),1)}/100")
                c3.metric("Budget saving", fmt_inr(saving))
                c4.metric("Scored",        len(EMPLOYEES))
                st.markdown("<br>", unsafe_allow_html=True)
                for i, res in enumerate(results):
                    _result_card(res, i, role)
        else:
            jd = st.text_area("", height=110, label_visibility="collapsed", placeholder="Paste any job description here…")
            si = st.text_input("", label_visibility="collapsed", placeholder="Required skills: Python, Docker, Kubernetes…")
            c1,c2,c3 = st.columns(3)
            with c1: bmin = st.number_input("Budget min",      value=1800000, step=100000)
            with c2: bmax = st.number_input("Budget max",      value=2400000, step=100000)
            with c3: bext = st.number_input("External cost",   value=2800000, step=100000)
            if st.button("Score", type="primary") and jd and si:
                req  = [x.strip() for x in si.split(",") if x.strip()]
                role = {"role_id":"C","title":"Custom Role","department":"Custom","required_skills":req,
                        "nice_to_have":[],"skill_weights":{s:2 for s in req},
                        "budget_min":bmin,"budget_max":bmax,"external_hire_cost":bext,
                        "team_composition":{"total":8,"female":2,"male":6},"description":jd}
                with st.spinner("Scoring..."):
                    results = score_all(role, top_n)
                for i, res in enumerate(results):
                    _result_card(res, i, role)

    # ── EMPLOYEE PROFILES ─────────────────────────────────────────────────────
    elif page == "Employee Profiles":
        page_header("Admin · People", "Employee Profiles", "Browse, filter, and reach out to internal talent.")

        cs, cd, cg = st.columns([3,2,2])
        with cs: search = st.text_input("", placeholder="Search by name or skill…", label_visibility="collapsed")
        with cd:
            depts  = ["All departments"] + sorted(set(e["department"] for e in EMPLOYEES))
            dept_f = st.selectbox("", depts, label_visibility="collapsed")
        with cg:
            gen_f  = st.selectbox("", ["All genders","Female","Male"], label_visibility="collapsed")

        fil = EMPLOYEES
        if search:
            sl  = search.lower()
            fil = [e for e in fil if sl in e["name"].lower() or any(sl in s.lower() for s in e["skills"])]
        if dept_f != "All departments": fil = [e for e in fil if e["department"] == dept_f]
        if gen_f  == "Female":          fil = [e for e in fil if e["gender"] == "F"]
        if gen_f  == "Male":            fil = [e for e in fil if e["gender"] == "M"]

        st.markdown(f'<div style="font-size:12px;color:#7B8BB2;margin-bottom:14px;font-family:JetBrains Mono,monospace">{len(fil)} profile(s)</div>', unsafe_allow_html=True)

        for e in fil:
            # apply any profile updates
            upd = st.session_state.profile_updates.get(e["id"], {})
            for k, v in upd.items(): e[k] = v

            gh       = e.get("github_data", {})
            sk_extra = f' <span class="pill p-p">+{len(e["skills"])-5}</span>' if len(e["skills"]) > 5 else ""
            sk_pills = pills(e["skills"][:5], "p-b") + sk_extra

            col_c, col_b = st.columns([6, 1])
            with col_c:
                st.markdown(f"""
                <div class="card" style="margin-bottom:6px;padding:16px 20px">
                  <div style="display:flex;gap:14px;align-items:center">
                    <div class="av av-sm">{initials(e['name'])}</div>
                    <div style="flex:1">
                      <div style="display:flex;justify-content:space-between;align-items:flex-start">
                        <div>
                          <div style="font-size:15px;font-weight:600;color:#CCD6F6;font-family:'Inter',sans-serif">{e['name']}</div>
                          <div style="font-size:12px;color:#7B8BB2">{e['current_role']} · {e['department']} · {e['years_exp']}y · {'F' if e['gender']=='F' else 'M'}</div>
                          <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a5568;margin-top:2px">{e['email']}</div>
                        </div>
                        <div style="text-align:right;font-family:'JetBrains Mono',monospace;font-size:10px;color:#7B8BB2">
                          {gh.get('commits_6mo',0)} commits · {gh.get('open_source_prs',0)} PRs
                        </div>
                      </div>
                      <div style="margin-top:8px">{sk_pills}</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)
            with col_b:
                if st.button("View", key=f"view_{e['id']}", use_container_width=True):
                    st.session_state.viewing_emp = e["id"]
                    st.rerun()

        if st.session_state.get("viewing_emp"):
            ve = next((e for e in EMPLOYEES if e["id"] == st.session_state.viewing_emp), None)
            if ve:
                upd = st.session_state.profile_updates.get(ve["id"], {})
                for k, v in upd.items(): ve[k] = v
                st.markdown("---")
                cx, _ = st.columns([1, 4])
                with cx:
                    if st.button("Close profile"):
                        st.session_state.viewing_emp = None
                        st.rerun()
                _full_profile(ve)

    # ── APPLICATIONS ──────────────────────────────────────────────────────────
    elif page.startswith("Applications"):
        page_header("Admin · Applications", "Applications", "Real-time submissions from your internal talent pool.")
        notifs = st.session_state.get("admin_notifs", [])
        if not notifs:
            st.info("No applications yet. Employees can apply via the Open Roles page.")
        else:
            for n in reversed(notifs):
                emp  = next((e for e in EMPLOYEES if e["id"] == n["emp_id"]), None)
                role = next((r for r in OPEN_ROLES if r["role_id"] == n["role_id"]), None)
                if not emp or not role: continue
                res = compute_full(emp, role)
                st.markdown(f"""
                <div class="card">
                  <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <div style="display:flex;gap:14px;align-items:center">
                      <div class="av av-sm">{initials(emp['name'])}</div>
                      <div>
                        <div style="font-size:15px;font-weight:600;color:#CCD6F6;font-family:'Inter',sans-serif">{emp['name']}</div>
                        <div style="font-size:12px;color:#7B8BB2">{emp['current_role']} applied for <b style="color:#CCD6F6">{role['title']}</b></div>
                        <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#4a5568">{n.get('time','')} · {emp['email']}</div>
                        <div style="margin-top:8px">{pills(res['matched'],'p-g')}</div>
                      </div>
                    </div>
                    <div style="text-align:right">
                      <div class="score-md" style="color:{score_color(n['score'])}">{n['score']}<span style="font-size:13px;color:#7B8BB2">/100</span></div>
                      <div style="font-size:11px;color:#22C55E;margin-top:4px">Saves {fmt_inr(res['budget']['saving'])}</div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

                ca, cb, cc = st.columns(3)
                with ca:
                    if st.button("AI recommendation", key=f"nr_{emp['id']}_{role['role_id']}"):
                        with st.spinner("Generating…"):
                            rec = gen_recommendation(res, role)
                        st.info(rec or "Add Groq API key in scoring.py for AI features.")
                with cb:
                    if st.button("Generate email", key=f"ne_{emp['id']}_{role['role_id']}"):
                        with st.spinner("Drafting email…"):
                            content = gen_email(emp, role, res)
                        subj, body = _parse_email(content, emp, role, res)
                        show_email(emp, subj, body)
                with cc:
                    if st.button("Quick message", key=f"nm_{emp['id']}_{role['role_id']}"):
                        with st.spinner("…"):
                            msg = gen_msg(emp, role, res)
                        st.info(msg or f"Hi {emp['name'].split()[0]}, your application for {role['title']} is under review — we'll be in touch soon.")

            if st.button("Clear all"):
                st.session_state.admin_notifs = []
                st.rerun()

    # ── SKILL GAP MATRIX ─────────────────────────────────────────────────────
    elif page == "Skill Gap Matrix":
        page_header("Admin · Insights", "Skill Gap Matrix", "Every employee × every required skill for a role.")
        rt   = st.selectbox("", [r["title"] for r in OPEN_ROLES], label_visibility="collapsed")
        role = next(r for r in OPEN_ROLES if r["title"] == rt)
        req  = role["required_skills"]

        all_res = score_all(role, 18)
        header  = "".join(f'<th style="padding:8px 10px;font-size:10px;color:#7B8BB2;font-family:JetBrains Mono,monospace;text-align:center;border-bottom:1px solid #1A2B6B;letter-spacing:0.05em">{s}</th>' for s in req)
        rows    = ""
        for res in all_res:
            emp  = res["emp"]
            ms   = set(m.lower() for m in res["matched"])
            as_  = set(a["skill"].lower() for a in res["adjacent"])
            cells = ""
            for skill in req:
                sl = skill.lower()
                if sl in ms:
                    cells += '<td style="text-align:center;padding:5px"><span style="background:rgba(34,197,94,0.12);color:#86efac;border:1px solid rgba(34,197,94,0.3);border-radius:4px;padding:2px 8px;font-size:10px;font-family:JetBrains Mono,monospace">yes</span></td>'
                elif sl in as_:
                    cells += '<td style="text-align:center;padding:5px"><span style="background:rgba(245,158,11,0.12);color:#fcd34d;border:1px solid rgba(245,158,11,0.3);border-radius:4px;padding:2px 8px;font-size:10px;font-family:JetBrains Mono,monospace">~near</span></td>'
                else:
                    cells += '<td style="text-align:center;padding:5px"><span style="background:#0B1437;color:#4a5568;border:1px solid #1A2B6B;border-radius:4px;padding:2px 8px;font-size:10px;font-family:JetBrains Mono,monospace">—</span></td>'
            rows += f'<tr><td style="padding:8px 14px;white-space:nowrap;border-bottom:1px solid #1A2B6B"><div style="font-size:12px;color:#CCD6F6;font-weight:500;font-family:Inter,sans-serif">{emp["name"]}</div><div style="font-size:10px;color:#7B8BB2">{emp["current_role"]}</div></td><td style="padding:6px 14px;text-align:center;border-bottom:1px solid #1A2B6B"><span style="font-family:JetBrains Mono,monospace;font-size:12px;color:{score_color(res["total"])};font-weight:600">{res["total"]}</span></td>{cells}</tr>'

        st.markdown(f"""
        <div class="card" style="overflow-x:auto;padding:0">
          <div style="padding:14px 20px 0;font-family:'JetBrains Mono',monospace;font-size:10px;color:#00C9A7;text-transform:uppercase;letter-spacing:0.1em">
            yes = has &nbsp;·&nbsp; ~near = learnable via adjacency &nbsp;·&nbsp; — = missing
          </div>
          <table style="width:100%;border-collapse:collapse;margin-top:10px">
            <thead>
              <tr>
                <th style="padding:8px 14px;font-size:10px;color:#7B8BB2;font-family:JetBrains Mono,monospace;text-align:left;border-bottom:1px solid #1A2B6B;letter-spacing:0.05em">Employee</th>
                <th style="padding:8px 14px;font-size:10px;color:#7B8BB2;font-family:JetBrains Mono,monospace;text-align:center;border-bottom:1px solid #1A2B6B">Score</th>
                {header}
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </div>""", unsafe_allow_html=True)

    # ── COMPARE ───────────────────────────────────────────────────────────────
    elif page == "Compare":
        page_header("Admin · Tools", "Compare Candidates", "Head-to-head for any open role.")
        rt   = st.selectbox("", [r["title"] for r in OPEN_ROLES], label_visibility="collapsed")
        role = next(r for r in OPEN_ROLES if r["title"] == rt)
        names = [e["name"] for e in EMPLOYEES]
        ca2, cb2 = st.columns(2)
        with ca2: na = st.selectbox("", names, 0, label_visibility="collapsed")
        with cb2: nb = st.selectbox("", names, 1, label_visibility="collapsed")

        if st.button("Compare", type="primary"):
            ea = next(e for e in EMPLOYEES if e["name"] == na)
            eb = next(e for e in EMPLOYEES if e["name"] == nb)
            sa = compute_full(ea, role)
            sb = compute_full(eb, role)
            winner = "A" if sa["total"] >= sb["total"] else "B"

            for col, e, s, lbl in [(ca2, ea, sa, "A"), (cb2, eb, sb, "B")]:
                with col:
                    w = winner == lbl
                    st.markdown(f"""
                    <div class="card" style="border-color:{'#00C9A7' if w else '#1A2B6B'}">
                      <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:{'#00C9A7' if w else '#7B8BB2'};margin-bottom:6px">{'WINNER' if w else 'CANDIDATE'} {lbl}</div>
                      <div style="font-size:18px;font-weight:600;color:#CCD6F6;font-family:'Inter',sans-serif">{e['name']}</div>
                      <div style="font-size:12px;color:#7B8BB2">{e['current_role']} · {e['department']}</div>
                      <div class="score-hero" style="color:{score_color(s['total'])};margin:10px 0 6px">{s['total']}<span style="font-size:18px;color:#7B8BB2">/100</span></div>
                      <div>{pills(s['matched'],'p-g')}{pills(s['missing'],'p-r')}</div>
                      <div style="font-size:12px;color:#22C55E;margin-top:10px">Saves {fmt_inr(s['budget']['saving'])}</div>
                    </div>""", unsafe_allow_html=True)

            trs = "".join(f'<tr><td style="color:#7B8BB2">{lbl}</td><td style="color:#CCD6F6">{a}</td><td style="color:#CCD6F6">{b}</td></tr>' for lbl,a,b in [
                ("Experience",   f"{ea['years_exp']}y",              f"{eb['years_exp']}y"),
                ("Tenure",       f"{ea['tenure_years']}y",           f"{eb['tenure_years']}y"),
                ("Salary",       fmt_inr(ea["current_salary"]),      fmt_inr(eb["current_salary"])),
                ("Offer",        fmt_inr(sa["budget"]["offer"]),     fmt_inr(sb["budget"]["offer"])),
                ("Saving",       fmt_inr(sa["budget"]["saving"]),    fmt_inr(sb["budget"]["saving"])),
                ("Matched",      f'{len(sa["matched"])}/{len(role["required_skills"])}', f'{len(sb["matched"])}/{len(role["required_skills"])}'),
                ("Commits",      ea["github_data"].get("commits_6mo",0), eb["github_data"].get("commits_6mo",0)),
                ("OSS PRs",      ea["github_data"].get("open_source_prs",0), eb["github_data"].get("open_source_prs",0)),
                ("Time-to-prod", f'{sa["ttp"]}w',                   f'{sb["ttp"]}w'),
            ])
            st.markdown(f'<div class="card" style="margin-top:14px"><table class="tbl"><tr><th>Metric</th><th>{ea["name"].split()[0]}</th><th>{eb["name"].split()[0]}</th></tr>{trs}</table></div>', unsafe_allow_html=True)

            with st.spinner("AI analysis…"):
                analysis = llm_call(
                    f"Compare {ea['name']} (score {sa['total']}, matched {sa['matched']}) vs "
                    f"{eb['name']} (score {sb['total']}, matched {sb['matched']}) for {role['title']}. "
                    "2-3 sentences on tradeoffs and a clear recommendation."
                )
            st.info(analysis or "Add Groq API key in scoring.py for AI analysis.")

    footer()


# ═══════════════════════════════════════════════════════════════════════════════
# SHARED HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _parse_email(content, emp, role, res):
    """Parse Subject / body from LLM output, falling back to a template."""
    if content:
        lines   = content.split("\n")
        subject = next((l.replace("Subject:", "").strip() for l in lines if l.startswith("Subject:")),
                       f"An internal opportunity — {role['title']}")
        body    = "\n".join(l for l in lines if not l.startswith("Subject:")).strip()
        return subject, body
    # fallback
    ts = TALENT_SENDER
    subject = f"An internal opportunity for you — {role['title']}"
    body    = f"""Hi {emp['name'].split()[0]},

I hope you're doing well. I'm reaching out from the talent team — your profile stood out for our open {role['title']} role in {role['department']}.

You match {len(res['matched'])}/{len(role['required_skills'])} required skills, including {', '.join(res['matched'][:3])}.{"" if not res['missing'] else " Any gaps are small and learnable."} From a company perspective, hiring you internally saves ₹{res['budget']['saving']//100000:.1f}L vs an external hire.

Would you be open to a quick conversation this week?

Warm regards,
{ts['name']}
{ts['role']}, {ts['company']}
{ts['email']}"""
    return subject, body


def _result_card(res, rank, role):
    emp    = res["emp"]
    b      = res["breakdown"]
    budget = res["budget"]
    gh     = emp.get("github_data", {})
    ranks  = ["1st","2nd","3rd","4th","5th","6th","7th","8th","9th","10th"]

    # upskill links — inline, clickable
    up_html = ""
    shown   = set()
    for skill in res["missing"] + [a["skill"] for a in res["adjacent"]]:
        if skill in shown or skill not in COURSES: continue
        shown.add(skill)
        cr   = COURSES[skill]
        cost = "Free" if cr["cost"] == 0 else f"₹{cr['cost']}"
        up_html += (f'<div style="font-size:12px;color:#7B8BB2;margin:3px 0">'
                    f'<b style="color:#CCD6F6">{skill}</b> — '
                    f'<a href="{cr["url"]}" target="_blank" style="color:#00C9A7">{cr["course"]}</a>'
                    f' · {cr["platform"]} · {cr["weeks"]}w · {cost}</div>')

    st.markdown(f"""
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <div style="display:flex;gap:14px;align-items:center">
          <div class="av av-sm">{initials(emp['name'])}</div>
          <div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#00C9A7;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:3px">{ranks[rank]}</div>
            <div style="font-size:17px;font-weight:600;color:#CCD6F6;font-family:'Inter',sans-serif">{emp['name']}</div>
            <div style="font-size:12px;color:#7B8BB2">{emp['current_role']} · {emp['department']} · {emp['years_exp']}y · {emp['email']}</div>
          </div>
        </div>
        <div style="text-align:right">
          <div class="score-lg" style="color:{score_color(res['total'])}">{res['total']}<span style="font-size:14px;color:#7B8BB2">/100</span></div>
          <div style="font-family:'JetBrains Mono',monospace;font-size:9px;color:#7B8BB2">sk {b['skill']} · sem {b['semantic']} · gh {b['github']}</div>
        </div>
      </div>
      <hr>
      <div>{pills(res['matched'],'p-g')}{pills(res['missing'],'p-r')}{''.join(f'<span class="pill p-a">{a["skill"]} via {a["bridge"]}</span>' for a in res['adjacent'])}</div>
      <div style="font-size:12px;color:#7B8BB2;margin-top:8px">GitHub: {gh.get('commits_6mo',0)} commits · {gh.get('open_source_prs',0)} OSS PRs · {res['gh_reason']}</div>
      <div class="ss">
        <div class="si"><div class="sn">{fmt_inr(budget['offer'])}</div><div class="sl">Offer {"ok" if budget['within'] else "!"}</div></div>
        <div class="si"><div class="sn" style="color:#22C55E">{fmt_inr(budget['saving'])}</div><div class="sl">Saving</div></div>
        <div class="si"><div class="sn">{res['ttp']}w</div><div class="sl">Time-to-prod</div></div>
      </div>
      {f'<div style="margin-top:10px">{up_html}</div>' if up_html else ""}
      {f'<div class="badge bg-a" style="margin-top:8px;display:inline-block">{res["diversity"]}</div>' if res["diversity"] else ""}
      <div style="margin-top:8px"><span class="badge bg-g">Bias check passed</span></div>
    </div>""", unsafe_allow_html=True)

    ca, cb, cc = st.columns(3)
    with ca:
        if st.button("AI recommendation", key=f"rec_{emp['id']}_{rank}"):
            with st.spinner("…"):
                rec = gen_recommendation(res, role)
            st.info(rec or "Add Groq API key in scoring.py for AI features.")
    with cb:
        if st.button(f"Email {emp['name'].split()[0]}", key=f"email_{emp['id']}_{rank}"):
            with st.spinner("Drafting email…"):
                content = gen_email(emp, role, res)
            subj, body = _parse_email(content, emp, role, res)
            show_email(emp, subj, body)
    with cc:
        if st.button("Quick message", key=f"msg_{emp['id']}_{rank}"):
            with st.spinner("…"):
                msg = gen_msg(emp, role, res)
            st.info(msg or f"Hi {emp['name'].split()[0]}, we think you'd be a great fit for {role['title']} — worth a conversation?")


def _full_profile(emp):
    gh  = emp.get("github_data", {})
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
          <span class="slabel">Skills</span>
          <div>{pills(emp.get('skills',[]),'p-b')}</div>
          <span class="slabel">Certifications</span>
          {certs_html or '<div style="font-size:12px;color:#4a5568">None listed</div>'}
          <hr>
          <div style="font-size:13px;color:#7B8BB2;margin-bottom:8px">{emp['email']}</div>
          <div style="display:flex;gap:16px">
            <a href="{emp.get('github_url','')}" target="_blank">GitHub</a>
            <a href="{emp.get('linkedin','')}" target="_blank">LinkedIn</a>
          </div>
        </div>
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
        st.markdown('<div style="font-size:22px;font-family:Libre Baskerville,serif;font-weight:700;color:#F0F4FF;margin-bottom:16px">Match scores</div>', unsafe_allow_html=True)
        for role in OPEN_ROLES:
            res = compute_full(emp, role)
            st.markdown(f"""
            <div class="card" style="margin-bottom:12px">
              <div style="display:flex;justify-content:space-between">
                <div>
                  <div style="font-size:16px;font-family:'Libre Baskerville',serif;font-weight:700;color:#F0F4FF">{role['title']}</div>
                  <div style="font-family:'JetBrains Mono',monospace;font-size:10px;color:#00C9A7;text-transform:uppercase;letter-spacing:0.08em">{role['department']}</div>
                </div>
                <div style="text-align:right">
                  <div class="score-md" style="color:{score_color(res['total'])}">{res['total']}<span style="font-size:13px;color:#7B8BB2">/100</span></div>
                  <div style="font-size:11px;color:#22C55E">saves {fmt_inr(res['budget']['saving'])}</div>
                </div>
              </div>
              <div style="margin-top:10px">{pills(res['matched'],'p-g')}{pills(res['missing'],'p-r')}{''.join(f'<span class="pill p-a">{a["skill"]} via {a["bridge"]}</span>' for a in res['adjacent'])}</div>
              {f'<div class="badge bg-a" style="margin-top:8px;display:inline-block">{res["diversity"]}</div>' if res["diversity"] else ""}
            </div>""", unsafe_allow_html=True)

        st.markdown('<div style="font-size:18px;font-family:Libre Baskerville,serif;font-weight:700;color:#F0F4FF;margin:20px 0 12px">Send opportunity email</div>', unsafe_allow_html=True)
        re_sel = st.selectbox("", [r["title"] for r in OPEN_ROLES], key=f"er_{emp['id']}", label_visibility="collapsed")
        ro = next(r for r in OPEN_ROLES if r["title"] == re_sel)
        if st.button("Generate & preview email", key=f"gep_{emp['id']}", type="primary"):
            with st.spinner("Drafting…"):
                res2    = compute_full(emp, ro)
                content = gen_email(emp, ro, res2)
            subj, body = _parse_email(content, emp, ro, res2)
            show_email(emp, subj, body)
