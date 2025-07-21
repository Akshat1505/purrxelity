from langgraph.graph import StateGraph
from langgraph.constants import START,END
from langchain_community.tools import TavilySearchResults
from langchain_google_genai import ChatGoogleGenerativeAI
from dr_state import ReportState,SectionState
from dotenv import load_dotenv
load_dotenv()

llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.7)
search_tool=TavilySearchResults(max_result=5)
tools=[search_tool]
agent=llm.bind_tools(tools)


def ChatBot(state:SectionState):
    return{
        "messages":llm.invoke(state['section'])
    }

def ToolCall(state:SectionState):
    return 0
graph=StateGraph(SectionState)
graph.add_node("ChatBot",ChatBot)

        
