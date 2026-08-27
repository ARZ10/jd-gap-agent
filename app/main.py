from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.db import AsyncSessionLocal
from app.models import Analysis
from app.db import engine, Base
from app.graph import compiled_graph


app = FastAPI(title="jd-gap-agent")



class AnalyzeRequest(BaseModel):
    job_description: str


class AnalyzeResponse(BaseModel):
    id: int
    job_description: str
    matched_skills: list[str]
    missing_skills: list[str]

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    async with AsyncSessionLocal() as session:
        new_analysis = Analysis(job_description=payload.job_description)
        result = await compiled_graph.ainvoke(
            {"job_description": payload.job_description,
             "extracted": None,
             "error": None,
             "gap_analysis": None}
        )
        if result.get("error"):
            raise HTTPException(status_code=422, detail=result["error"])

        new_analysis.extracted_requirements=result["gap_analysis"]

        session.add(new_analysis)
        await session.commit()
        await session.refresh(new_analysis)


    return AnalyzeResponse(id=new_analysis.id,
                           job_description=new_analysis.job_description,
                           matched_skills=new_analysis.extracted_requirements["matched"],
                           missing_skills=new_analysis.extracted_requirements["missing"],
    )