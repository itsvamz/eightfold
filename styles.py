import streamlit as st

# ── palette ──────────────────────────────────────────────────────────────────
TEAL   = "#00C9A7"
NAVY   = "#0B1437"
NAVY2  = "#0F1D4E"
CARD   = "#0D1842"
BORDER = "#1A2B6B"
WHITE  = "#F0F4FF"
MUTED  = "#7B8BB2"
GREEN  = "#22C55E"
AMBER  = "#F59E0B"
RED    = "#EF4444"
PURPLE = "#A78BFA"

def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --teal:#00C9A7; --teal-dim:rgba(0,201,167,0.12); --teal-border:rgba(0,201,167,0.3);
  --navy:#0B1437; --navy2:#0F1D4E; --card:#0D1842; --border:#1A2B6B;
  --white:#F0F4FF; --muted:#7B8BB2; --text:#CCD6F6;
  --green:#22C55E; --green-dim:rgba(34,197,94,0.12); --green-border:rgba(34,197,94,0.3);
  --amber:#F59E0B; --amber-dim:rgba(245,158,11,0.12); --amber-border:rgba(245,158,11,0.3);
  --red:#EF4444;   --red-dim:rgba(239,68,68,0.12);    --red-border:rgba(239,68,68,0.3);
  --purple:#A78BFA;--purple-dim:rgba(167,139,250,0.12);
}

/* ── base ── */
html,body,[class*="css"],.stApp { background:var(--navy) !important; color:var(--text) !important; }
* { box-sizing:border-box; }
.block-container { padding:0 2.5rem 4rem !important; max-width:1280px; }
a { color:var(--teal) !important; text-decoration:none !important; }
a:hover { opacity:0.8 !important; }
hr { border:none !important; border-top:1px solid var(--border) !important; margin:16px 0 !important; }

/* ── sidebar ── */
[data-testid="stSidebar"] { background:var(--navy2) !important; border-right:1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color:var(--text) !important; }
[data-testid="stSidebar"] .stRadio label { font-family:'Inter',sans-serif !important; font-size:13px !important; color:var(--muted) !important; }
[data-testid="stSidebar"] .stRadio label:hover { color:var(--teal) !important; }
[data-testid="stSidebar"] [data-testid="stRadioLabel"] { display:none; }

/* ── typography ── */
h1,h2,h3,h4 { font-family:'Libre Baskerville',Georgia,serif !important; font-weight:700 !important; color:var(--white) !important; letter-spacing:-0.02em; }
p,div,span,label,li { font-family:'Inter',sans-serif !important; }
code,pre,.mono { font-family:'JetBrains Mono',monospace !important; }

