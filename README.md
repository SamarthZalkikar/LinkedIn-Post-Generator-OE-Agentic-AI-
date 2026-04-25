# 🚀 LinkedIn Profile Optimizer & Post Generator AI

> **A 5-agent AI pipeline that researches live LinkedIn trends, identifies gaps in your profile, rewrites every section, scores the result, and generates a ready-to-post LinkedIn post — powered by Groq + Gemini, no local GPU needed.**

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?style=flat-square)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203-orange?style=flat-square)](https://console.groq.com/)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-blue?style=flat-square)](https://aistudio.google.com/)

# Link of the deployed project 

https://linkedin-optimizer-ai.streamlit.app/

# Loom Video link
https://www.loom.com/share/ccad611cb4c74e4599cb7159ba1c5c84

<br>

## Table of Contents

1. [What It Does](#what-it-does)
2. [Architecture Overview](#architecture-overview)
3. [The 5-Agent Pipeline](#the-5-agent-pipeline)
4. [File Structure](#file-structure)
5. [Tech Stack](#tech-stack)
6. [Prerequisites](#prerequisites)
7. [Installation & Local Run](#installation--local-run)
8. [How to Use It](#how-to-use-it)
9. [UI Design System](#ui-design-system)
10. [Data Flow Diagram](#data-flow-diagram)
11. [Key Functions Reference](#key-functions-reference)
12. [Configuration](#configuration)
13. [Deploying to Streamlit Cloud](#deploying-to-streamlit-cloud)
14. [Troubleshooting](#troubleshooting)

---
<br>

## What It Does

LinkedIn Profile Optimizer AI is a **conversational Streamlit web app** that takes your existing LinkedIn profile and target job role, then runs it through a sequential **5-agent LLM pipeline**:

1. **Researches** current LinkedIn trends for your role (live DuckDuckGo search)
2. **Identifies gaps** between your profile and recruiter expectations
3. **Rewrites** your headline, about section, and skills with ATS-friendly language
4. **Scores** the rewritten profile on clarity, keyword density, and professional appeal
5. **Generates** a ready-to-post, role-specific LinkedIn post with a scroll-stopping hook, punchy insights, CTA, and hashtags

Results are shown as a side-by-side LinkedIn-style card comparison, an SVG donut score gauge, and a copy-ready LinkedIn post card.

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend (app.py)                        │
│  ┌──────────┐  ┌──────────┐  ┌───────────────┐  ┌────────┐  ┌───────┐ │
│  │ Chat UI  │→ │ Step Bar │→ │ Profile Cards │→ │ Score  │→ │ Post  │ │
│  │ (4 Q&A)  │  │(progress)│  │(orig vs. opt) │  │(donut) │  │ Card  │ │
│  └──────────┘  └──────────┘  └───────────────┘  └────────┘  └───────┘ │
└──────────────────────────┬─────────────────────────────────────────────┘
                           │ calls
┌──────────────────────────▼──────────────────────────────────────────────┐
│                     Agent Pipeline (agents.py)                          │
│                                                                         │
│  Agent 1     Agent 2         Agent 3        Agent 4       Agent 5       │
│  Trend  ──►  Gap        ──►  Profile  ──►  LLM-as-  ──►  Post          │
│  Researcher  Analyzer        Rewriter       Judge          Generator    │
│                                                                         │
│  Groq        Groq            Gemini         Groq           Gemini       │
│  3.1-8b      3.3-70b         2.0-flash      3.1-8b         2.0-flash    │
└──────┬────────────────────────────────────────────┬──────────────────────┘
       │                                            │
┌──────▼──────┐                           ┌─────────▼────────┐
│ DuckDuckGo  │                           │  Groq Cloud API  │
│ Web Search  │                           │  Gemini Cloud    │
└─────────────┘                           └──────────────────┘
```

---

## The 5-Agent Pipeline

### Agent 1 — Trend Researcher
**Model:** `Groq / llama-3.1-8b-instant`

1. Fires **3 DuckDuckGo searches** (no key required):
   - `"best LinkedIn profile examples for {role} 2024"`
   - `"LinkedIn headline tips for {role} recruiters"`
   - `"top skills keywords {role} LinkedIn optimization"`
2. Collects up to 12 snippets (350 chars each)
3. Synthesises a **4-section Trend Report**: Headline Patterns · About Style · Must-Have Keywords · Common Mistakes

**Returns:** `{ raw_results, trend_report, error }`

---

### Agent 2 — Gap Analyzer
**Model:** `Groq / llama-3.3-70b-versatile` (strongest reasoning model)

Compares the user's current profile against the Trend Report and returns **6–10 specific gaps** as a numbered list, covering: missing keywords, weak headline, vague about section, missing CTA, skills deficiencies.

**Returns:** `{ gaps: list[str], raw_response, error }`

---

### Agent 3 — Profile Rewriter
**Model:** `Gemini / gemini-2.0-flash` *(falls back to Groq llama-3.3-70b on quota error)*

Rewrites all three profile sections following strict rules:
- **HEADLINE** — max 220 chars, format `Role | Differentiator | Key Tools`
- **ABOUT** — 3 paragraphs: hook, 2 quantified achievements, call-to-action
- **SKILLS** — 12–15 items, most important first

Uses two-pass parsing (JSON → regex marker fallback) plus a `_clean()` post-processor that strips markdown, deduplicates skills, and removes label bleed-through.

**Returns:** `{ headline, about, skills, raw_response, error }`

---

### Agent 4 — LLM-as-Judge
**Model:** `Groq / llama-3.1-8b-instant`

Scores the *rewritten* profile and returns JSON:

```json
{
  "clarity": 8,
  "keyword_density": 7,
  "professional_appeal": 9,
  "overall_score": 8.0,
  "reasoning": "Strong value prop with quantified achievements."
}
```

| Metric | What it measures |
|--------|-----------------|
| **Clarity** | Is the value proposition obvious in 3 seconds? |
| **Keyword Density** | Are ATS-searchable, role-specific terms present? |
| **Professional Appeal** | Is the tone confident, engaging, and memorable? |

**Returns:** `{ clarity, keyword_density, professional_appeal, overall_score, reasoning, error }`

---

### Agent 5 — LinkedIn Post Generator
**Model:** `Gemini / gemini-2.0-flash` *(falls back to Groq llama-3.3-70b on quota error)*

Takes the optimized profile (headline, about, skills) plus the role and trend report, and crafts a **ready-to-post LinkedIn post** following content best practices:

- 🎯 **Scroll-stopping hook** — a bold opening statement or question (shown separately in a yellow banner)
- 💡 **3–5 punchy insights** prefixed with role-relevant emojis
- 📣 **CTA** — invites comments or connections
- `#️⃣` **5–7 hashtags** for reach
- Sweet-spot length of **150–250 words**
- Tone: confident, conversational, authentic — not corporate

The full post is displayed in a copy-ready card with a text area for easy Ctrl+A → Ctrl+C.

**Returns:** `{ post, hook, raw_response, error }`

---

## File Structure

```
linkedin-optimizer/
│
├── app.py                   # Streamlit UI + pipeline orchestration
├── agents.py                # 5 agent functions (pure Python, no UI)
├── requirements.txt         # Python dependencies
├── .env                     # Local API keys (git-ignored)
├── .env.example             # Key template to share with others
└── .streamlit/
    ├── config.toml          # Streamlit server config
    └── secrets.toml         # API keys for Streamlit Cloud deployment
```

### `app.py` sections at a glance

| Section | Responsibility |
|---------|---------------|
| CSS | Full Gruvbox/Neobrutalist design system |
| `render_step_bar()` | 5-step progress bar showing active agent |
| `render_sidebar()` | Model map (Groq/Gemini) + usage tips |
| `main()` — Chat Loop | Conversational Q&A intake (steps 1–4) |
| `main()` — Pipeline | Runs all 5 agents sequentially (step 5) |
| `main()` — Results | Side-by-side cards, gaps, scores, LinkedIn post card (step 6) |

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| UI Framework | Streamlit ≥ 1.35 | Python web app with chat primitives |
| LLM — Speed | [Groq](https://console.groq.com/) | Ultra-fast inference for Agents 1, 2, 4 |
| LLM — Quality | [Gemini 2.0 Flash](https://aistudio.google.com/) | Best writing quality for Agents 3 & 5 |
| Web Search | DDGS (DuckDuckGo) | Free, no-key live trend research |
| Fonts | JetBrains Mono + Space Grotesk | Code aesthetic + readable body |
| Secrets | python-dotenv + st.secrets | Works for both local & cloud deploy |

---

## Prerequisites

### API Keys

| Service | Get it at | Free tier |
|---------|-----------|-----------|
| **Groq** | [console.groq.com](https://console.groq.com) | ✅ Generous free tier |
| **Gemini** | [aistudio.google.com](https://aistudio.google.com/app/apikey) | ✅ Free tier available |

### Python 3.10+

```bash
python --version   # must be 3.10 or later
```

---

## Installation & Local Run

```bash
# 1. Navigate to the project folder
cd linkedin-optimizer

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your API keys
cp .env.example .env
# Edit .env and fill in GROQ_API_KEY and GEMINI_API_KEY

# 5. Run
streamlit run app.py
```

App opens at **http://localhost:8501**.

> **Speed:** Cloud APIs respond in seconds per agent — the full pipeline typically completes in **under 30 seconds** (vs. 3–5 minutes with local models).

---

## How to Use It

```
On load       Bot asks: "What job role are you targeting?"

Step 1  →  You type your target role  (e.g. "Senior Data Scientist")
Step 2  →  You paste your current headline
Step 3  →  You paste your current About section
Step 4  →  You list your current skills (comma-separated or one per line)

Pipeline runs (step bar shows which agent is active):
  🔍 Agent 1 — Trend Research    [Groq / llama-3.1-8b-instant]
  🔎 Agent 2 — Gap Analysis      [Groq / llama-3.3-70b-versatile]
  ✍️  Agent 3 — Profile Rewrite   [Gemini / gemini-2.0-flash]
  ⚖️  Agent 4 — Quality Judge     [Groq / llama-3.1-8b-instant]
  📝 Agent 5 — Post Generator    [Gemini / gemini-2.0-flash]

Results display:
  • Side-by-side LinkedIn-style profile cards (Original vs Optimized)
  • Gap list with specific improvement areas
  • SVG donut + per-metric score bars (Clarity, Keywords, Appeal)
  • 📝 LinkedIn Post card — scroll-stopping hook banner + full post
  • Copy-ready text area (Ctrl+A → Ctrl+C → paste to LinkedIn)
  • Expandable raw DuckDuckGo trend report
  • "Start Over" button to analyze another profile
```

---

## UI Design System

The app uses a **Neobrutalist × Gruvbox Dark** design — all plain CSS injected via `st.markdown(..., unsafe_allow_html=True)`.

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg0-h` | `#1d2021` | App background |
| `--bg0` | `#282828` | Card backgrounds |
| `--yellow` | `#fabd2f` | Primary accent, buttons, Groq labels |
| `--orange` | `#fe8019` | Section headers, hover |
| `--green` | `#b8bb26` | High scores, done steps |
| `--red` | `#fb4934` | Low scores |
| `--aqua` | `#8ec07c` | AI chat bubbles, Gemini labels, optimized pills |
| `--blue` | `#83a598` | Reasoning block borders |
| `--black` | `#000000` | Neobrutalist hard shadows (`5px 5px 0 #000`) |

### Typography
- **Body:** Space Grotesk — modern, readable
- **Mono/Labels:** JetBrains Mono — scores, badges, inputs, step bar

---

## Data Flow Diagram

```
              User Input (4 chat answers)
                          │
                          ▼
                ┌─────────────────────┐
                │  job_role           │
                │  current_headline   │  → stored in st.session_state
                │  current_about      │
                │  current_skills     │
                └──────────┬──────────┘
                           │
                           ▼
┌──────────────────────────────────────────────────────────┐
│  Agent 1 — trend_researcher(job_role)                    │
│  DuckDuckGo ×3 → 12 snippets → Groq synthesis            │
│  Output: trend_report (string)                           │
└──────────────────────────┬───────────────────────────────┘
                           │ trend_report
                           ▼
┌──────────────────────────────────────────────────────────┐
│  Agent 2 — gap_analyzer(role, headline, about,           │
│                          skills, trend_report)           │
│  Groq llama-3.3-70b → numbered gap list                  │
│  Output: gaps (list[str], 6–10 items)                    │
└──────────────────────────┬───────────────────────────────┘
                           │ gaps
                           ▼
┌──────────────────────────────────────────────────────────┐
│  Agent 3 — profile_rewriter(role, …, trend, gaps)        │
│  Gemini 2.0-flash → HEADLINE/ABOUT/SKILLS markers        │
│  → JSON fallback → _clean() post-processing              │
│  Output: headline, about, skills (strings)               │
└──────────────────────────┬───────────────────────────────┘
                           │ headline, about, skills
                           ▼
┌──────────────────────────────────────────────────────────┐
│  Agent 4 — llm_judge(role, headline, about, skills)      │
│  Groq llama-3.1-8b → JSON scores                         │
│  Output: clarity, keyword_density, appeal, overall       │
└──────────────────────────┬───────────────────────────────┘
                           │ headline, about, skills, trend_report
                           ▼
┌──────────────────────────────────────────────────────────┐
│  Agent 5 — linkedin_post_generator(role, headline,       │
│                          about, skills, trend_report)    │
│  Gemini 2.0-flash → HOOK + POST markers                  │
│  Output: hook (str), post (str)                          │
└──────────────────────────┬───────────────────────────────┘
                           │ all results
                           ▼
                  Streamlit Results UI
          ┌──────────────────────────────────────┐
          │  Side-by-side profile cards          │
          │  Gap list (orange border cards)      │
          │  SVG donut + score bars              │
          │  📝 LinkedIn Post card + copy area   │
          │  Expandable raw research view        │
          └──────────────────────────────────────┘
```

---

## Key Functions Reference

### `agents.py`

| Function | Description |
|----------|-------------|
| `_get_secret(key)` | Reads from `st.secrets` (Streamlit Cloud) or `.env` (local) |
| `_extract_json(text)` | 3-strategy JSON extractor: fence strip → brace match → auto-fix |
| `_chat_groq(model, prompt)` | Groq chat completion, returns text string |
| `_chat_gemini(prompt)` | Gemini generation; auto-falls back to Groq on 429/quota errors |
| `trend_researcher(job_role)` | Agent 1: DuckDuckGo search + synthesis |
| `gap_analyzer(...)` | Agent 2: profile vs. trends comparison |
| `profile_rewriter(...)` | Agent 3: full rewrite with two-pass parsing + cleaning |
| `llm_judge(...)` | Agent 4: JSON score evaluation |
| `linkedin_post_generator(...)` | Agent 5: role-specific post with hook, insights, CTA, hashtags |

### `app.py`

| Function | Description |
|----------|-------------|
| `render_step_bar(active)` | Progress bar; `active=1..5` running, `6` = all done |
| `render_sidebar()` | Shows Groq/Gemini model map (all 5 agents) + usage tips |
| `_safe(text)` | Strips markdown, label prefixes, HTML-escapes for safe injection |
| `_score_donut(score)` | SVG circular gauge (green ≥8, yellow ≥6, red <6) |
| `_chat_gemini` fallback | If Gemini 429s, silently retries via Groq smart model |

---

## Configuration

### `.env` (local development)

```env
GROQ_API_KEY=gsk_...
GEMINI_API_KEY=AIza...
```

### Model constants in `agents.py`

```python
MODEL_GROQ_FAST  = "llama-3.1-8b-instant"    # Agents 1 & 4
MODEL_GROQ_SMART = "llama-3.3-70b-versatile" # Agent 2 & Gemini fallback
MODEL_GEMINI     = "models/gemini-2.0-flash"  # Agents 3 & 5
```

Want to swap models? Any Groq-supported model ID works for `MODEL_GROQ_*`.  
For Gemini, use the `models/` prefix (e.g. `models/gemini-2.5-flash`).

---

## Deploying to Streamlit Cloud

> **Why not Vercel?** Vercel is a serverless platform for stateless functions. Streamlit requires a persistent Python process with WebSocket connections — these are fundamentally incompatible. **[Streamlit Community Cloud](https://share.streamlit.io)** is the correct free hosting platform for this app.

### Steps

**1. Push your code to GitHub**
```bash
git init && git add . && git commit -m "initial commit"
gh repo create linkedin-optimizer --public --push
```

> Make sure `.env` is in `.gitignore` — never commit your API keys.

**2. Connect to Streamlit Cloud**
- Go to [share.streamlit.io](https://share.streamlit.io)
- Click **New app** → select your repo
- Set **Main file path** to `app.py`

**3. Add secrets**
- In your app → **Settings → Secrets**, paste:

```toml
GROQ_API_KEY = "gsk_..."
GEMINI_API_KEY = "AIza..."
```

**4. Deploy** — Streamlit installs `requirements.txt` automatically.

Your app will be live at `https://your-app-name.streamlit.app` in ~1 minute.

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `[Groq Error] Authentication failed` | Check `GROQ_API_KEY` in `.env` or Streamlit secrets |
| `[Gemini Error] 429 RESOURCE_EXHAUSTED` | Auto-fallback to Groq activates; no action needed |
| `[Gemini Error] 404 NOT_FOUND` | Model name must include `models/` prefix |
| DuckDuckGo search fails | Rate-limited — wait 30 s and retry, or check network |
| Empty headline / `⚠️ No headline` | LLM output was unparseable — re-run; pipeline still completes |
| `streamlit: command not found` | Activate your virtual environment first |
| Port conflict | `streamlit run app.py --server.port 8502` |


---

<div align="center">
  <strong>Built with ❤️ using Streamlit · Groq · Gemini · DuckDuckGo</strong><br>
  <em>5-agent pipeline · Cloud-powered · No local GPU needed · Deploys in minutes</em>
</div>
