"""
agents.py — LinkedIn Profile Optimizer: 5-Agent Pipeline Functions

Model assignment:
  - Agent 1 (Trend Researcher)   → Groq  / llama-3.1-8b-instant   (fast synthesis)
  - Agent 2 (Gap Analyzer)       → Groq  / llama-3.3-70b-versatile (strong reasoning)
  - Agent 3 (Profile Rewriter)   → Gemini / gemini-2.0-flash       (best writing quality)
  - Agent 4 (LLM-as-Judge)       → Groq  / llama-3.1-8b-instant   (fast evaluation)
  - Agent 5 (Post Generator)     → Gemini / gemini-2.0-flash       (creative post writing)
"""

import os
import re
import json

from groq import Groq
from google import genai as google_genai
from ddgs import DDGS
from dotenv import load_dotenv

load_dotenv()

# ── API key resolution (works for both local .env and Streamlit Cloud secrets) ─

def _get_secret(key: str) -> str:
    """Read a secret from st.secrets (Streamlit Cloud) or os.environ (.env)."""
    try:
        import streamlit as st
        return st.secrets.get(key) or os.environ.get(key, "")
    except Exception:
        return os.environ.get(key, "")

# ── API client initialisation ─────────────────────────────────────────────────

_groq_client = Groq(api_key=_get_secret("GROQ_API_KEY"))
_gemini_client = google_genai.Client(api_key=_get_secret("GEMINI_API_KEY"))

# Model constants
MODEL_GROQ_FAST  = "llama-3.1-8b-instant"      # Agents 1 & 4 — synthesis, evaluation
MODEL_GROQ_SMART = "llama-3.3-70b-versatile"   # Agent 2 & fallback — analytical reasoning
MODEL_GEMINI     = "models/gemini-2.0-flash"    # Agent 3 — profile rewriting


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_json(text: str) -> dict:
    """Extract JSON from model output with multiple fallback strategies."""
    # Strategy 1: strip ```json fences, then parse
    fenced = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    candidate = fenced.group(1).strip() if fenced else text

    # Strategy 2: find the outermost {...} block
    brace_match = re.search(r"\{[\s\S]+\}", candidate)
    if brace_match:
        try:
            return json.loads(brace_match.group())
        except json.JSONDecodeError:
            # Strategy 3: try to fix common small-model JSON mistakes
            fixed = brace_match.group()
            # Remove trailing commas before } or ]
            fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
            # Escape unescaped newlines inside string values
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                pass

    return {}


def _chat_groq(model: str, prompt: str) -> str:
    """Send a prompt to Groq and return the response text."""
    try:
        response = _groq_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2048,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[Groq Error - {model}] {e}"


