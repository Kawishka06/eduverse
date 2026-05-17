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

**Frontend (example)** — see `frontend/.env.example`

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_SITE_URL=https://eduverse-gold-mu.vercel.app
API_URL=https://your-deployed-api.example.com
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Deploy frontend on Vercel (GitHub import)

1. Import the repo on [vercel.com](https://vercel.com) and set **Root Directory** to `frontend`.
2. Add environment variables (Production + Preview):

   | Variable | Value |
   |----------|--------|
   | `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
   | `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase anon key |
   | `NEXT_PUBLIC_SITE_URL` | `https://eduverse-gold-mu.vercel.app` |
   | `API_URL` | HTTPS URL of your deployed FastAPI backend |

3. In **Supabase → Authentication → URL configuration**, set Site URL and Redirect URLs to your Vercel domain (e.g. `https://eduverse-gold-mu.vercel.app/auth/callback`).
4. Deploy the **backend** separately (Render, Railway, Fly.io, etc.) with `ENVIRONMENT=production`, `SUPABASE_JWT_SECRET`, and `CORS_ORIGINS=https://eduverse-gold-mu.vercel.app`.
5. Redeploy Vercel after setting `API_URL`. The app proxies API calls through `/api/backend` so the browser sends cookies and avoids CORS issues.

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
