import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from app.main import app
from app. schemas import ExtractedRequirements
from app.db import engine, Base

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


@pytest.mark.asyncio
async def test_analyze_success():
    fake_result = ExtractedRequirements(
        required_skills=["FastAPI", "Python", "Docker"],
        nice_to_have_skills=["Redis"]
    )
    mock_model = AsyncMock()
    mock_model.ainvoke = AsyncMock(return_value=fake_result)

    #builds a fake/expected output object.
    with patch("app.graph.structured_model", new=mock_model):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/analyze", json={"job_description": "some real JD text"})

    assert response.status_code == 200
    body = response.json()
    assert "python" in body["matched_skills"]



@pytest.mark.asyncio
async def test_analyze_failure():
    fake_result = ExtractedRequirements(
        required_skills=[],
        nice_to_have_skills=[],
    )

    mock_model = AsyncMock()
    mock_model.ainvoke = AsyncMock(return_value=fake_result)

    with patch("app.graph.structured_model", new=mock_model):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.post("/analyze", json={"job_description": "garbage text"})

    assert response.status_code == 422
    body = response.json()
    assert body["detail"] == "No requirements could be extracted from the job description."

