import re
from data import SKILL_ADJACENCY, LEARNING_WEEKS, COURSES, EMPLOYEES, OPEN_ROLES

GROQ_API_KEY = ""   # paste your Groq key here

TALENT_SENDER = {
    "name":    "Vamika Mendiratta",
    "role":    "Talent Intelligence Lead",
    "email":   "vamika.mendiratta1304@gmail.com",
    "company": "TalentIQ × Eightfold AI",
}

# ── scoring ───────────────────────────────────────────────────────────────────
def get_bridge(emp_skills, need):
    for edge in SKILL_ADJACENCY:
        f, t = edge["from"].lower(), edge["to"].lower()
        for s in emp_skills:
            sl = s.lower()
            if (f == sl and t == need.lower()) or (t == sl and f == need.lower()):
                return {"bridge": s, "distance": edge["distance"], "reason": edge["reason"]}
    return None

def skill_score(emp_skills, required, weights):
    emp_lower = [s.lower() for s in emp_skills]
    matched, missing, adjacent = [], [], []
    total_w = sum(weights.get(s, 1) for s in required)
    earned = 0
    for skill in required:
        w = weights.get(skill, 1)
        if skill.lower() in emp_lower:
            matched.append(skill); earned += w
        else:
            bridge = get_bridge(emp_skills, skill)
            if bridge:
                adjacent.append({"skill": skill, **bridge})
                earned += w * 0.5
            else:
                missing.append(skill)
    return round(earned / total_w * 70, 1) if total_w else 0, matched, missing, adjacent

def emb_score(emp_skills, jd):
    jd_words  = set(re.sub(r'[^\w\s]', '', jd.lower()).split())
    emp_words = set(re.sub(r'[^\w\s]', '', " ".join(emp_skills).lower()).split())
    overlap   = len(jd_words & emp_words)
    return round(min(overlap / max(len(jd_words), 1) * 30, 15), 1)

def gh_boost(emp, required):
    gh = emp.get("github_data", {})
    if not gh: return 0.0, "No GitHub data"
    boost, parts = 0.0, []
    c = gh.get("commits_6mo", 0)
    if   c >= 400: boost += 6; parts.append(f"{c} commits/6mo")
    elif c >= 200: boost += 4; parts.append(f"{c} commits/6mo")
    elif c >= 100: boost += 2; parts.append(f"{c} commits/6mo")
    langs = [l.lower() for l in gh.get("top_languages", [])]
    rel   = [s for s in required if s.lower() in langs]
    if rel: boost += len(rel) * 2; parts.append(f"active in {', '.join(rel)}")
    prs = gh.get("open_source_prs", 0)
    if   prs >= 10: boost += 3; parts.append(f"{prs} OSS PRs")
    elif prs >= 3:  boost += 1; parts.append(f"{prs} OSS PRs")
    return round(min(boost, 15), 1), " · ".join(parts) or "low activity"

def budget_calc(emp, role):
    offer  = min(max(emp["current_salary"] * 1.15, role["budget_min"]), role["budget_max"])
    saving = role["external_hire_cost"] - offer
    return {"offer": round(offer), "saving": round(saving),
            "within": role["budget_min"] <= offer <= role["budget_max"]}

def diversity_flag(emp, role):
    team = role["team_composition"]
    total, female = team["total"], team["female"]
    pct = round(female / total * 100)
    if emp.get("gender") == "F" and pct < 30:
        new_pct = round((female + 1) / (total + 1) * 100)
        return f"Team is {pct}% women. Hiring improves to {new_pct}%."
    return ""

