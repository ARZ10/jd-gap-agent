import os
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from typing import TypedDict, Optional
from app.schemas import ExtractedRequirements
from dotenv import load_dotenv


load_dotenv()


model = ChatAnthropic(
    model="claude-haiku-4-5",
    api_key=os.environ["ANTHROPIC_API_KEY"]
)

structured_model = model.with_structured_output(ExtractedRequirements)


class GraphState(TypedDict):
    job_description: str
    extracted: Optional[ExtractedRequirements]


async def extract_node(state: GraphState) -> GraphState:
    result = await structured_model.ainvoke(state["job_description"])
    return {"extracted":result}


graph_builder = StateGraph(GraphState)
graph_builder.add_node("extract", extract_node)
graph_builder.set_entry_point("extract")
graph_builder.add_edge("extract", END)

compiled_graph = graph_builder.compile()