/* ── streamlit overrides ── */
.stButton>button { font-family:'Inter',sans-serif !important; font-weight:600 !important; font-size:13px !important; border-radius:8px !important; transition:all 0.2s !important; letter-spacing:0.01em !important; }
.stButton>button[kind="primary"] { background:var(--teal) !important; color:var(--navy) !important; border:none !important; padding:10px 22px !important; }
.stButton>button[kind="primary"]:hover { box-shadow:0 6px 20px rgba(0,201,167,0.4) !important; transform:translateY(-1px) !important; }
.stButton>button:not([kind="primary"]) { background:transparent !important; color:var(--text) !important; border:1px solid var(--border) !important; }
.stButton>button:not([kind="primary"]):hover { border-color:var(--teal) !important; color:var(--teal) !important; }
.stTextInput>div>div>input,.stTextArea>div>div>textarea,.stSelectbox>div>div,.stNumberInput>div>div>input { background:var(--card) !important; border:1px solid var(--border) !important; border-radius:8px !important; color:var(--white) !important; font-family:'Inter',sans-serif !important; }
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus { border-color:var(--teal) !important; box-shadow:0 0 0 3px var(--teal-dim) !important; }
.stSelectbox>div>div { color:var(--text) !important; }
.stRadio>div { gap:6px !important; }
.stCheckbox label { color:var(--muted) !important; font-family:'Inter',sans-serif !important; font-size:13px !important; }
.stSlider [data-baseweb="slider"] div[role="slider"] { background:var(--teal) !important; }
[data-testid="stMetric"] { background:var(--card) !important; border:1px solid var(--border) !important; border-radius:12px !important; padding:18px 20px !important; }
[data-testid="stMetricLabel"] { font-family:'JetBrains Mono',monospace !important; font-size:10px !important; color:var(--muted) !important; text-transform:uppercase; letter-spacing:0.1em; }
[data-testid="stMetricValue"] { font-family:'Libre Baskerville',serif !important; font-size:28px !important; font-weight:700 !important; color:var(--white) !important; }
[data-testid="stMetricDelta"] { color:var(--teal) !important; }
.stExpander { background:var(--card) !important; border:1px solid var(--border) !important; border-radius:12px !important; }
.stExpander summary { font-family:'Inter',sans-serif !important; color:var(--text) !important; }
.stSuccess { background:var(--green-dim) !important; border:1px solid var(--green-border) !important; border-radius:10px !important; color:#86efac !important; }
.stInfo    { background:var(--teal-dim) !important; border:1px solid var(--teal-border) !important; border-radius:10px !important; color:#5eead4 !important; }
.stWarning { background:var(--amber-dim) !important; border:1px solid var(--amber-border) !important; border-radius:10px !important; color:#fcd34d !important; }
.stError   { background:var(--red-dim) !important; border:1px solid var(--red-border) !important; border-radius:10px !important; color:#fca5a5 !important; }

/* ── topbar ── */
.topbar { background:var(--navy2); border-bottom:1px solid var(--border); padding:0 2.5rem; margin:0 -2.5rem 2rem; display:flex; align-items:center; justify-content:space-between; height:56px; }
.topbar-logo { font-family:'Libre Baskerville',Georgia,serif; font-size:22px; font-weight:700; color:var(--white); letter-spacing:-0.5px; }
.topbar-logo span { color:var(--teal); }
.topbar-right { font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--muted); text-transform:uppercase; letter-spacing:0.1em; }

/* ── footer ── */
.footer { margin:3rem -2.5rem -4rem; padding:20px 2.5rem; background:var(--navy2); border-top:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; }
.footer-left { font-family:'Libre Baskerville',serif; font-size:16px; font-weight:700; color:var(--white); }
.footer-left span { color:var(--teal); }
.footer-right { font-size:11px; color:var(--muted); font-family:'JetBrains Mono',monospace; }

/* ── page header ── */
.ph { padding:24px 0; border-bottom:1px solid var(--border); margin-bottom:28px; }
.ph-eyebrow { font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--teal); text-transform:uppercase; letter-spacing:0.2em; margin-bottom:8px; }
.ph-title { font-family:'Libre Baskerville',Georgia,serif; font-size:34px; font-weight:700; color:var(--white); letter-spacing:-1px; line-height:1.1; }
.ph-sub { font-size:14px; color:var(--muted); margin-top:6px; font-family:'Inter',sans-serif; }

/* ── section label ── */
.slabel { font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--teal); text-transform:uppercase; letter-spacing:0.18em; margin:16px 0 8px; display:block; }

/* ── cards ── */
.card { background:var(--card); border:1px solid var(--border); border-radius:16px; padding:22px 24px; margin-bottom:14px; transition:border-color 0.2s; }
.card:hover { border-color:rgba(0,201,167,0.35); }
.card-sm { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:14px 16px; margin-bottom:8px; }
.login-card { background:var(--card); border:1px solid var(--border); border-radius:20px; padding:36px 30px; box-shadow:0 24px 64px rgba(0,0,0,0.6); }

/* ── score ── */
.score-hero { font-family:'Libre Baskerville',serif; font-size:56px; font-weight:700; line-height:1; letter-spacing:-2px; }
.score-lg   { font-family:'Libre Baskerville',serif; font-size:38px; font-weight:700; line-height:1; }
.score-md   { font-family:'Libre Baskerville',serif; font-size:26px; font-weight:700; line-height:1; }
.score-mono { font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--muted); margin-top:4px; }

