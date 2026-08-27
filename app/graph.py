import os
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from typing import TypedDict, Optional
from app.schemas import ExtractedRequirements
from app.tools import analyze_gap
from dotenv import load_dotenv


load_dotenv()
# Load .env key-value pair in the environmental variable.

MY_SKILLS = ["Python", "FastAPI", "Docker", "NumPy", "Pandas", "Machine Learning", "PostgreSQL", "Git"]


model = ChatAnthropic(
    model="claude-haiku-4-5",
    api_key=os.environ["ANTHROPIC_API_KEY"]
)
# set the LLM by using its API key.

structured_model = model.with_structured_output(ExtractedRequirements)

class GraphState(TypedDict):
    job_description: str
    extracted: Optional[ExtractedRequirements]
    gap_analysis: Optional[dict]
    error: Optional[str]


async def extract_node(state: GraphState) -> GraphState:
    result = await structured_model.ainvoke(state["job_description"])
    return {"extracted":result}


def match_node(state: GraphState) -> GraphState:
    result = analyze_gap(state["extracted"].required_skills, MY_SKILLS)
    return {"gap_analysis": result}


def route_after_extract(state: GraphState) -> str:
    if not state['extracted'] or not state['extracted'].required_skills:
        return "error"
    return "match"

def error_node(state: GraphState) -> GraphState:
    return {"error": "No requirements could be extracted from the job description."}


graph_builder = StateGraph(GraphState)
graph_builder.add_node("extract", extract_node)
graph_builder.add_conditional_edges(
    "extract",
    route_after_extract,
    {
        "match": "match",
        "error": "error"
    }
)
graph_builder.add_node("match", match_node)
graph_builder.add_node("error", error_node)
graph_builder.set_entry_point("extract")
graph_builder.add_edge("error", END)
graph_builder.add_edge("match", END)


compiled_graph = graph_builder.compile()
