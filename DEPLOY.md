# 🚀 Deployment Guide — LinkedIn Profile Optimizer AI

> Deploy to **Streamlit Community Cloud** and get a live public URL in under 5 minutes — for free.

---

## Before You Start — Checklist

- [ ] You have a [GitHub](https://github.com) account
- [ ] You have a [Groq API key](https://console.groq.com) (free)
- [ ] You have a [Gemini API key](https://aistudio.google.com/app/apikey) (free)
- [ ] Python 3.10+ installed locally (only needed to verify the project runs)

---

## Step 1 — Prepare Your Local Project

Make sure the project folder looks exactly like this:

```
linkedin-optimizer/
├── app.py
├── agents.py
├── requirements.txt
├── .env                  ← local only, will NOT be pushed to GitHub
├── .env.example
└── .streamlit/
    ├── config.toml
    └── secrets.toml      ← local only, will NOT be pushed to GitHub
```

### Create a `.gitignore` to protect your API keys

In the `linkedin-optimizer/` folder, create a file called `.gitignore`:

```
# Never commit these
.env
.streamlit/secrets.toml
__pycache__/
*.pyc
.venv/
```

> **Critical:** If you push `.env` or `secrets.toml` to a public GitHub repo, your API keys will be exposed and automatically revoked by GitHub's secret scanning. Always add them to `.gitignore` first.

---

## Step 2 — Push to GitHub

### Option A — Using GitHub Desktop (easiest)

1. Download and install [GitHub Desktop](https://desktop.github.com/)
2. Click **File → Add Local Repository** → select your `linkedin-optimizer/` folder
3. If it says "not a git repository", click **Initialize Repository**
4. Click **Publish Repository** (top bar)
5. Give it a name (e.g. `linkedin-optimizer`), set visibility to **Public**, click **Publish**

### Option B — Using the terminal

```bash
# 1. Navigate to your project folder
cd /path/to/linkedin-optimizer

# 2. Initialise git (skip if already a repo)
git init

# 3. Stage everything
git add .

# 4. First commit
git commit -m "feat: initial LinkedIn optimizer with Groq + Gemini"

# 5. Create a new repo on GitHub (requires GitHub CLI)
gh repo create linkedin-optimizer --public --source=. --push

# --- OR if you already created the repo on github.com ---
git remote add origin https://github.com/YOUR_USERNAME/linkedin-optimizer.git
git branch -M main
git push -u origin main
```

After this step, your code should be visible at:  
`https://github.com/YOUR_USERNAME/linkedin-optimizer`

---

## Step 3 — Sign In to Streamlit Community Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **Sign in with GitHub**
3. Authorize Streamlit to access your GitHub account
4. You land on the **My Apps** dashboard

---

## Step 4 — Create a New App

1. Click the **New app** button (top right)
2. You'll see a form — fill it in:

   | Field | Value |
   |-------|-------|
   | **Repository** | `YOUR_USERNAME/linkedin-optimizer` |
   | **Branch** | `main` |
   | **Main file path** | `app.py` |
   | **App URL** (optional) | choose a custom slug, e.g. `linkedin-optimizer-ai` |

3. Click **Advanced settings** (important — do this before deploying)

---

## Step 5 — Add Your API Keys as Secrets

This is the most important step. Since `.env` is not on GitHub, you must give Streamlit your keys through its secure secrets panel.

1. Inside **Advanced settings**, find the **Secrets** text box
2. Paste exactly this (replace with your real keys):

```toml
GROQ_API_KEY = "your-groq-api-key"
GEMINI_API_KEY = "your-gemini-api-key"
```

> **How it works:** Streamlit Cloud stores these securely and injects them as `st.secrets["GROQ_API_KEY"]` at runtime. The `_get_secret()` function in `agents.py` reads from `st.secrets` first, then falls back to `os.environ` — so the same code works locally and in the cloud without any changes.

3. Click **Save**

---

## Step 6 — Deploy

1. Click **Deploy!**
2. Streamlit will:
   - Clone your GitHub repo
   - Install everything in `requirements.txt`
   - Start the app server
3. You'll see a live build log — it takes about **60–90 seconds**
4. Once it says **"Your app is live!"**, click the URL shown

Your app is now live at:
```
https://YOUR_SLUG.streamlit.app
```

---

## Step 7 — Verify It Works

Once the app loads in your browser:

1. You should see the **Gruvbox dark hero banner** with Groq/Gemini badges
2. The sidebar should show the **Agent → Model** map
3. The chat should ask: *"What job role are you targeting?"*
4. Type a role (e.g. `Product Manager`) and press Enter
5. Complete all 4 questions
6. Watch the step bar run through all 4 agents — the full pipeline should finish in **under 30 seconds**

✅ If results appear with a side-by-side card comparison and a score donut — you're live!

---

## Managing Your Deployed App

### Updating the app after code changes

Any `git push` to the `main` branch **automatically redeploys**:

```bash
# Make your changes, then:
git add .
git commit -m "fix: improved rewriter prompt"
git push
```

Streamlit Cloud detects the push and rebuilds within ~30 seconds.

### Updating secrets

1. Go to [share.streamlit.io](https://share.streamlit.io) → your app
2. Click the **⋮ menu** → **Settings** → **Secrets**
3. Edit and save — the app restarts automatically

### Rebooting / clearing cache

1. App dashboard → **⋮ menu** → **Reboot app**

### Taking the app offline

1. App dashboard → **⋮ menu** → **Delete app** (permanent) or **Pause app** (reversible)

---

## Troubleshooting Deployment Issues

### Build fails — `ModuleNotFoundError`

The package is missing from `requirements.txt`. Your `requirements.txt` should contain:

```
streamlit>=1.35.0
groq>=0.9.0
google-genai>=1.0.0
ddgs>=0.1.0
python-dotenv>=1.0.0
```

Push the fix and Streamlit will auto-rebuild.

---

### App loads but agents return errors

**Check your secrets** — the most common cause. In the Streamlit Cloud dashboard:
- Settings → Secrets → confirm both keys are present and spelled exactly:
  - `GROQ_API_KEY`
  - `GEMINI_API_KEY`

---

### `[Groq Error] 401 Unauthorized`

Your Groq key is wrong or expired. Generate a new one at [console.groq.com](https://console.groq.com) and update it in Streamlit secrets.

---

### `[Gemini Error] 429 RESOURCE_EXHAUSTED` (in logs)

This is handled automatically — Agent 3 silently falls back to Groq. No action needed; the pipeline will still complete.

---

### DuckDuckGo search errors

Streamlit Cloud's IP ranges are sometimes rate-limited by DuckDuckGo. If this happens repeatedly:
- The trend report will be shorter but the rest of the pipeline still runs
- It typically self-resolves within a few minutes

---

### App is slow on first load ("cold start")

Free Streamlit Cloud apps sleep after 7 days of inactivity. The first load after sleep takes ~15–20 seconds while the container spins up. Subsequent loads are instant.

## Alternative: Deploy to Railway

While Streamlit Community Cloud is the easiest, you can also deploy this project to [Railway](https://railway.app) if you need a custom domain or non-sleeping app.

The project is already configured for Railway with the included `Procfile` and `railway.toml`.

1. Sign up for [Railway](https://railway.app) and connect your GitHub account.
2. Click **New Project** → **Deploy from GitHub repo**.
3. Select your `linkedin-optimizer` repository.
4. Once added, click on the project box, go to **Variables**, and add:
   - `GROQ_API_KEY`
   - `GEMINI_API_KEY`
5. Go to the **Settings** tab → **Networking** → Click **Generate Domain**.
6. Railway will build and deploy the app automatically using Nixpacks.

---

## Free Tier Limits

| Resource | Streamlit Community Cloud (Free) |
|----------|----------------------------------|
| Apps | 3 public apps per account |
| RAM | 1 GB |
| CPU | Shared |
| Sleep | After 7 days inactive |
| Custom domain | ❌ (use `.streamlit.app` subdomain) |
| Private repos | ✅ supported |

| Resource | Groq Free Tier |
|----------|---------------|
| Requests/min | 30 RPM |
| Tokens/min | ~14,400 TPM |
| Daily limit | ~7,000 requests |

| Resource | Gemini Free Tier |
|----------|-----------------|
| Requests/min | 15 RPM |
| Tokens/min | 1M TPM |
| Daily limit | 1,500 requests |

> All limits are well within range for personal/demo use. The full pipeline uses ~3 Groq calls and 1 Gemini call per run.

---

## Your Live App URL

Once deployed, your app lives at:

```
https://<your-slug>.streamlit.app
```

Share this link with anyone — no installation, no API keys required on their end.
