from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from langgraph.graph import StateGraph
from langgraph.constants import START,END
from langchain_community.tools import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel,Field
from class_def import ReportState,SectionState
from typing import List,TypedDict,Literal
import asyncio
from dotenv import load_dotenv
load_dotenv()

llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.7)
researchers=ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite",temperature=0.4)
search_tool=TavilySearchResults(max_result=2)
tools=[search_tool]
# agent=researchers.bind_tools(tools)

def generate_message_plan(state:ReportState):
    prompt=ChatPromptTemplate.from_messages([
        ("system","You are a report planning agent. Your task is to generate a structured plan with atmost 2 sections for a given topic. The plan should be comprehensive and well-organized"),
        ("human","Generate a report plan for the topic: {input}") #change max section
    ])
    class Sections(BaseModel):
        sections:List[SectionState]=Field(description="List of sections for the report atmost 2") #change max section

    structured_llm = llm.with_structured_output(Sections)
    formatted_prompt=prompt.format(input=state['topic'])
    response=Sections.model_validate(structured_llm.invoke(formatted_prompt))
    return {"sections":response.sections,"messages":HumanMessage(content="Sections Generated !")}

async def research_agent(state:ReportState):
    print(f"Agent {len(state["completed_sections"])} Called")
    section_to_research=state["sections"][len(state["completed_sections"])]
    print(f"Section to research {section_to_research}")
    prompt=[
        SystemMessage(content="You are a research agent. Your task is to research a given topic and provide a detailed summary."),
        HumanMessage(content=f"Research the following topic for the section '{section_to_research.name}', description '{section_to_research.description}'"),
    ]
    # response= await agent.ainvoke(prompt)
    response=await researchers.ainvoke(prompt)
    print(f"Agent {len(state["completed_sections"])} Response {response}")
    return {"messages":response}

def research_section_entry(state: ReportState):
    """Entry point for researching a section."""
    print("Research Section Entry")
    if len(state["completed_sections"]) < len(state["sections"]):
        return {"messages": [HumanMessage(content="Starting research for the next section.")]}
    else:
        return {"messages": [HumanMessage(content="All sections researched.")]}

def should_continue_research(state: ReportState) -> Literal["research_agent", "compile_final_report"]:
    """Determine whether to continue researching or compile the final report."""
    if len(state["completed_sections"]) < len(state["sections"]):
        return "research_agent"
    else:
        return "compile_final_report"

def update_completed_sections(state:ReportState):
    last_message=state["messages"][-1].content
    section_index=len(state["completed_sections"])
    updated_section=state["sections"][:] #shallow copy, seperate list
    updated_section[section_index].content=str(last_message)
    return {
        "completed_sections":[updated_section[section_index]],
        "sections":updated_section
    }

async def compile_final_report(state:ReportState):
    # Introduction report
    # Conclusion report
    all_section="\n\n".join([s.content for s in state["sections"]])
    return{
        "final_report":all_section
    }

def routing_function(state:ReportState):
    last_message=state["messages"][-1]
    if isinstance(last_message,AIMessage) and last_message.tool_calls:
        return "research_tools"
    else:
        # return END
        return "update_completed_sections"

graph=StateGraph(ReportState)
toolnode=ToolNode(tools=tools)
graph.add_node("generate_message_plan",generate_message_plan)
graph.add_node("research_agent",research_agent)
graph.add_node("research_section_entry",research_section_entry)
# graph.add_node("should_continue_research",should_continue_research)
graph.add_node("update_completed_sections",update_completed_sections)
graph.add_node("compile_final_report",compile_final_report)
# graph.add_node("research_tools", toolnode)

graph.add_edge(START,"generate_message_plan")
graph.add_edge("generate_message_plan","research_section_entry")
graph.add_conditional_edges(
    "research_section_entry",
    should_continue_research,
    {
        "research_agent":"research_agent",
        "compile_final_report":"compile_final_report"
    }
)
# graph.add_edge("research_tools","research_agent")
# graph.add_conditional_edges(
#     "research_agent",
#     routing_function,
#     {
#         "research_tools":"research_tools",
#         "update_completed_sections":"update_completed_sections"
#         # END:END
#     }
# )
graph.add_edge("research_agent","update_completed_sections")
graph.add_edge("update_completed_sections","research_section_entry")
graph.add_edge("compile_final_report",END)
app=graph.compile()
# print(app.get_graph().draw_ascii())
# print(app.get_graph().draw_mermaid())

async def main():
    initial_topic = "What is K.V cache in large language models ? How does it help ?"

    initial_state = {
        "topic": initial_topic,
        "sections":[],
        "completed_sections": [],
        "messages": [],
        "final_report":""
    }

    final_state = await app.ainvoke(
        initial_state,
        config={"recursion_limit": 50} #1+6*4 = 26 > 25
    )

    print("\n--- FINAL REPORT ---")
    print(final_state['final_report'])

if __name__=="__main__":
    print("Graph")
    asyncio.run(main())
