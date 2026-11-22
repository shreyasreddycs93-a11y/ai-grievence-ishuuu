# GrievanceAI (CivicSahayak)

An AI-assisted civic complaint portal, built as a team for Smart India Hackathon
(problem SIH260011). Citizens report a problem as text, voice or a photo, in
English, Hindi or a regional language. The AI layer works out which municipal
department it belongs to and how urgent it is, and the backend routes it to
officers and tracks it to resolution with SLA-based escalation.

My part was the AI layer (`ai_service/`).

## How a complaint flows

1. **Intake.** Voice is transcribed, photos are described in words, and
   regional-language or Hinglish text is normalised to clear English.
2. **Classification.** An LLM (Gemini, with a fallback chain) picks one of 9
   categories (water supply, roads, sanitation, electricity, streetlights,
   drainage, garbage, parks, other) and a priority (low to critical), with a
   confidence score. Low-confidence results go to a human instead of being
   routed blindly.
3. **Splitting.** A complaint that covers two departments can be split into
   separate tickets.
4. **Tracking.** The backend stores the ticket with a text embedding (pgvector),
   assigns it, and escalates it if the SLA is missed.

## Accuracy

On 200 held-out test complaints the classifier never saw during prompt design:
**93% correct department, 83.5% correct priority**, no fallbacks
(`ai_service/tests/holdout_results/holdout_raw_batch200.json`). See
`ai_service/README.md` for how this is measured and why the in-prompt examples
are kept separate from the test set.

## Repository layout

| Folder | What is in it |
| --- | --- |
| `ai_service/` | AI layer: transcription, normalisation, image description, classification, department splitting, embeddings, and the accuracy test scripts |
| `Backend/` | FastAPI + PostgreSQL (pgvector) + SQLAlchemy API, with an APScheduler job for SLA escalation |
| `Frontend/` | Citizen app (React, TypeScript, Vite, Tailwind) |
| `OfficerFrontend/` | Officer dashboard (React, TypeScript, Vite) |
| `Landing/` | Landing page |
| `docs/` | Design notes |

## Run it locally

Needs Python, Node.js and Docker (for Postgres with pgvector).
`Backend/README.md` has the full steps. On Windows, `start-demo.bat` starts
Postgres, builds the three frontends and starts the server once everything is installed.

You need a free Gemini API key (https://aistudio.google.com/) in `.env`
(see `.env.example`). A Groq key is optional.

## Tech stack

Python, Gemini and Groq LLM APIs, prompt design, text embeddings, FastAPI,
PostgreSQL + pgvector, React, TypeScript, Docker, Render.
