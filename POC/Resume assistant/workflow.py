from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from tools.web_scraper import scrape_job_description
from tools.resume_parser import parse_resume_from_gcs
from tools.comparator import compare_resume_with_jd
from tools.suggester import generate_suggestions

# ----------------------------
# 1️⃣ Define State
# ----------------------------
class ResumeState(TypedDict):
    resume_gcs_uri: str
    job_description_url: Optional[str]
    job_description_text: Optional[str]
    resume_text: Optional[str]
    comparison_result: Optional[dict]
    suggestions: Optional[list]

# ----------------------------
# 2️⃣ Define Nodes
# ----------------------------
def web_scraper_node(state: ResumeState) -> ResumeState:
    if state.get("job_description_url"):
        jd_text = scrape_job_description(state["job_description_url"])
        state["job_description_text"] = jd_text
    return state

def resume_parser_node(state: ResumeState) -> ResumeState:
    resume_text = parse_resume_from_gcs(state["resume_gcs_uri"])
    state["resume_text"] = resume_text
    return state

def comparison_analyzer_node(state: ResumeState) -> ResumeState:
    comparison = compare_resume_with_jd(
        resume_text=state["resume_text"],
        job_description=state["job_description_text"]
    )
    state["comparison_result"] = comparison
    return state

def suggestion_generator_node(state: ResumeState) -> ResumeState:
    suggestions = generate_suggestions(state["comparison_result"])
    state["suggestions"] = suggestions
    return state

# ----------------------------
# 3️⃣ Build LangGraph
# ----------------------------
def build_resume_graph():
    graph = StateGraph(ResumeState)

    graph.add_node("scrape_jd", web_scraper_node)
    graph.add_node("parse_resume", resume_parser_node)
    graph.add_node("compare", comparison_analyzer_node)
    graph.add_node("suggest", suggestion_generator_node)

    graph.set_entry_point("scrape_jd")
    graph.add_edge("scrape_jd", "parse_resume")
    graph.add_edge("parse_resume", "compare")
    graph.add_edge("compare", "suggest")
    graph.add_edge("suggest", END)

    return graph.compile()
