"""
app.py — LinkedIn Profile Optimizer: Streamlit UI + Pipeline Orchestration

Models:
  Agent 1 (Trend Researcher)  → Groq  / llama-3.1-8b-instant    (fast synthesis)
  Agent 2 (Gap Analyzer)      → Groq  / llama-3.3-70b-versatile  (strong reasoning)
  Agent 3 (Profile Rewriter)  → Gemini / gemini-2.0-flash        (best writing quality)
  Agent 4 (LLM-as-Judge)      → Groq  / llama-3.1-8b-instant    (fast evaluation)
  Agent 5 (Post Generator)    → Gemini / gemini-2.0-flash        (creative post writing)
"""

import streamlit as st
from agents import trend_researcher, gap_analyzer, profile_rewriter, llm_judge, linkedin_post_generator

# ── Page Config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="LinkedIn Profile Optimizer AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

/* ── Gruvbox + Neobrutalism tokens ───────────────────────────────────────── */
:root {
  --bg0-h:  #1d2021;
  --bg0:    #282828;
  --bg0-s:  #32302f;
  --bg1:    #3c3836;
  --bg2:    #504945;
  --bg3:    #665c54;
  --fg:     #ebdbb2;
  --fg2:    #bdae93;
  --fg3:    #a89984;
  --fg4:    #928374;
  --red:    #fb4934;
  --green:  #b8bb26;
  --yellow: #fabd2f;
  --blue:   #83a598;
  --purple: #d3869b;
  --aqua:   #8ec07c;
  --orange: #fe8019;
  --black:  #000000;
  --sh:     5px 5px 0 #000;
  --sh-sm:  3px 3px 0 #000;
  --sh-acc: 5px 5px 0 var(--yellow);
}

/* ── Base ────────────────────────────────────────────────────────────────── */
* { border-radius: 0 !important; box-sizing: border-box; }
body, * { font-family: 'Space Grotesk', sans-serif; }
.stApp { background: var(--bg0-h); color: var(--fg); }
#MainMenu, footer, header { visibility: hidden; }

/* ── Hero ────────────────────────────────────────────────────────────────── */
.hero {
    background: var(--bg0);
    border: 3px solid var(--yellow);
    box-shadow: var(--sh);
    padding: 2.5rem 3rem;
    margin-bottom: 2.5rem;
    text-align: center;
    position: relative;
}
.hero::before {
    content: '// AI AGENT PIPELINE v1.0';
    position: absolute; top: 0.5rem; left: 0.8rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; color: var(--fg4); letter-spacing: 0.1em;
}
.hero h1 {
    font-size: 2.3rem; font-weight: 800;
    color: var(--yellow); letter-spacing: -0.02em;
    margin-bottom: 0.4rem; text-transform: uppercase;
}
.hero p { color: var(--fg3); font-size: 0.88rem; margin: 0; }

/* ── Badges ──────────────────────────────────────────────────────────────── */
.badge {
    display: inline-block; padding: 0.2rem 0.65rem;
    font-size: 0.67rem; font-weight: 800; margin: 0.25rem;
    border: 2px solid var(--black); text-transform: uppercase; letter-spacing: 0.07em;
    font-family: 'JetBrains Mono', monospace; box-shadow: 2px 2px 0 var(--black);
}
.badge-yellow { background: var(--yellow); color: var(--black); }
.badge-blue   { background: var(--blue);   color: var(--black); }
.badge-green  { background: var(--green);  color: var(--black); }
.badge-purple { background: var(--purple); color: var(--black); }

/* ── Step bar ────────────────────────────────────────────────────────────── */
.step-bar { display: flex; gap: 0.5rem; margin: 1.5rem 0; justify-content: center; flex-wrap: wrap; }
.step {
    display: flex; align-items: center; gap: 0.4rem;
    padding: 0.4rem 0.9rem; font-size: 0.72rem; font-weight: 700;
    border: 2px solid var(--bg3); background: var(--bg0-s); color: var(--fg4);
    font-family: 'JetBrains Mono', monospace; text-transform: uppercase; letter-spacing: 0.05em;
}
.step.active {
    background: var(--yellow); border-color: var(--black); color: var(--black);
    box-shadow: var(--sh-sm);
}
.step.done {
    background: var(--green); border-color: var(--black); color: var(--black);
}

/* ── Section header ──────────────────────────────────────────────────────── */
.section-header {
    display: inline-block;
    font-size: 0.72rem; font-weight: 800;
    color: var(--black); background: var(--orange);
    border: 2px solid var(--black); padding: 0.3rem 0.8rem;
    margin: 1.5rem 0 1rem 0; box-shadow: var(--sh-sm);
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase; letter-spacing: 0.1em;
}

/* ── Profile cards ───────────────────────────────────────────────────────── */
.profile-card {
    background: var(--bg0-s); border: 2px solid var(--bg3);
    padding: 1.4rem; height: 100%; box-shadow: var(--sh-sm);
}
.profile-card.optimized {
    border-color: var(--yellow); box-shadow: var(--sh-acc);
}
.card-label {
    font-size: 0.64rem; font-weight: 800; text-transform: uppercase;
    letter-spacing: 0.14em; margin-bottom: 1rem; padding: 0.22rem 0.65rem;
    display: inline-block; font-family: 'JetBrains Mono', monospace; border: 2px solid;
}
.card-label.original  { background: var(--bg2); color: var(--fg3); border-color: var(--bg3); }
.card-label.optimized { background: var(--yellow); color: var(--black); border-color: var(--black); box-shadow: 2px 2px 0 var(--black); }

