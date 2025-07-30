from google.ai.generativelanguage_v1beta.types import content
from langchain_core.messages import HumanMessage,SystemMessage,AIMessage
from langgraph.graph import StateGraph
from langgraph.constants import START,END
from langchain_community.tools import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel,Field
from class_def import ReportState,SectionState
from typing import List,TypedDict,Literal
import asyncio
from dotenv import load_dotenv
load_dotenv()

#works perfectly, tool call checked, response properly formatted
class ResearchLLM():
    def __init__(self,researchers):
        self.llm=researchers

    def __call__(self,state:SectionState):
        # print("Called")
        last_message=state["content"]
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=f"""
            You are a specialized research assistant LLM responsible for conducting precise web searches using the available search tool.
            Your task is to gather accurate, relevant, and up-to-date information about the topic: '{state["name"]}'.
            Topic Description: '{state["description"]}'
            Instructions:
            - Use the search tool to locate authoritative, high-quality sources (e.g., academic, governmental, news, or reputable technical sites).
            - Summarize the key findings in a well-organized, objective, and concise manner.
            - Focus on facts, statistics, recent developments, definitions, or explanations relevant to the topic.
            - Highlight any discrepancies or conflicting viewpoints in the sources, if found.
            - Structure the response clearly, using paragraphs or bullet points if helpful.
           """),
            # SystemMessage(content=f"You are a research summarization agent. Based on the search results provided in the conversation,provide a detailed, comprehensive summary for the section '{state["name"]}' with description '{state["description"]}'. Make it informative and well-organized."),
            MessagesPlaceholder(variable_name="input")
        ])
        # formatted_prompt=prompt.format_messages(input=last_message)
        # print(formatted_prompt)
        # response=self.llm.invoke(formatted_prompt)
        response=self.llm.invoke(prompt.format_messages(input=last_message))
        return{
            "content":[response]
        }

researchers=ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.4)
search_tool=TavilySearchResults(max_results=1)
tools=[search_tool]        
agent=ResearchLLM(researchers=researchers.bind_tools(tools))

def routing_function(state:SectionState): 
    last_message=state["content"][-1]
    if isinstance(last_message,AIMessage) and last_message.tool_calls:
        # print("Tool Call")
        return "toolnode"
    else:
        return END

graph=StateGraph(SectionState)
toolnode=ToolNode(tools,messages_key="content")
graph.add_node("ModelReply",agent)
graph.add_node("toolnode",toolnode)
graph.add_conditional_edges(
    "ModelReply",
    routing_function,
    {
        "toolnode":"toolnode",
        END:END
    }
)
graph.set_entry_point("ModelReply")
graph.add_edge("toolnode","ModelReply")
app=graph.compile()
print(app.get_graph().draw_ascii())

if __name__=="__main__":
    initial_state = {
    "name": "K.V cache",
    "description": "Brief overview of K.V. cache in transformers",
    "content": [HumanMessage(content="Research this topic")]
    }
    result=app.invoke(initial_state)
    print(result["content"][-1].content)