def _chat_gemini(prompt: str) -> str:
    """Send a prompt to Gemini and return the response text.
    Falls back to Groq llama-3.3-70b-versatile if Gemini quota is exceeded.
    """
    try:
        response = _gemini_client.models.generate_content(
            model=MODEL_GEMINI,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        err_str = str(e)
        # Graceful fallback: if rate-limited or quota exceeded, use Groq
        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
            return _chat_groq(MODEL_GROQ_SMART, prompt)
        return f"[Gemini Error - {MODEL_GEMINI}] {e}"


# ── Agent 1 — Trend Researcher (Groq / llama-3.1-8b-instant) ─────────────────

def trend_researcher(job_role: str) -> dict:
    """
    Run 3 DuckDuckGo searches on LinkedIn trends for the given job role,
    then synthesize results using Groq llama-3.1-8b-instant.

    Returns:
        dict with keys: raw_results (list[str]), trend_report (str), error (str|None)
    """
    out = {"raw_results": [], "trend_report": "", "error": None}
    queries = [
        f"best LinkedIn profile examples for {job_role} 2024",
        f"LinkedIn headline tips for {job_role} recruiters",
        f"top skills keywords {job_role} LinkedIn optimization",
    ]
    snippets = []
    try:
        with DDGS() as ddgs:
            for q in queries:
                try:
                    results = list(ddgs.text(q, max_results=4))
                    for r in results:
                        snippets.append(f"[{r.get('title', '')}] {r.get('body', '')[:350]}")
                except Exception as e:
                    snippets.append(f"[Search error: {q}] {e}")
    except Exception as e:
        out["error"] = f"DuckDuckGo search failed: {e}"
        return out

    out["raw_results"] = snippets

    prompt = f"""You are a LinkedIn expert. Based on search results about profiles for "{job_role}", write a trend report with 4 sections using bullet points:

1. Headline Patterns — formats and keywords top profiles use
2. About Section Style — tone, length, hooks
3. Must-Have Keywords — critical searchable terms
4. Common Mistakes — what weak profiles get wrong

Search Results:
{chr(10).join(snippets[:8])}

Write concise, actionable bullet points for each section."""

    out["trend_report"] = _chat_groq(MODEL_GROQ_FAST, prompt)
    return out


# ── Agent 2 — Gap Analyzer (Groq / llama-3.3-70b-versatile) ──────────────────

def gap_analyzer(job_role: str, headline: str, about: str, skills: str,
                 trend_report: str) -> dict:
    """
    Compare user's current profile against the trend report and identify 6-10 gaps.
    Uses Groq llama-3.3-70b-versatile for stronger analytical reasoning.

    Returns:
        dict with keys: gaps (list[str]), raw_response (str), error (str|None)
    """
    out = {"gaps": [], "raw_response": "", "error": None}

    prompt = f"""You are a LinkedIn career coach reviewing a "{job_role}" profile.

Current Profile:
- Headline: {headline or "(empty)"}
- About: {about or "(empty)"}
- Skills: {skills or "(empty)"}

Industry Trends:
{trend_report}

List 6 to 10 specific gaps as a numbered list. Each item: "N. **Label** — explanation"
Cover: missing keywords, weak headline, vague about section, missing CTA, skills gaps.
Return ONLY the numbered list, nothing else."""

    raw = _chat_groq(MODEL_GROQ_SMART, prompt)
    out["raw_response"] = raw

    gaps = [l.strip() for l in raw.splitlines() if re.match(r"^\d+[\.\)]\s+", l.strip())]
    out["gaps"] = gaps if gaps else [l.strip() for l in raw.splitlines() if l.strip()]
    return out


# ── Agent 3 — Profile Rewriter (Gemini / gemini-2.0-flash) ───────────────────

def profile_rewriter(job_role: str, headline: str, about: str, skills: str,
                     trend_report: str, gaps: list) -> dict:
    """
    Rewrite headline, about, and skills based on gaps and trends.
    Uses Gemini gemini-2.0-flash for best-in-class writing quality.

    Returns:
        dict with keys: headline (str), about (str), skills (str),
                        raw_response (str), error (str|None)
    """
    out = {"headline": "", "about": "", "skills": "", "raw_response": "", "error": None}

    gaps_text = "\n".join(gaps[:6]) if gaps else "None identified."

    prompt = f"""You are an expert LinkedIn profile writer. Rewrite this profile for "{job_role}".

Current Profile:
Headline: {headline or "(empty)"}
About: {about or "(empty)"}
Skills: {skills or "(empty)"}

Gaps to fix:
{gaps_text}

Key trends: {trend_report[:400]}

Write the three sections following these rules:
- HEADLINE: max 220 chars, format: Role | Differentiator | Key Tools
- ABOUT: 3 short paragraphs - hook sentence, 2 achievements with numbers, call-to-action
- SKILLS: 12-15 items comma-separated, most important first

Output format - use EXACTLY these markers on separate lines:
HEADLINE: <your headline here>
ABOUT: <your about section here>
SKILLS: <skill1, skill2, skill3, ...>"""

    raw = _chat_gemini(prompt)
    out["raw_response"] = raw

    # Primary: try JSON extraction
    parsed = _extract_json(raw)
    out["headline"] = parsed.get("headline", "")
    out["about"]    = parsed.get("about", "")
    out["skills"]   = parsed.get("skills", "")

    # Fallback: extract via HEADLINE/ABOUT/SKILLS markers
    if not out["headline"]:
        m = re.search(r"HEADLINE:\s*(.+?)(?=\nABOUT:|\nSKILLS:|$)", raw, re.DOTALL | re.IGNORECASE)
        if m:
            out["headline"] = m.group(1).strip()[:220]

    if not out["about"]:
        m = re.search(r"ABOUT:\s*(.+?)(?=\nSKILLS:|\nHEADLINE:|$)", raw, re.DOTALL | re.IGNORECASE)
        if m:
            out["about"] = m.group(1).strip()

    if not out["skills"]:
        m = re.search(r"SKILLS:\s*(.+?)(?=\nHEADLINE:|\nABOUT:|$)", raw, re.DOTALL | re.IGNORECASE)
        if m:
            raw_skills = m.group(1).strip()
            out["skills"] = "\n".join(
                s.strip() for s in re.split(r"[,\n]", raw_skills) if s.strip()
            )

    # Post-process: strip markdown and stray label prefixes from all fields
    def _clean(text: str) -> str:
        # Strip matched bold/italic pairs
        text = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", text, flags=re.DOTALL)
        # Strip orphaned leading asterisks (no closing pair)
        text = re.sub(r"^\*+\s*", "", text, flags=re.MULTILINE)
        # Strip trailing asterisks
        text = re.sub(r"\s*\*+$", "", text, flags=re.MULTILINE)
        # Strip label prefixes (Headline:, About:, Skills:)
        text = re.sub(r"^(headline|about|skills)\s*:\s*", "", text, flags=re.IGNORECASE)
        # Cut off any trailing Skills: section that leaked into About
        text = re.sub(r"\n?Skills?:\s*.+$", "", text, flags=re.IGNORECASE | re.DOTALL)
        # Remove any "About:" prefix mid-text
        text = re.sub(r"\bAbout:\s*", "", text, flags=re.IGNORECASE)
        return text.strip()

    def _clean_skills(text: str) -> str:
        items = re.split(r"[,\n]", text)
        seen, cleaned = set(), []
        for item in items:
            item = re.sub(r"^[\s*+\-•]+", "", item)   # strip bullets
            item = re.sub(r"\*{1,3}(.+?)\*{1,3}", r"\1", item)
            item = re.sub(r"^\*+\s*", "", item)
            item = re.sub(r"^(skills?|headline|about)\s*:?\s*$", "", item, flags=re.IGNORECASE)
            item = item.strip()
            if item and item.lower() not in seen:
                seen.add(item.lower())
                cleaned.append(item)
        return "\n".join(cleaned)

    out["headline"] = _clean(out["headline"])
    out["about"]    = _clean(out["about"])
    out["skills"]   = _clean_skills(out["skills"])

    return out


# ── Agent 4 — LLM-as-Judge (Groq / llama-3.1-8b-instant) ────────────────────

def llm_judge(job_role: str, headline: str, about: str, skills: str) -> dict:
    """
    Score the rewritten profile on clarity, keyword_density, professional_appeal (1-10).
    Uses Groq llama-3.1-8b-instant for fast evaluation.

    Returns:
        dict with keys: clarity, keyword_density, professional_appeal,
                        overall_score, reasoning, raw_response, error
    """
    out = {"clarity": 0, "keyword_density": 0, "professional_appeal": 0,
           "overall_score": 0.0, "reasoning": "", "raw_response": "", "error": None}

    prompt = f"""Score this LinkedIn profile for "{job_role}" on three criteria (1-10 each):

Headline: {headline}
About: {about[:400]}
Skills: {skills}

Criteria:
- clarity: Is the value proposition obvious in 3 seconds?
- keyword_density: Are ATS-searchable role-specific terms present?
- professional_appeal: Is the tone confident, engaging, memorable?

Return ONLY valid JSON, no extra text:
{{"clarity": N, "keyword_density": N, "professional_appeal": N, "overall_score": N.N, "reasoning": "one sentence"}}"""

    raw = _chat_groq(MODEL_GROQ_FAST, prompt)
    out["raw_response"] = raw
    parsed = _extract_json(raw)

    try:
        out["clarity"] = int(parsed.get("clarity", 0))
        out["keyword_density"] = int(parsed.get("keyword_density", 0))
        out["professional_appeal"] = int(parsed.get("professional_appeal", 0))
        scores = [out["clarity"], out["keyword_density"], out["professional_appeal"]]
        valid = [s for s in scores if s > 0]
        out["overall_score"] = round(sum(valid) / len(valid), 1) if valid else 0.0
        out["reasoning"] = parsed.get("reasoning", "")
    except (ValueError, TypeError) as e:
        out["error"] = f"Score parsing failed: {e}"

    return out


# ── Agent 5 — LinkedIn Post Generator (Gemini / gemini-2.0-flash) ────────────

def linkedin_post_generator(job_role: str, headline: str, about: str,
                            skills: str, trend_report: str) -> dict:
    """
    Generate an engaging, role-specific LinkedIn post based on the optimized
    profile data. Uses Gemini gemini-2.0-flash for creative writing quality.

    Returns:
        dict with keys: post (str), hook (str), raw_response (str), error (str|None)
    """
    out = {"post": "", "hook": "", "raw_response": "", "error": None}

    skills_preview = ", ".join(s.strip() for s in skills.replace("\n", ",").split(",") if s.strip())[:200]
    about_preview = about[:500] if about else ""

    prompt = f"""You are an expert LinkedIn content strategist. Write an engaging LinkedIn post for someone targeting the role of "{job_role}".

Their optimized profile:
- Headline: {headline}
- About (excerpt): {about_preview}
- Key Skills: {skills_preview}

Role-specific LinkedIn trends:
{trend_report[:500]}

Post requirements:
1. START with a powerful 1-2 line hook that stops the scroll (no emojis at the very start — use a provocative statement or question)
2. Share 3-5 punchy insights, tips, or value-adds relevant to "{job_role}" professionals
3. Each insight on its own line, prefixed with a relevant emoji
4. End with a CTA inviting connection or comments (e.g. "DM me", "What do you think?")
5. Add 5-7 relevant hashtags on the last line
6. Total length: 150-250 words (LinkedIn sweet spot)
7. Tone: confident, conversational, authentic — NOT corporate or salesy

Return your response in this EXACT format:
HOOK: <the opening 1-2 lines only>
POST: <the full post text including the hook, insights, CTA, and hashtags>"""

    raw = _chat_gemini(prompt)
    out["raw_response"] = raw

    # Extract HOOK
    hook_match = re.search(r"HOOK:\s*(.+?)(?=\nPOST:|$)", raw, re.DOTALL | re.IGNORECASE)
    if hook_match:
        out["hook"] = hook_match.group(1).strip()

    # Extract POST
    post_match = re.search(r"POST:\s*(.+)", raw, re.DOTALL | re.IGNORECASE)
    if post_match:
        out["post"] = post_match.group(1).strip()
    else:
        # Fallback: use the entire raw response if markers not found
        out["post"] = raw.strip()

    # Clean up any stray label artifacts
    out["post"] = re.sub(r"^(hook|post):\s*", "", out["post"], flags=re.IGNORECASE).strip()
    out["hook"] = re.sub(r"^hook:\s*", "", out["hook"], flags=re.IGNORECASE).strip()

    return out