.headline-text {
    font-size: 0.96rem; font-weight: 700; color: var(--fg);
    margin-bottom: 1rem; line-height: 1.5;
    font-family: 'JetBrains Mono', monospace;
    padding: 0.55rem 0.75rem;
    background: var(--bg1); border-left: 4px solid var(--orange);
}
.about-text {
    color: var(--fg2); font-size: 0.86rem; line-height: 1.8;
    white-space: pre-wrap;
}
.sub-label {
    font-size: 0.62rem; font-weight: 800; color: var(--fg4);
    text-transform: uppercase; letter-spacing: 0.1em;
    font-family: 'JetBrains Mono', monospace;
    margin: 0.9rem 0 0.35rem 0;
}

/* ── Skill tags ──────────────────────────────────────────────────────────── */
.skills-container { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.35rem; }
.skill-tag {
    background: var(--bg1); color: var(--fg3); padding: 0.22rem 0.6rem;
    font-size: 0.71rem; font-weight: 600; border: 2px solid var(--bg3);
    font-family: 'JetBrains Mono', monospace;
}
.skill-tag.optimized {
    background: var(--bg0); color: var(--aqua); border-color: var(--aqua);
    box-shadow: 2px 2px 0 var(--black);
}

/* ── Gap cards ───────────────────────────────────────────────────────────── */
.gap-card {
    background: var(--bg0-s);
    border: 2px solid var(--bg3); border-left: 4px solid var(--orange);
    padding: 0.6rem 1rem; margin-bottom: 0.5rem;
    font-size: 0.83rem; color: var(--fg2); line-height: 1.6;
    box-shadow: 3px 3px 0 var(--black);
}

/* ── Score meters ────────────────────────────────────────────────────────── */
.score-row { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.9rem; }
.score-label {
    width: 170px; font-size: 0.7rem; color: var(--fg3); font-weight: 700;
    flex-shrink: 0; font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase; letter-spacing: 0.04em;
}
.score-bar-bg {
    flex: 1; background: var(--bg2); height: 14px; overflow: hidden;
    border: 2px solid var(--bg3);
}
.score-bar-fill { height: 100%; }
.score-value {
    font-size: 0.82rem; font-weight: 800; color: var(--fg);
    width: 38px; text-align: right; font-family: 'JetBrains Mono', monospace;
}

.overall-score {
    text-align: center; padding: 1.5rem 1rem;
    background: var(--yellow); border: 3px solid var(--black);
    box-shadow: var(--sh); margin-bottom: 1.2rem;
}
.overall-number {
    font-size: 4.5rem; font-weight: 800; color: var(--black);
    line-height: 1; font-family: 'JetBrains Mono', monospace;
}
.overall-label {
    color: var(--black); font-size: 0.68rem; margin-top: 0.35rem;
    font-family: 'JetBrains Mono', monospace;
    text-transform: uppercase; letter-spacing: 0.12em; font-weight: 800;
}

/* ── Button ──────────────────────────────────────────────────────────────── */
.stButton > button {
    background: var(--yellow) !important; color: var(--black) !important;
    border: 3px solid var(--black) !important;
    font-weight: 800 !important; font-size: 0.88rem !important;
    padding: 0.75rem 2rem !important; width: 100% !important;
    font-family: 'JetBrains Mono', monospace !important;
    text-transform: uppercase !important; letter-spacing: 0.1em !important;
    box-shadow: var(--sh) !important; transition: all 0.08s !important;
}
.stButton > button:hover {
    background: var(--orange) !important;
    box-shadow: 2px 2px 0 var(--black) !important;
    transform: translate(3px, 3px) !important;
}
.stButton > button:active {
    box-shadow: 0 0 0 var(--black) !important;
    transform: translate(5px, 5px) !important;
}

/* ── Inputs ──────────────────────────────────────────────────────────────── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--bg0) !important; border: 2px solid var(--bg3) !important;
    color: var(--fg) !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.87rem !important; padding: 0.55rem 0.75rem !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--yellow) !important;
    box-shadow: 3px 3px 0 var(--yellow) !important;
    outline: none !important;
}
label {
    color: var(--fg3) !important; font-size: 0.68rem !important; font-weight: 800 !important;
    text-transform: uppercase !important; letter-spacing: 0.08em !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: var(--bg0-s) !important;
    border-right: 3px solid var(--bg2) !important;
}

/* ── Expander ────────────────────────────────────────────────────────────── */
details summary {
    background: var(--bg1) !important; border: 2px solid var(--bg3) !important;
    color: var(--fg3) !important; font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important; text-transform: uppercase !important;
    letter-spacing: 0.06em !important; font-weight: 700 !important;
    padding: 0.5rem 0.8rem !important;
}