def compute_full(emp, role):
    skills = emp.get("skills", [])
    base, matched, missing, adjacent = skill_score(skills, role["required_skills"], role["skill_weights"])
    emb   = emb_score(skills, role["description"])
    boost, gh_reason = gh_boost(emp, role["required_skills"])
    total  = round(min(base + emb + boost, 100), 1)
    budget = budget_calc(emp, role)
    # bias check — score without demographics
    anon   = {k: v for k, v in emp.items() if k not in ("name","gender","university","github","github_data")}
    anon["github_data"] = {}
    a_base, _, _, _ = skill_score(skills, role["required_skills"], role["skill_weights"])
    a_emb  = emb_score(skills, role["description"])
    anon_total = round(min(a_base + a_emb, 100), 1)
    ttp = (sum(LEARNING_WEEKS.get(a["distance"], 12) for a in adjacent)
           + sum(COURSES[s]["weeks"] for s in missing if s in COURSES))
    return {
        "emp": emp, "total": total,
        "breakdown": {"skill": base, "semantic": emb, "github": boost},
        "matched": matched, "missing": missing, "adjacent": adjacent,
        "gh_reason": gh_reason, "budget": budget,
        "bias_passed": abs(total - anon_total) < 0.1,
        "diversity": diversity_flag(emp, role),
        "ttp": ttp,
    }

def score_all(role, top_n=18):
    results = [compute_full(emp, role) for emp in EMPLOYEES]
    results.sort(key=lambda x: x["total"], reverse=True)
    return results[:top_n]

def get_upskill_courses(missing, adjacent):
    recs, seen = [], set()
    for s in missing + [a["skill"] for a in adjacent]:
        if s not in seen and s in COURSES:
            seen.add(s); recs.append({"skill": s, **COURSES[s]})
    return recs[:5]

# ── LLM ───────────────────────────────────────────────────────────────────────
def llm_call(prompt, max_tokens=400):
    if not GROQ_API_KEY:
        return None
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"(LLM error: {e})"

def gen_email(emp, role, result):
    ts = TALENT_SENDER
    prompt = f"""Write a warm, professional internal job opportunity email.

From: {ts['name']} ({ts['role']}) <{ts['email']}>
To: {emp['name']} ({emp['current_role']}, {emp['department']}) <{emp['email']}>
Role: {role['title']}, {role['department']}

Data:
- Match score: {result['total']}/100
- Matched skills: {', '.join(result['matched'])}
- Missing skills: {', '.join(result['missing'])} (learnable)
- Budget saving vs external hire: ₹{result['budget']['saving']:,}

Write exactly:
Line 1: Subject: [subject]
Blank line
Body: 3-4 short paragraphs. Warm, encouraging, specific. Sign as {ts['name']}, {ts['role']}.
No meta-commentary, just the email."""
    content = llm_call(prompt, 500)
    if not content:
        # fallback template
        subject = f"An internal opportunity for you — {role['title']}"
        body = f"""Hi {emp['name'].split()[0]},

I hope you're doing well. I wanted to reach out from the talent team about an exciting internal opening that matches your profile really well.

We have an open {role['title']} position in {role['department']}, and your experience stood out. You already match {len(result['matched'])} of the {len(role['required_skills'])} required skills, including {', '.join(result['matched'][:3])}.{"" if not result['missing'] else " Any gaps are small and very learnable."}

This kind of internal move tends to come with a competitive uplift, and from a company perspective it saves ₹{result['budget']['saving']//100000:.1f}L vs hiring externally — so everyone wins.

Would you be open to a quick chat this week? Just reply here and we can find a time.

Warm regards,
{ts['name']}
{ts['role']}, {ts['company']}
{ts['email']}"""
        return f"Subject: {subject}\n\n{body}"
    return content

def gen_recommendation(result, role):
    emp = result["emp"]
    return llm_call(
        f"Write a 2-3 sentence hiring recommendation for {emp['name']} for {role['title']}. "
        f"Score {result['total']}/100. Matched: {result['matched']}. Missing: {result['missing']}. "
        f"GitHub: {result['gh_reason']}. Saves {fmt_inr(result['budget']['saving'])} vs external hire. Be specific.",
        200
    )

def gen_msg(emp, role, result):
    return llm_call(
        f"Write a 2-sentence warm, casual internal Slack message to {emp['name'].split()[0]} "
        f"about the open {role['title']} role. They match {len(result['matched'])}/{len(role['required_skills'])} "
        f"skills. No buzzwords, no emojis, professional.",
        120
    )

def fmt_inr(n):
    return f"₹{n/100000:.1f}L"