/* ── pills ── */
.pill { display:inline-block; padding:4px 12px; border-radius:20px; font-family:'JetBrains Mono',monospace; font-size:11px; margin:2px; }
.p-g { background:var(--green-dim); color:#86efac; border:1px solid var(--green-border); }
.p-r { background:var(--red-dim);   color:#fca5a5; border:1px solid var(--red-border); }
.p-a { background:var(--amber-dim); color:#fcd34d; border:1px solid var(--amber-border); }
.p-b { background:var(--teal-dim);  color:var(--teal); border:1px solid var(--teal-border); }
.p-p { background:var(--purple-dim);color:#c4b5fd; border:1px solid rgba(167,139,250,0.3); }

/* ── stat strip ── */
.ss { display:flex; gap:10px; margin:14px 0; flex-wrap:wrap; }
.si { background:var(--navy); border:1px solid var(--border); border-radius:10px; padding:12px 16px; flex:1; min-width:72px; text-align:center; }
.sn { font-family:'Libre Baskerville',serif; font-size:20px; font-weight:700; color:var(--white); line-height:1; }
.sl { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--muted); margin-top:3px; text-transform:uppercase; letter-spacing:0.08em; }

/* ── avatar ── */
.av { display:flex; align-items:center; justify-content:center; border-radius:50%; font-weight:800; background:linear-gradient(135deg,var(--navy2),var(--teal)); color:var(--white); flex-shrink:0; font-family:'Libre Baskerville',serif; }
.av-lg { width:68px; height:68px; font-size:22px; }
.av-sm { width:40px; height:40px; font-size:14px; }

/* ── badge ── */
.badge { display:inline-block; border-radius:6px; padding:3px 10px; font-family:'JetBrains Mono',monospace; font-size:10px; }
.bg-g { background:var(--green-dim); color:#86efac; border:1px solid var(--green-border); }
.bg-r { background:var(--red-dim);   color:#fca5a5; border:1px solid var(--red-border); }
.bg-a { background:var(--amber-dim); color:#fcd34d; border:1px solid var(--amber-border); }
.bg-b { background:var(--teal-dim);  color:var(--teal); border:1px solid var(--teal-border); }
.bg-p { background:var(--purple-dim);color:#c4b5fd; border:1px solid rgba(167,139,250,0.3); }

/* ── bars ── */
.bar-r { margin:7px 0; }
.bar-top { display:flex; justify-content:space-between; font-size:12px; color:var(--muted); margin-bottom:4px; font-family:'Inter',sans-serif; }
.bar-bg  { background:var(--navy); border-radius:4px; height:5px; border:1px solid var(--border); }
.bar-fill { height:5px; border-radius:4px; transition:width 0.5s ease; }

/* ── notification ── */
.notif { background:var(--card); border:1px solid var(--border); border-left:3px solid var(--teal); border-radius:0 12px 12px 0; padding:14px 18px; margin-bottom:10px; }
.notif-title { font-size:14px; font-weight:600; color:var(--white); font-family:'Inter',sans-serif; }
.notif-sub   { font-size:12px; color:var(--muted); margin-top:3px; font-family:'Inter',sans-serif; }

/* ── course card ── */
.cc { background:var(--navy); border:1px solid var(--border); border-radius:12px; padding:16px 18px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; gap:16px; transition:border-color 0.15s; }
.cc:hover { border-color:var(--teal-border); }
.cc-title { font-size:14px; font-weight:600; color:var(--white); font-family:'Inter',sans-serif; }
.cc-meta  { font-size:12px; color:var(--muted); margin-top:3px; font-family:'Inter',sans-serif; }
.tag-free { background:var(--green-dim); color:#86efac; border:1px solid var(--green-border); border-radius:6px; padding:3px 10px; font-size:11px; white-space:nowrap; font-family:'JetBrains Mono',monospace; }
.tag-paid { background:var(--navy); border:1px solid var(--border); border-radius:6px; padding:3px 10px; font-size:11px; color:var(--muted); white-space:nowrap; font-family:'JetBrains Mono',monospace; }
.open-btn { background:var(--navy2); color:var(--teal) !important; border:1px solid var(--border); padding:6px 16px; border-radius:6px; font-size:12px; font-weight:600; white-space:nowrap; font-family:'Inter',sans-serif; }
.open-btn:hover { border-color:var(--teal) !important; background:var(--teal-dim) !important; }

/* ── email preview ── */
.email-wrap { background:var(--navy); border:1px solid var(--border); border-radius:14px; overflow:hidden; margin-top:12px; }
.email-hdr { background:var(--card); border-bottom:1px solid var(--border); padding:16px 20px; }
.ef-lbl { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--teal); text-transform:uppercase; letter-spacing:0.15em; display:block; margin-bottom:2px; }
.ef-val { font-size:13px; color:var(--text); font-family:'Inter',sans-serif; }
.email-body { padding:20px; font-size:13px; color:var(--muted); line-height:1.8; white-space:pre-wrap; font-family:'Inter',sans-serif; }
.mailto-btn { display:inline-block; margin-top:12px; background:var(--teal); color:var(--navy) !important; font-weight:700; font-size:13px; padding:10px 22px; border-radius:8px; font-family:'Inter',sans-serif; }
.mailto-btn:hover { opacity:0.9 !important; }

/* ── applied banner ── */
.app-banner { background:var(--green-dim); border:1px solid var(--green-border); border-radius:10px; padding:12px 18px; font-size:13px; color:#86efac; display:flex; align-items:center; gap:10px; margin-top:8px; font-family:'Inter',sans-serif; }

/* ── table ── */
.tbl { width:100%; border-collapse:collapse; font-size:13px; font-family:'Inter',sans-serif; }
.tbl th { background:var(--navy); color:var(--muted); padding:10px 14px; text-align:left; border-bottom:1px solid var(--border); font-family:'JetBrains Mono',monospace; font-size:9px; letter-spacing:0.1em; font-weight:400; }
.tbl td { padding:10px 14px; border-bottom:1px solid var(--border); color:var(--text); }
.tbl tr:hover td { background:rgba(0,201,167,0.04); }

/* ── profile ── */
.prof-name { font-family:'Libre Baskerville',serif; font-size:28px; font-weight:700; color:var(--white); letter-spacing:-0.5px; }
.prof-role { font-size:13px; color:var(--muted); margin-top:4px; font-family:'Inter',sans-serif; }
.prof-detail { font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--teal); margin-top:6px; text-transform:uppercase; letter-spacing:0.1em; }

/* ── sidebar avatar & name ── */
.sb-av { width:52px; height:52px; border-radius:50%; background:linear-gradient(135deg,var(--navy2),var(--teal)); display:flex; align-items:center; justify-content:center; font-family:'Libre Baskerville',serif; font-size:18px; font-weight:700; color:var(--white); margin:0 auto 10px; }
.sb-name { font-family:'Libre Baskerville',serif; font-size:18px; font-weight:700; color:var(--white); text-align:center; }
.sb-role { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--teal); text-transform:uppercase; letter-spacing:0.1em; text-align:center; margin-top:3px; }

/* ── login wordmark ── */
.wm { font-family:'Libre Baskerville',Georgia,serif; font-size:44px; font-weight:700; letter-spacing:-2px; line-height:1; background:linear-gradient(135deg,var(--white) 0%,var(--teal) 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.wm-sub { font-family:'JetBrains Mono',monospace; font-size:11px; color:var(--muted); letter-spacing:0.15em; text-transform:uppercase; margin-top:8px; }

/* ── teal glow rule ── */
.tglow { height:2px; background:linear-gradient(90deg,transparent,var(--teal),transparent); margin:0 -2.5rem 2rem; }

/* ── metric card ── */
.mc { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px 18px; text-align:center; }
.mc-num { font-family:'Libre Baskerville',serif; font-size:28px; font-weight:700; color:var(--white); line-height:1; }
.mc-lbl { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--muted); margin-top:4px; text-transform:uppercase; letter-spacing:0.08em; }
.mc-delta { font-size:11px; color:var(--teal); margin-top:3px; font-family:'Inter',sans-serif; }
</style>
""", unsafe_allow_html=True)


# ── helpers ───────────────────────────────────────────────────────────────────
def fmt_inr(n): return f"₹{n/100000:.1f}L"

def score_color(s):
    if s >= 75: return "#22C55E"
    if s >= 50: return "#F59E0B"
    return "#EF4444"

def bar_html(label, value, max_val, color="#00C9A7", suffix=""):
    pct = round(value / max(max_val, 1) * 100)
    return (f'<div class="bar-r">'
            f'<div class="bar-top"><span>{label}</span><span style="color:{color}">{value}{suffix}</span></div>'
            f'<div class="bar-bg"><div class="bar-fill" style="width:{pct}%;background:{color}"></div></div>'
            f'</div>')

def initials(name):
    p = name.split()
    return (p[0][0] + p[-1][0]).upper()

def pills(items, cls):
    return " ".join(f'<span class="pill {cls}">{i}</span>' for i in items)

def topbar(right_text=""):
    st.markdown(f"""
    <div class="topbar">
      <div class="topbar-logo">Talent<span>IQ</span></div>
      <div class="topbar-right">{right_text}</div>
    </div>
    """, unsafe_allow_html=True)

def footer():
    st.markdown("""
    <div class="footer">
      <div class="footer-left">Talent<span>IQ</span></div>
      <div class="footer-right">Techkriti '26 × Eightfold AI &nbsp;·&nbsp; Internal Talent Intelligence</div>
    </div>
    """, unsafe_allow_html=True)

def page_header(eyebrow, title, sub=""):
    st.markdown(f"""
    <div class="ph">
      <div class="ph-eyebrow">{eyebrow}</div>
      <div class="ph-title">{title}</div>
      {"<div class='ph-sub'>"+sub+"</div>" if sub else ""}
    </div>
    """, unsafe_allow_html=True)

def show_email(emp, subject, body):
    import urllib.parse
    mailto = f"mailto:{emp['email']}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body[:1500])}"
    st.markdown(f"""
    <div class="email-wrap">
      <div class="email-hdr">
        <div style="margin-bottom:10px"><span class="ef-lbl">From</span><div class="ef-val">Vamika Mendiratta &lt;vamika.mendiratta1304@gmail.com&gt;</div></div>
        <div style="margin-bottom:10px"><span class="ef-lbl">To</span><div class="ef-val">{emp['name']} &lt;{emp['email']}&gt;</div></div>
        <div><span class="ef-lbl">Subject</span><div class="ef-val">{subject}</div></div>
      </div>
      <div class="email-body">{body}</div>
    </div>
    <a href="{mailto}" target="_blank" class="mailto-btn">Open in email client</a>
    """, unsafe_allow_html=True)