/* ── Misc Streamlit ──────────────────────────────────────────────────────── */
.stAlert { border: 2px solid !important; box-shadow: var(--sh-sm) !important; }
hr { border: 0; border-top: 2px solid var(--bg2) !important; margin: 1.5rem 0 !important; }
.stSpinner > div { border-top-color: var(--yellow) !important; }

/* ── Unified chat feed (Gemini/Claude style) ─────────────────────────────── */
/* Strip Streamlit's default white bubble background */
[data-testid="stChatMessageContent"] {
    background: transparent !important;
    padding: 0 !important;
}
/* AI message bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
[data-testid="stChatMessageContent"] {
    background: var(--bg1) !important;
    border: 2px solid var(--aqua) !important;
    border-left: 4px solid var(--aqua) !important;
    box-shadow: 3px 3px 0 #000 !important;
    padding: 1rem 1.2rem !important;
    color: var(--fg2) !important;
}
/* User message bubble */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
[data-testid="stChatMessageContent"] {
    background: var(--yellow) !important;
    border: 2px solid #000 !important;
    box-shadow: 3px 3px 0 #000 !important;
    padding: 0.85rem 1.1rem !important;
    color: #000 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
[data-testid="stChatMessageContent"] p {
    color: #000 !important;
}
/* Avatars — neobrutalist squares */
[data-testid="chatAvatarIcon-assistant"],
[data-testid="chatAvatarIcon-user"] {
    border: 2px solid #000 !important;
    box-shadow: 2px 2px 0 #000 !important;
    border-radius: 0 !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.6rem !important; font-weight: 800 !important;
}
[data-testid="chatAvatarIcon-assistant"] { background: var(--aqua) !important;   color: #000 !important; }
[data-testid="chatAvatarIcon-user"]      { background: var(--yellow) !important; color: #000 !important; }

/* Result sections inside an AI bubble */
.result-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.63rem; font-weight: 800; color: var(--fg4);
    text-transform: uppercase; letter-spacing: 0.12em;
    border-bottom: 1px solid var(--bg2);
    padding-bottom: 0.3rem; margin: 1.2rem 0 0.7rem;
}

/* ── Chat input bar ──────────────────────────────────────────────────────── */
[data-testid="stChatInput"] > div {
    background: var(--bg0) !important;
    border: 2px solid var(--bg3) !important;
    box-shadow: var(--sh-sm) !important;
}
[data-testid="stChatInput"] > div:focus-within {
    border-color: var(--yellow) !important;
    box-shadow: 3px 3px 0 var(--yellow) !important;
}
[data-testid="stChatInput"] textarea {
    background: var(--bg0) !important; color: var(--fg) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.88rem !important; border: none !important; box-shadow: none !important;
}
[data-testid="stChatInput"] button {
    background: var(--yellow) !important; border: 2px solid #000 !important;
    color: #000 !important; box-shadow: 2px 2px 0 #000 !important;
}
[data-testid="stChatInput"] button:hover {
    background: var(--orange) !important;
    transform: translate(2px,2px) !important; box-shadow: none !important;
}
.stChatFloatingInputContainer {
    background: var(--bg0-h) !important;
    border-top: 2px solid var(--bg2) !important; padding-top: 0.6rem !important;
}

/* ── LinkedIn-style profile card ─────────────────────────────────────────── */
.li-card {
    background: var(--bg0-s);
    border: 2px solid var(--bg3);
    box-shadow: var(--sh-sm);
    overflow: hidden;
    font-family: 'Space Grotesk', sans-serif;
}
.li-card.is-optimized { border-color: var(--yellow); box-shadow: 4px 4px 0 #000; }
.li-cover {
    height: 80px;
    background: linear-gradient(135deg, #3c3836 0%, #665c54 100%);
    border-bottom: 2px solid var(--bg2);
    position: relative;
}
.li-card.is-optimized .li-cover {
    background: linear-gradient(135deg, #3c3836 0%, #665c54 50%, rgba(250,189,47,.35) 100%);
    border-bottom-color: var(--yellow);
}
.li-avatar-row {
    display: flex; align-items: flex-end; justify-content: space-between;
    padding: 0 0.9rem; margin-top: -32px; margin-bottom: 0.5rem;
}
.li-avatar {
    width: 64px; height: 64px; flex-shrink: 0;
    border-radius: 50%;
    border: 3px solid var(--bg0-s); box-shadow: 2px 2px 0 #000;
    background: #504945; overflow: hidden;
    position: relative;
}
/* Person head */
.li-avatar::before {
    content: '';
    position: absolute;
    width: 26px; height: 26px;
    background: #928374;
    border-radius: 50%;
    top: 9px; left: 50%; transform: translateX(-50%);
}
/* Person body */
.li-avatar::after {
    content: '';
    position: absolute;
    width: 54px; height: 38px;
    background: #928374;
    border-radius: 50% 50% 0 0;
    bottom: -10px; left: 50%; transform: translateX(-50%);
}
.li-avatar > div { width: 100%; height: 100%; }
.li-card.is-optimized .li-avatar { border-color: var(--yellow); }
.li-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.58rem; font-weight: 800; text-transform: uppercase; letter-spacing: .08em;
    padding: 0.2rem 0.55rem; border: 2px solid; box-shadow: 2px 2px 0 #000;
}
.li-badge.orig { background: var(--bg2); color: var(--fg4); border-color: var(--bg3); }
.li-badge.opt  { background: var(--yellow); color: #000; border-color: #000; }
.li-body { padding: 0 0.9rem 0.9rem; }
.li-name { font-size: 0.9rem; font-weight: 800; color: var(--fg); margin-bottom: 0.18rem; }
.li-hl   { font-size: 0.78rem; color: var(--fg2); line-height: 1.45; margin-bottom: 0.3rem; font-family: 'JetBrains Mono', monospace; }
.li-loc  { font-size: 0.68rem; color: var(--fg4); font-family: 'JetBrains Mono', monospace; }
.li-divider { border: 0; border-top: 1px solid var(--bg2); margin: 0.7rem 0; }
.li-sec-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.63rem; font-weight: 800; color: var(--fg3);
    text-transform: uppercase; letter-spacing: .1em; margin-bottom: 0.4rem;
}
.li-about-text {
    font-size: 0.8rem; color: var(--fg2); line-height: 1.7; white-space: pre-line;
}
.li-skill-pill {
    display: inline-block; padding: 0.22rem 0.65rem; margin: 0.18rem 0.18rem 0 0;
    border: 1.5px solid var(--bg3); font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; font-weight: 600; color: var(--fg3); background: var(--bg1);
}
.li-card.is-optimized .li-skill-pill { border-color: var(--aqua); color: var(--aqua); }

/* ── Score display ───────────────────────────────────────────────────────── */
.score-wrap {
    display: flex; gap: 1.2rem; align-items: flex-start;
}
.score-donut-box {
    flex-shrink: 0;
    display: flex; flex-direction: column; align-items: center;
    gap: 0.3rem;
}
.score-metrics { flex: 1; display: flex; flex-direction: column; gap: 0.55rem; }
.score-row {
    display: flex; align-items: center; gap: 0.6rem;
}
.score-row-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.6rem; font-weight: 800; color: var(--fg4);
    text-transform: uppercase; letter-spacing: .08em;
    width: 110px; flex-shrink: 0;
}
.score-bar-track {
    flex: 1; height: 8px;
    background: var(--bg2); border: 1px solid var(--bg3);
}
.score-bar-fill { height: 100%; }
.score-pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.65rem; font-weight: 800; color: #000;
    background: var(--yellow); border: 1.5px solid #000;
    padding: 0.1rem 0.4rem; flex-shrink: 0;
}
.score-reasoning {
    margin-top: 0.8rem; padding: 0.65rem 0.85rem;
    border: 2px solid var(--bg3); border-left: 3px solid var(--blue);
    background: var(--bg0-s); font-size: 0.78rem; color: var(--fg3);
    line-height: 1.6; font-family: 'Space Grotesk', sans-serif;
}
</style>
""", unsafe_allow_html=True)


# ── UI Helpers ────────────────────────────────────────────────────────────────

def render_step_bar(active: int):
    """Render the 5-step progress indicator. active=1..5; 6=all done."""
    steps = [
        ("\U0001f50d", "Trend Research", "Groq/llama-3.1-8b"),
        ("\U0001f50e", "Gap Analysis", "Groq/llama-3.3-70b"),
        ("\u270d\ufe0f", "Profile Rewrite", "Gemini/gemini-2.0"),
        ("\u2696\ufe0f", "Quality Judge", "Groq/llama-3.1-8b"),
        ("\U0001f4dd", "Post Generator", "Gemini/gemini-2.0"),
    ]
    html = '<div class="step-bar">'
    for i, (icon, label, model) in enumerate(steps, 1):
        if i < active:
            cls, ico = "done", "✓"
        elif i == active:
            cls, ico = "active", icon
        else:
            cls, ico = "", icon
        html += f'<div class="step {cls}">{ico} {label} <span style="opacity:.55;font-size:.72rem">({model})</span></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def render_skill_tags(skills_str: str, optimized: bool = False):
    """Render skills as inline pill tags."""
    cls = "optimized" if optimized else ""
    skills = [s.strip() for s in skills_str.replace(",", "\n").splitlines() if s.strip()]
    tags = "".join(f'<span class="skill-tag {cls}">{s}</span>' for s in skills)
    st.markdown(f'<div class="skills-container">{tags}</div>', unsafe_allow_html=True)


def render_score_bar(label: str, score: int):
    """Render a labelled Gruvbox-coloured score bar (1-10)."""
    pct = score * 10
    if score >= 8:
        color = "#b8bb26"   # gruvbox green
    elif score >= 6:
        color = "#fabd2f"   # gruvbox yellow
    else:
        color = "#fb4934"   # gruvbox red
    st.markdown(f"""
<div class="score-row">
  <div class="score-label">{label}</div>
  <div class="score-bar-bg">
    <div class="score-bar-fill" style="width:{pct}%;background:{color};"></div>
  </div>
  <div class="score-value">{score}/10</div>
</div>""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar():
    """Render sidebar with model info and tips."""
    with st.sidebar:
        st.markdown("## &#x1F916; Model Setup")
        st.markdown("""
<div style="background:#3c3836;border:1px solid #504945;border-left:3px solid #fabd2f;padding:1rem;margin-bottom:1rem;">
  <div style="font-size:.75rem;color:#928374;margin-bottom:.6rem;font-weight:700;font-family:monospace;letter-spacing:.08em;">AGENT &rarr; MODEL</div>
  <div style="font-size:.8rem;color:#bdae93;line-height:2;font-family:monospace;">
    &#x1F50D; Trend Research &rarr; <span style="color:#fabd2f;font-weight:700;">Groq / llama-3.1-8b-instant</span><br>
    &#x1F50E; Gap Analysis &rarr; <span style="color:#fabd2f;font-weight:700;">Groq / llama-3.3-70b-versatile</span><br>
    &#x270D;&#xFE0F; Profile Rewrite &rarr; <span style="color:#8ec07c;font-weight:700;">Gemini / gemini-2.0-flash</span><br>
    &#x2696;&#xFE0F; Quality Judge &rarr; <span style="color:#fabd2f;font-weight:700;">Groq / llama-3.1-8b-instant</span><br>
    &#x1F4DD; Post Generator &rarr; <span style="color:#8ec07c;font-weight:700;">Gemini / gemini-2.0-flash</span>
  </div>
</div>
<div style="background:#3c3836;border:1px solid #504945;border-left:3px solid #83a598;padding:.7rem 1rem;margin-bottom:1rem;">
  <div style="font-size:.65rem;color:#928374;margin-bottom:.4rem;font-weight:700;font-family:monospace;letter-spacing:.08em;">POWERED BY</div>
  <div style="font-size:.75rem;color:#bdae93;line-height:1.9;font-family:monospace;">
    &#x26A1; <span style="color:#fabd2f;font-weight:700;">Groq</span> &mdash; ultra-fast inference<br>
    &#x1F48E; <span style="color:#8ec07c;font-weight:700;">Gemini</span> &mdash; best writing quality<br>
    &#x1F50D; <span style="color:#ebdbb2;">DuckDuckGo</span> &mdash; live trend search
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div style="margin-top:1.2rem;margin-bottom:0.5rem;font-size:.65rem;font-weight:800;color:#928374;
            text-transform:uppercase;letter-spacing:.1em;font-family:monospace;">&#x1F4A1; Tips</div>
<div style="border:2px solid #665c54;border-left:4px solid #8ec07c;background:#32302f;
            padding:.6rem .8rem;margin-bottom:.5rem;box-shadow:2px 2px 0 #000;
            font-size:.78rem;color:#bdae93;font-family:monospace;line-height:1.5;">
  Paste your <strong style="color:#ebdbb2;">full About section</strong> for best results.
</div>
<div style="border:2px solid #665c54;border-left:4px solid #8ec07c;background:#32302f;
            padding:.6rem .8rem;margin-bottom:.5rem;box-shadow:2px 2px 0 #000;
            font-size:.78rem;color:#bdae93;font-family:monospace;line-height:1.5;">
  Skills: comma-separated or one per line.
</div>
<div style="border:2px solid #665c54;border-left:4px solid #fabd2f;background:#32302f;
            padding:.6rem .8rem;margin-bottom:1rem;box-shadow:2px 2px 0 #000;
            font-size:.78rem;color:#bdae93;font-family:monospace;line-height:1.5;">
  &#x26A1; Cloud APIs run in <strong style="color:#fabd2f;">seconds per agent.</strong> Much faster!
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<div style="border-top:2px solid #504945;padding-top:.8rem;margin-top:.5rem;
            font-size:.68rem;color:#928374;text-align:center;font-family:monospace;
            letter-spacing:.04em;line-height:1.8;">
  &#x26A1; Groq Cloud Inference<br>
  &#x1F48E; Gemini Cloud Writing<br>
  &#x1F50D; DuckDuckGo (free)<br>
  <span style="color:#665c54;">Profile data stays in your session</span>
</div>""", unsafe_allow_html=True)




# ── Main App ──────────────────────────────────────────────────────────────────

def main():
    """Main Streamlit entry point."""

    render_sidebar()

    # ── Hero ──────────────────────────────────────────────────────────────────
    st.markdown("""
<div class="hero">
  <h1>&#x1F680; LinkedIn Profile Optimizer AI</h1>
  <p>4-agent pipeline &middot; Groq + Gemini powered &middot; DuckDuckGo live research</p>
  <div style="margin-top:.8rem;">
    <span class="badge badge-yellow">&#x1F50D; DuckDuckGo</span>
    <span class="badge badge-blue">&#x26A1; Groq LLaMA</span>
    <span class="badge badge-green">&#x1F48E; Gemini 2.0</span>
    <span class="badge badge-purple">&#x1F916; 4-Agent AI</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Session state init ─────────────────────────────────────────────────────
    defaults = {
        "messages": [],
        "chat_step": 0,          # 0=init, 1-4=collecting, 5=running, 6=done
        "job_role": "",
        "current_headline": "",
        "current_about": "",
        "current_skills": "",
        "pipeline_results": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    BOT_Q = [
        "👋 **Hey!** I'm your LinkedIn Profile Optimizer.\n\nI'll ask you **4 quick questions**, then run a full AI analysis.\n\n**What job role are you targeting?**\n*(e.g. Senior Data Scientist, Product Manager, ML Engineer)*",
        "Got it! 📌\n\n**What's your current LinkedIn headline?**\n*(e.g. Data Analyst | Python | SQL | Turning Data into Insights)*",
        "Nice. 📖\n\n**Paste your current About section.**\nThe more detail you share, the better I can optimize it.",
        "Almost there! 🛠️\n\n**List your current skills** — comma-separated or one per line.\n*(e.g. Python, SQL, Machine Learning, Tableau, Excel)*",
    ]

    # Seed first message on fresh load
    if st.session_state.chat_step == 0:
        st.session_state.messages = [{"role": "assistant", "content": BOT_Q[0]}]
        st.session_state.chat_step = 1

    # ── Render all chat messages via st.chat_message (one unified feed) ────────
    import re as _re

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Collect answers (steps 1-4) ────────────────────────────────────────────
    if st.session_state.chat_step in (1, 2, 3, 4):
        placeholders = [
            "e.g. Senior Data Scientist",
            "e.g. Data Analyst | Python | SQL | Turning Data into Insights",
            "Paste your LinkedIn About section here...",
            "Python, SQL, Machine Learning, Tableau...",
        ]
        ph = placeholders[st.session_state.chat_step - 1]
        user_input = st.chat_input(ph)

        if user_input and user_input.strip():
            ans = user_input.strip()
            st.session_state.messages.append({"role": "user", "content": ans})
            step = st.session_state.chat_step
            if step == 1:
                st.session_state.job_role = ans
                st.session_state.chat_step = 2
                st.session_state.messages.append({"role": "assistant", "content": BOT_Q[1]})
            elif step == 2:
                st.session_state.current_headline = ans
                st.session_state.chat_step = 3
                st.session_state.messages.append({"role": "assistant", "content": BOT_Q[2]})
            elif step == 3:
                st.session_state.current_about = ans
                st.session_state.chat_step = 4
                st.session_state.messages.append({"role": "assistant", "content": BOT_Q[3]})
            elif step == 4:
                st.session_state.current_skills = ans
                st.session_state.chat_step = 5
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"🚀 **Perfect!** Running the 4-agent pipeline for **{st.session_state.job_role}**...\n\n*This takes 3–5 minutes locally. Hang tight!*"
                })
            st.rerun()

    # ── Run pipeline (step 5) ──────────────────────────────────────────────────
    if st.session_state.chat_step == 5 and st.session_state.pipeline_results is None:
        jb = st.session_state.job_role
        ch = st.session_state.current_headline
        ca = st.session_state.current_about
        cs = st.session_state.current_skills

        render_step_bar(1)
        with st.spinner("🔍 Agent 1 — Researching LinkedIn trends..."):
            trend_data = trend_researcher(jb)
        if trend_data.get("error"):
            st.error(f"Trend Researcher failed: {trend_data['error']}"); return

        render_step_bar(2)
        with st.spinner("🔎 Agent 2 — Analyzing your profile gaps..."):
            gap_data = gap_analyzer(jb, ch, ca, cs, trend_data["trend_report"])
        if gap_data.get("error"):
            st.error(f"Gap Analyzer failed: {gap_data['error']}"); return

        render_step_bar(3)
        with st.spinner("✍️ Agent 3 — Rewriting your profile..."):
            rewrite_data = profile_rewriter(jb, ch, ca, cs,
                                            trend_data["trend_report"], gap_data["gaps"])
        if rewrite_data.get("error"):
            st.error(f"Profile Rewriter failed: {rewrite_data['error']}"); return

        render_step_bar(4)
        with st.spinner("⚖️ Agent 4 — Scoring the rewritten profile..."):
            judge_data = llm_judge(jb, rewrite_data["headline"],
                                   rewrite_data["about"], rewrite_data["skills"])
        render_step_bar(5)
        with st.spinner("\U0001f4dd Agent 5 — Generating your LinkedIn post..."):
            post_data = linkedin_post_generator(
                jb,
                rewrite_data["headline"],
                rewrite_data["about"],
                rewrite_data["skills"],
                trend_data["trend_report"],
            )
        render_step_bar(6)

        st.session_state.pipeline_results = {
            "trend": trend_data, "gaps": gap_data,
            "rewrite": rewrite_data, "judge": judge_data,
            "post": post_data,
        }
        st.session_state.chat_step = 6
        st.session_state.messages.append({
            "role": "assistant",
            "content": "✅ **Done!** Here's your full analysis 👇"
        })
        st.rerun()

    # ── Show results inside an AI chat message (step 6) ───────────────────────
    if st.session_state.chat_step == 6 and st.session_state.pipeline_results:
        res          = st.session_state.pipeline_results
        trend_data   = res["trend"]
        gap_data     = res["gaps"]
        rewrite_data = res["rewrite"]
        judge_data   = res["judge"]
        post_data    = res.get("post", {})
        ch = st.session_state.current_headline
        ca = st.session_state.current_about
        cs = st.session_state.current_skills

        def _safe(text):
            if not text:
                return text
            # Strip matched bold/italic pairs
            text = _re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text, flags=_re.DOTALL)
            # Strip orphaned leading/trailing asterisks (no closing pair)
            text = _re.sub(r"^\*+\s*", "", text, flags=_re.MULTILINE)
            text = _re.sub(r"\s*\*+$", "", text, flags=_re.MULTILINE)
            # Strip label prefixes at start
            text = _re.sub(r"^(headline|about|skills)\s*:\s*", "", text, flags=_re.IGNORECASE)
            # Cut off Skills: section bleeding into About (anywhere it appears)
            text = _re.sub(r"\n?Skills?:\s*.+$", "", text, flags=_re.IGNORECASE | _re.DOTALL)
            # Remove mid-text About: prefix
            text = _re.sub(r"\bAbout:\s*", "", text, flags=_re.IGNORECASE)
            return text.strip().replace("<", "&lt;").replace(">", "&gt;")


        # ── Avatar: empty div –– drawn by CSS ::before / ::after ────────────────
        AVATAR_HTML = ""  # silhouette rendered via CSS pseudo-elements

        def _li_skills(raw: str, optimized: bool) -> str:
            """Generate LinkedIn-style skill pills HTML."""
            items = [s.strip() for s in _re.split(r"[\n,]", raw) if s.strip()]
            # Filter out any gap/label text
            items = [i for i in items if not _re.match(
                r"^(\d+[\.\)]|gaps?|key|trends?|headline|about|skills?|missing|weak|vague)", i, _re.I)]
            pills = "".join(f'<span class="li-skill-pill">{_safe(i)}</span>' for i in items[:15])
            return pills or "(none)"

        def _score_donut(score) -> str:
            """SVG donut gauge for overall score."""
            try:
                s = float(score)
            except (TypeError, ValueError):
                s = 0.0
            r = 36
            circ = 2 * 3.14159265 * r
            filled = circ * min(s, 10) / 10
            gap = circ - filled
            color = "#b8bb26" if s >= 8 else "#fabd2f" if s >= 6 else "#fb4934"
            label = int(s) if s == int(s) else round(s, 1)
            return f"""<div class="score-donut-box">
  <svg width="108" height="108" viewBox="0 0 100 100">
    <circle cx="50" cy="50" r="{r}" fill="none" stroke="#504945" stroke-width="10"/>
    <circle cx="50" cy="50" r="{r}" fill="none" stroke="{color}" stroke-width="10"
      stroke-dasharray="{filled:.2f} {gap:.2f}" stroke-linecap="square"
      transform="rotate(-90 50 50)"/>
    <text x="50" y="47" text-anchor="middle" dominant-baseline="middle"
      font-family="JetBrains Mono,monospace" font-size="22" font-weight="800"
      fill="{color}">{label}</text>
    <text x="50" y="63" text-anchor="middle" dominant-baseline="middle"
      font-family="JetBrains Mono,monospace" font-size="9" fill="#928374">/10</text>
  </svg>
  <div style="font-size:.58rem;color:#928374;text-transform:uppercase;letter-spacing:.1em;font-family:monospace">Overall</div>
</div>"""

        def _score_row(label: str, val) -> str:
            """Single metric row: label + bar + pill."""
            try:
                v = float(val)
            except (TypeError, ValueError):
                v = 0.0
            pct = min(v, 10) / 10 * 100
            color = "#b8bb26" if v >= 8 else "#fabd2f" if v >= 6 else "#fb4934"
            num = int(v) if v == int(v) else round(v, 1)
            return f"""<div class="score-row">
  <div class="score-row-label">{label}</div>
  <div class="score-bar-track"><div class="score-bar-fill" style="width:{pct:.1f}%;background:{color}"></div></div>
  <div class="score-pill">{num}/10</div>
</div>"""

        # Render results as a rich assistant message — same feed as the chat
        with st.chat_message("assistant"):
            st.markdown('<div class="result-sub">&#x1F4CA; Profile Comparison</div>', unsafe_allow_html=True)
            col_orig, col_opt = st.columns(2)

            with col_orig:
                st.markdown(f"""
<div class="li-card">
  <div class="li-cover"></div>
  <div class="li-avatar-row">
    <div class="li-avatar"></div>
    <span class="li-badge orig">ORIGINAL</span>
  </div>
  <div class="li-body">
    <div class="li-name">LinkedIn User</div>
    <div class="li-hl">{_safe(ch) or "(no headline)"}</div>
    <div class="li-loc">&#x1F4CD; Your Location &nbsp;&middot;&nbsp; 500+ connections</div>
    <hr class="li-divider">
    <div class="li-sec-title">About</div>
    <div class="li-about-text">{_safe(ca) or "(no about section)"}</div>
    <hr class="li-divider">
    <div class="li-sec-title">Skills</div>
    <div>{_li_skills(cs, False)}</div>
  </div>
</div>""", unsafe_allow_html=True)

            with col_opt:
                hl  = _safe(rewrite_data["headline"]) if rewrite_data["headline"] else "⚠️ No headline"
                ab  = _safe(rewrite_data["about"])    if rewrite_data["about"]    else "⚠️ No about"
                sk  = rewrite_data["skills"] or ""
                st.markdown(f"""
<div class="li-card is-optimized">
  <div class="li-cover"></div>
  <div class="li-avatar-row">
    <div class="li-avatar"></div>
    <span class="li-badge opt">&#x2728; OPTIMIZED</span>
  </div>
  <div class="li-body">
    <div class="li-name">LinkedIn User</div>
    <div class="li-hl">{hl}</div>
    <div class="li-loc">&#x1F4CD; Your Location &nbsp;&middot;&nbsp; 500+ connections</div>
    <hr class="li-divider">
    <div class="li-sec-title">About</div>
    <div class="li-about-text">{ab}</div>
    <hr class="li-divider">
    <div class="li-sec-title">Skills</div>
    <div>{_li_skills(sk, True)}</div>
  </div>
</div>""", unsafe_allow_html=True)

            # ── Gaps ──────────────────────────────────────────────────────────
            st.markdown('<div class="result-sub">&#x1F50E; Identified Gaps</div>', unsafe_allow_html=True)
            if gap_data["gaps"]:
                for gap in gap_data["gaps"]:
                    st.markdown(f'<div class="gap-card">{_safe(gap)}</div>', unsafe_allow_html=True)
            else:
                st.caption("No specific gaps parsed.")

            # ── Quality scores ─────────────────────────────────────────────────
            st.markdown('<div class="result-sub">&#x2696;&#xFE0F; Quality Scores</div>', unsafe_allow_html=True)
            overall  = judge_data.get("overall_score", 0)
            clarity  = judge_data.get("clarity", 0)
            keywords = judge_data.get("keyword_density", 0)
            appeal   = judge_data.get("professional_appeal", 0)

            score_html = f"""
<div class="score-wrap">
  {_score_donut(overall)}
  <div class="score-metrics">
    {_score_row("Clarity", clarity)}
    {_score_row("Keywords", keywords)}
    {_score_row("Appeal", appeal)}
  </div>
</div>"""
            st.markdown(score_html, unsafe_allow_html=True)
            if judge_data.get("reasoning"):
                st.markdown(f'<div class="score-reasoning">{_safe(judge_data["reasoning"])}</div>', unsafe_allow_html=True)

            # ── LinkedIn Post ───────────────────────────────────────────────
            st.markdown('<div class="result-sub">&#x1F4DD; Your LinkedIn Post</div>', unsafe_allow_html=True)
            post_text = post_data.get("post", "") if post_data else ""
            post_hook = post_data.get("hook", "") if post_data else ""
            if post_text:
                # Hook banner
                if post_hook:
                    hook_safe = post_hook.replace('<', '&lt;').replace('>', '&gt;')
                    st.markdown(f"""
<div style="
  background:var(--yellow);color:#000;
  border:3px solid #000;box-shadow:5px 5px 0 #000;
  padding:1rem 1.3rem;margin-bottom:1rem;
  font-family:'JetBrains Mono',monospace;
  font-size:.92rem;font-weight:800;line-height:1.5;
">
  &#x1F3AF; <span style="font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;font-weight:800;display:block;margin-bottom:.3rem;opacity:.7;">SCROLL-STOPPING HOOK</span>
  {hook_safe}
</div>""", unsafe_allow_html=True)

                # Full post card
                st.markdown(f"""
<div style="
  background:var(--bg0-s);border:2px solid var(--aqua);
  border-left:4px solid var(--aqua);box-shadow:4px 4px 0 #000;
  padding:1.2rem 1.4rem;margin-bottom:.8rem;
  font-family:'Space Grotesk',sans-serif;
  font-size:.88rem;color:var(--fg2);line-height:1.8;
  white-space:pre-wrap;
">
  <div style="font-family:'JetBrains Mono',monospace;font-size:.58rem;font-weight:800;
              color:var(--aqua);text-transform:uppercase;letter-spacing:.12em;margin-bottom:.75rem;
              border-bottom:1px solid var(--bg2);padding-bottom:.4rem;">
    &#x1F4CB; GENERATED POST — COPY &amp; PASTE TO LINKEDIN
  </div>
  {post_text.replace(chr(10), '<br>')}
</div>""", unsafe_allow_html=True)

                # Copy-friendly text area
                st.text_area(
                    "\U0001f4cb Copy your post (click inside → Ctrl+A → Ctrl+C)",
                    value=post_text,
                    height=260,
                    key="post_copy_area",
                    help="Select all text and copy to paste on LinkedIn",
                )
            else:
                st.warning("Post generation did not return content. The profile pipeline results are shown above.")

            # ── Raw research ───────────────────────────────────────────────────
            st.markdown('<div class="result-sub">&#x1F52C; Raw Research</div>', unsafe_allow_html=True)
            with st.expander("View DuckDuckGo Trend Report", expanded=False):
                st.markdown(trend_data["trend_report"])
                for snippet in trend_data["raw_results"]:
                    st.caption(snippet)

        # Reset
        st.chat_input("Analysis complete — start over below ↓", disabled=True)
        if st.button("🔄 Start Over — Optimize Another Profile", key="reset_btn"):
            for k in ["messages", "chat_step", "job_role", "current_headline",
                      "current_about", "current_skills", "pipeline_results"]:
                del st.session_state[k]
            st.rerun()



if __name__ == "__main__":
    main()
