from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from langchain_core.tools import structured
from langgraph.graph import StateGraph
from langgraph.constants import START,END
from langchain_community.tools import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel,Field
from .class_def import ReportState,SectionState,SectionOutput
from typing import List,TypedDict,Literal
import asyncio
from dotenv import load_dotenv
from .research_subgraph import app as research_app
load_dotenv()

class SupervisorLLM():
    def __init__(self,supervisor):
        self.llm=supervisor

    def __call__(self,state:ReportState):
        # print("Called")
        prompt=ChatPromptTemplate.from_messages([
            ("system","You are a report planning agent. Your task is to generate a structured plan with atmost 2 sections for a given topic. The plan should be comprehensive and well-organized"),
            ("human","Generate a report plan for the topic: {input}") #change max section
        ])
        formatted_prompt=prompt.format(input=state['topic'])
        class Sections(BaseModel):
            sections:List[SectionOutput]=Field(description="List of sections for report atmost 2")
        structured_llm=self.llm.with_structured_output(Sections)
        response=Sections.model_validate(structured_llm.invoke(formatted_prompt))
        print(response)
        return{
            "sections":response.sections
        }

def call_researcher(state:ReportState):
    """
    Calls the research subgraph for each section to gather detailed content
    """
    updated_section=[]
    for section in state["sections"]:
        research_state={
            "name":section.name,
            "description":section.description,
            "content":[HumanMessage(content="Research the topic strictly based on name and description")]
        }
        result=research_app.invoke(research_state)
        print("RESEARCHER")
        print(result)
        updated_section.append(result["content"][-1].content)
    return{
        "final_report":updated_section
    }

# def print_final_report(state:ReportState):

supervisor=ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.7)
agent=SupervisorLLM(supervisor=supervisor)
graph=StateGraph(ReportState)
graph.add_node("ModelReply",agent)
graph.add_node("call_researcher",call_researcher)
graph.set_entry_point("ModelReply")
graph.add_edge("ModelReply","call_researcher")
graph.add_edge("call_researcher",END)
supervisor_graph=graph.compile()
# print(app.get_graph().draw_ascii())

if __name__=="__main__":
    initial_topic = "What is GRPO in large language models ? How does it help ?"

    initial_state = {
        "topic": initial_topic,
        "sections":[],
        "completed_sections": [],
        "messages": [],
        "final_report":""
    }
    result=supervisor_graph.invoke(initial_state)
    print(result)
