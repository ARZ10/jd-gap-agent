import uuid
from fastapi import FastAPI
from pydantic import BaseModel
from app.db import AsyncSessionLocal
from app.models import Analysis
from app.db import engine, Base


app = FastAPI(title="jd-gap-agent")



class AnalyzeRequest(BaseModel):
    job_description: str


class AnalyzeResponse(BaseModel):
    id: int
    job_description: str

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    async with AsyncSessionLocal() as session:
        new_analysis = Analysis(job_description=payload.job_description)
        session.add(new_analysis)
        await session.commit()
        await session.refresh(new_analysis)
    # placeholder: just echoes input back for now.
    # Day 3 replaces this line with the langGraph call.
    return AnalyzeResponse(id=new_analysis.id,job_description=new_analysis.job_description)