from pydantic import BaseModel, Field


class ExtractedRequirements(BaseModel):
    required_skills: list[str] = Field(
        description="Concrete technical skills, tools, or technologies explicitly required in the job posting."
    )
    nice_to_have_skills: list[str] = Field(
        description="Skills listed as preferred, bonus, or an asset, not strictly required"
    )


