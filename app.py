import streamlit as st

st.set_page_config(
    page_title="TalentIQ × Eightfold AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# hide default streamlit chrome that shows "app · admin · employee" at top
st.markdown("""
<style>
  [data-testid="stSidebarNav"] { display:none !important; }
  #MainMenu { display:none !important; }
  header[data-testid="stHeader"] { display:none !important; }
  footer { display:none !important; }
  .stDeployButton { display:none !important; }
</style>
""", unsafe_allow_html=True)

def _init():
    defaults = {
        "role": None,
        "user_id": None,
        "applications": {},      # {emp_id: [role_id, ...]}
        "admin_notifs": [],      # list of application events
        "profile_updates": {},   # {emp_id: {field: value}}
        "viewing_emp": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

from data import EMPLOYEES
from styles import inject_css, topbar, footer
inject_css()

# ── LOGIN ─────────────────────────────────────────────────────────────────────
if st.session_state.role is None:
    # minimal header
    st.markdown('<div style="text-align:center;padding:56px 0 36px">', unsafe_allow_html=True)
    st.markdown('<div class="wm">TalentIQ</div>', unsafe_allow_html=True)
    st.markdown('<div class="wm-sub">Internal Talent Intelligence &nbsp;·&nbsp; Techkriti × Eightfold AI</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    _, col, _ = st.columns([1, 1, 1])
    with col:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        mode = st.radio("", ["Employee", "Admin"], horizontal=True, label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        if mode == "Employee":
            chosen = st.selectbox("", [e["name"] for e in EMPLOYEES], label_visibility="collapsed")
            if st.button("Continue", type="primary", use_container_width=True):
                emp = next(e for e in EMPLOYEES if e["name"] == chosen)
                st.session_state.role    = "employee"
                st.session_state.user_id = emp["id"]
                st.rerun()
        else:
            pwd = st.text_input("", type="password", placeholder="Password — try admin123", label_visibility="collapsed")
            if st.button("Continue", type="primary", use_container_width=True):
                if pwd == "admin123":
                    st.session_state.role = "admin"
                    st.rerun()
                else:
                    st.error("Incorrect password.")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="text-align:center;font-size:11px;color:#4a5568;margin-top:12px;font-family:JetBrains Mono,monospace">Any employee profile · Admin password: admin123</div>', unsafe_allow_html=True)
    footer()
    st.stop()

# ── ROUTE ─────────────────────────────────────────────────────────────────────
if st.session_state.role == "admin":
    from pages.admin import render_admin
    render_admin()
else:
    from pages.employee import render_employee
    emp = next(e for e in EMPLOYEES if e["id"] == st.session_state.user_id)
    render_employee(emp)
