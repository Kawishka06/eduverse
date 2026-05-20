# EduVerse AI

A multimodal AI-powered social learning platform built with [fal.ai](https://fal.ai).

EduVerse combines social learning, creator tools, and AI-assisted education—meme generation, tutoring, and image-to-video—in one place for students and content creators.

---

## Core Features

| Feature | Description |
|--------|-------------|
| **Authentication** | Supabase Auth (email/password) + API session sync |
| **Dashboard** | Role-aware workspace with stats, library, and quick actions |
| **Roles** | Student, creator, and admin with role-based access |
| **AI Meme Generation** | Text prompts → images via fal.ai |
| **Learning Agent** | Custom ReAct agent with calculator, code review, and web search tools |
| **Lesson Characters** | Student- and teacher-designed mascots with fal-generated reference art |
| **Lesson Video Studio** | Upload study materials → scripted scenes → TTS + image-to-video clips |
| **AI Tutor** | Chat UI powered by the learning agent (requires sign-in) |
| **Image-to-Video** | Per-scene clips in the lesson pipeline |
| **Social Feed** | Posts, likes, and comments |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, Tailwind CSS |
| Backend | FastAPI |
| AI | fal.ai APIs, LLM |
| Database | Supabase (Auth + Postgres via API) |
| Vector DB | Pinecone |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                         │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST / API
┌───────────────────────────▼─────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────────┐  │
│  │  Auth   │ │ Content │ │Characters│ │ Learning Agent   │  │
│  │ Service │ │Materials│ │ Service  │ │ + Orchestrator   │  │
│  └────┬────┘ └────┬────┘ └────┬─────┘ └────────┬─────────┘  │
└───────┼───────────┼───────────┼───────────────┼────────────┘
        │           │           │               │
        │           │           │               │
        └───────────┴───────────┴───────────────┘
                            │
                            ▼
                      Supabase
                   (Auth + Database)
                            │
                            ▼
                      fal.ai / LLM
```

### Modular Services

- **Auth** — Supabase Auth sessions, profile sync, role enforcement
- **Content** — Posts, media metadata, creator workflows
- **Social** — Feed, likes, comments, engagement
- **AI Orchestrator** — Meme generation, lesson video pipeline, character art, vision, TTS, and image-to-video
- **Learning Agent** — Tool-using tutor loop (calculator, code review, search) via fal `any-llm`
- **Characters** — Custom lesson mascots with generated reference sheets
- **Content / Materials** — Student uploads (PDF, text, images) with text extraction for lessons

The AI Orchestrator centralizes fal.ai calls; the Learning Agent adds pedagogy, tools, and character persona on top.

---

## Roles

| Role | Capabilities |
|------|----------------|
| **Student** | Learning agent, characters, lesson studio, feed, library |
| **Teacher** | Publish class characters, announcements, lesson studio |
| **Creator** | Slide studio, memes, lesson studio, library |
| **Admin** | User moderation, platform configuration, analytics |

---

## Project Structure (planned)

```
eduverse/
├── frontend/          # Next.js + Tailwind
├── backend/           # FastAPI
│   ├── services/
│   │   ├── auth/
│   │   ├── content/
│   │   ├── social/
│   │   └── ai/        # AI Orchestrator
│   └── ...
├── README.md
└── ...
```

---

## Prerequisites

- Node.js 18+
- Python 3.11+
- Supabase project (database + auth)
- Pinecone account
- fal.ai API key
- LLM provider credentials (as configured in the AI Orchestrator)

---

## Environment Variables

Create `.env` files for frontend and backend (do not commit secrets).

**Backend (example)**

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret
FAL_KEY=your-fal-key
FAL_CHARACTER_MODEL=fal-ai/flux/schnell
AGENT_MAX_TURNS=6
SEARCH_PROVIDER=tavily
TAVILY_API_KEY=your-tavily-key
```

See `backend/.env.example` for all AI and search variables.

The backend uses the **Supabase Python client** (service role) for all database access — no local PostgreSQL, SQLite, or `DATABASE_URL` required.

**Frontend (Netlify)** — see `frontend/.env.example`

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_SITE_URL=https://your-app.netlify.app
NEXT_PUBLIC_API_URL=https://your-eduverse-api.vercel.app
```

**Backend (Vercel)** — see `backend/.env.example`

```env
ENVIRONMENT=production
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
SUPABASE_JWT_SECRET=...
FAL_KEY=...
CORS_ORIGINS=http://localhost:3000,https://your-app.netlify.app
API_PUBLIC_URL=https://your-eduverse-api.vercel.app
FRONTEND_PUBLIC_URL=https://your-app.netlify.app
```

### Deploy: backend on Vercel + frontend on Netlify

**1. Vercel (FastAPI API)**

1. [vercel.com](https://vercel.com) → New Project → import this GitHub repo.
2. Set **Root Directory** to `backend`.
3. Add all variables from `backend/.env.example` (Production).
4. Deploy. Note the URL, e.g. `https://eduverse-api.vercel.app`.
5. Test: `https://your-api.vercel.app/health` → `{"status":"ok",...}`.

**2. Netlify (Next.js UI)**

1. [netlify.com](https://netlify.com) → Add new site → Import from Git.
2. Set **Base directory** to `frontend`.
3. Build command: `npm run build` (also set in `frontend/netlify.toml`).
4. Environment variables:

   | Variable | Value |
   |----------|--------|
   | `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key |
   | `NEXT_PUBLIC_SITE_URL` | Your Netlify URL |
   | `NEXT_PUBLIC_API_URL` | Your **Vercel API** URL from step 1 |

5. Deploy.

**3. Supabase auth URLs**

In **Authentication → URL configuration**:

- Site URL: `https://your-app.netlify.app`
- Redirect URLs: `https://your-app.netlify.app/auth/callback`

**Serverless limits (Vercel API):** Lesson video generation (long jobs, ffmpeg, disk files) and live feed WebSockets work best on a long-running host (Railway/Render). On Vercel serverless, memes/tutor/posts/subscriptions usually work; lesson studio and live feed may be limited.

**Vercel build error `cd frontend && npm install exited with 1`:** Your project **Root Directory** is already `frontend`, but the install command still runs `cd frontend` (which does not exist). Fix: Vercel → Settings → Build & Deployment → set **Install Command** to `npm install` (or leave empty). Do **not** use `cd frontend && npm install` when Root Directory is `frontend`. The API project should use Root Directory `backend` only (no npm).

**Netlify:** Use Base directory `frontend` — build is `npm run build` from `netlify.toml` (no `cd frontend`).

**Supabase setup**

1. Create a project at [supabase.com](https://supabase.com)
2. Enable **Email** auth under Authentication → Providers
3. Run base schema: paste **`supabase/COMPLETE_SETUP.sql`** in the SQL Editor (includes lesson tables + storage), **or** run migrations `001`–`006` then lesson migrations below.
4. **Lesson features (required for Characters + Lesson Studio):** In SQL Editor, paste and run **`supabase/RUN_LESSON_MIGRATIONS.sql`** (combines `007` + `008`). Safe to re-run.
5. Verify: open `http://localhost:8000/health/db` — `lessonFeaturesReady` should be `true`.
6. Copy **Project URL**, **anon key**, and **JWT secret** (Settings → API) into your `.env` files
7. Set `SUPABASE_JWT_SECRET` in the backend `.env` so the API accepts Supabase session tokens

**Optional CLI migrate** (if you add the database URI to `backend/.env`):

```env
SUPABASE_DB_URL=postgresql://postgres.[ref]:[PASSWORD]@...pooler.supabase.com:6543/postgres
```

```bash
cd backend
pip install psycopg2-binary python-dotenv
python scripts/apply_lesson_migrations.py
```

Get the URI from Supabase Dashboard → **Settings** → **Database** → **Connection string** (URI).

---

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) for the marketing page, [http://localhost:3000/register](http://localhost:3000/register) to create an account, and [http://localhost:3000/dashboard](http://localhost:3000/dashboard) after sign-in. API docs: [http://localhost:8000/docs](http://localhost:8000/docs).

Copy `frontend/.env.example` and `backend/.env.example` to `.env.local` / `.env` and fill in your Supabase credentials before signing up.

---

## AI Flows

1. **Meme generation** — Client → `/ai/meme` → Orchestrator → fal text-to-image → library post
2. **Learning agent** — Client → `/ai/agent/chat` → ReAct loop + tools → fal `any-llm`
3. **Character design** — Client → `/characters` → LLM bible + fal reference image → Supabase
4. **Lesson video** — Upload → `/content/materials` → `/ai/lesson-video` → script → scene images → TTS → image-to-video per scene
5. **AI tutor (legacy path)** — `/ai/tutor` wraps the learning agent for the chat UI

---

## License

Specify your license here (e.g. MIT, proprietary).

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit changes and open a pull request

---

Built with fal.ai for multimodal AI workloads.
