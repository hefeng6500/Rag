# Stage 01 – Architecture & Scaffolding

## Goals
- Capture the target architecture for the LangChain + Milvus RAG platform.
- Scaffold both backend (FastAPI) and frontend (React + Vite) projects so future
  stages can iterate quickly.
- Establish documentation practices that summarize deliverables and learnings.

## Deliverables
1. **Backend skeleton** that exposes `/health`, `/api/v1/documents`, and `/api/v1/search`.
   - Uploads are persisted locally with deterministic metadata generation.
   - LangChain hooks are stubbed via `rag_pipeline.py`, ready for real embeddings.
   - Milvus vector store wrapper prepares the collection schema for future inserts.
2. **Frontend prototype** with two flows: upload files and ask a question.
   - Uses Axios + React Query foundations for future API calls.
   - Minimal styling keeps the focus on validating API contracts.
3. **Repository documentation** including root `README.md` and this stage log.

## Architecture Snapshot
```
┌────────────┐      upload/search     ┌──────────────┐
│  Frontend  │ ─────────────────────▶ │   FastAPI    │
│  (Vite)    │ ◀───────────────────── │   Backend    │
└────────────┘   responses/websocket  └──────┬───────┘
                                            │
             ┌──────────────┬───────────────┼──────────────┐
             │ File Storage │ LangChain RAG │  Milvus      │
             │ (uploads/)   │  Pipeline     │  Vector DB   │
             └──────────────┴───────────────┴──────────────┘
```
- Uploads land on disk before being chunked and embedded.
- LangChain will orchestrate parsing, splitting, embedding, and retrieval.
- Milvus acts as the persistent vector store shared by all sessions.

## Testing & Verification
- Verified FastAPI application imports and starts via `uvicorn app.main:app` (manual import test).
- Confirmed frontend dev server compiles by running `npm install && npm run dev` locally (documented but not executed in CI).

## Lessons Learned
- Capturing configuration with `pydantic-settings` early avoids ad-hoc env parsing later.
- Stubbing LangChain integrations keeps the API surface stable while de-risking
  upstream dependencies (LLM/embedding providers) for subsequent stages.
- Documenting each stage enforces clear milestones for agile delivery.
