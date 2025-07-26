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
search_tool=TavilySearchResults(max_results=1)
tools=[search_tool]
agent=researchers.bind_tools(tools)

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

def research_agent(state:ReportState): #removed async
    print(f"Agent {len(state["completed_sections"])} Called")
    section_to_research=state["sections"][len(state["completed_sections"])]
    print(f"Section to research {section_to_research}")
    print("\n")
    prompt=[
        SystemMessage(content="You are a research agent. Your task is to research a given topic and provide a detailed summary. You have web search tool in case needed"),
        HumanMessage(content=f"Research the following topic for the section '{section_to_research.name}', description '{section_to_research.description}'"),
    ]
    response= agent.invoke(prompt)
    # response=await researchers.ainvoke(prompt)
    print(f"Agent {len(state["completed_sections"])} Response {response}")
    print("\n")
    return {"messages":response}

def process_search_results(state: ReportState):
    """Process search results and generate final summary"""
    print("Processing search results...")
    section_to_research = state["sections"][len(state["completed_sections"])]

    # Get the conversation history including search results
    conversation_history = state["messages"]

    # Create a summarization prompt
    prompt = [
        SystemMessage(content="You are a research summarization agent. Based on the search results provided in the conversation, create a comprehensive and well-structured summary for the report section."),
        HumanMessage(content=f"Based on all the search results above, provide a detailed, comprehensive summary for the section '{section_to_research.name}' with description '{section_to_research.description}'. Make it informative and well-organized.")
    ]

    # Combine conversation history with summarization prompt
    full_conversation = conversation_history + prompt
    response = researchers.invoke(full_conversation)
    print(f"Summary generated: {response}")
    return {"messages": response}

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

def compile_final_report(state:ReportState):
    # Introduction report
    # Conclusion report
    all_section="\n\n".join([s.content for s in state["sections"]])
    return{
        "final_report":all_section
    }

def routing_function(state:ReportState):
    last_message=state["messages"][-1]
    if isinstance(last_message,AIMessage) and last_message.tool_calls:
        print("TOOLS CALLED")
        return "research_tools"
    else:
        # return END
        return "update_completed_sections"

#Break into two subgraphs
graph=StateGraph(ReportState)
toolnode=ToolNode(tools)
graph.add_node("generate_message_plan",generate_message_plan)
graph.add_node("research_agent",research_agent)
graph.add_node("research_section_entry",research_section_entry)
graph.add_node("process_search_results", process_search_results) #claude
graph.add_node("update_completed_sections",update_completed_sections)
graph.add_node("compile_final_report",compile_final_report)
graph.add_node("research_tools", toolnode)

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
graph.add_conditional_edges(
    "research_agent",
    routing_function,
    {
        "research_tools":"research_tools",
        "update_completed_sections":"update_completed_sections"
        # END:END
    }
)
# graph.add_edge("research_agent","update_completed_sections") #if no web search
# graph.add_edge("research_agent","research_tools") #web search raw
# graph.add_edge("research_tools","update_completed_sections") #web search raw
graph.add_edge("research_tools", "process_search_results")
graph.add_edge("process_search_results", "update_completed_sections")
graph.add_edge("update_completed_sections","research_section_entry")
graph.add_edge("compile_final_report",END)
app=graph.compile()
print(app.get_graph().draw_ascii())
print(app.get_graph().draw_mermaid())

def main(): #removed async
    initial_topic = "What is GRPO in large language models ? How does it help ?"

    initial_state = {
        "topic": initial_topic,
        "sections":[],
        "completed_sections": [],
        "messages": [],
        "final_report":""
    }

    final_state = app.invoke(
        initial_state,
        config={"recursion_limit": 50} #1+6*4 = 26 > 25
    )

    print("\n--- FINAL REPORT ---")
    print(final_state['final_report'])

if __name__=="__main__":
    print("Graph")
    # main()
