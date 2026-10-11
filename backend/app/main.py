from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import db, llm
from .schemas import Entry, EntryCreate, EntrySummary


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="AI Content Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/entries", response_model=Entry, status_code=201)
def create_entry(body: EntryCreate):
    try:
        summary, tags = llm.summarize(body.text)
    except llm.LLMConfigError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except llm.LLMServiceError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return db.create_entry(body.text, summary, tags)


@app.get("/entries", response_model=list[EntrySummary])
def list_entries():
    return db.list_entries()


@app.get("/entries/{entry_id}", response_model=Entry)
def get_entry(entry_id: int):
    entry = db.get_entry(entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry
