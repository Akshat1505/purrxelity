from langchain_core.messages import AIMessage, BaseMessage,HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from langgraph.graph import add_messages,StateGraph
from langgraph.constants import START,END
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Annotated,Sequence,List, TypedDict
from dotenv import load_dotenv
load_dotenv()

class BasicChat(TypedDict):
    messages:Annotated[Sequence[BaseMessage],add_messages]

class LLMNode():
    def __init__(self,llm):
        self.llm=llm

    def __call__(self,state:BasicChat):
        last_message=state["messages"]
        return{
            "messages":[self.llm.invoke(last_message)]
        }

model=ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0.7)
search_tool=TavilySearchResults(max_result=5)
tools=[search_tool]
agent=LLMNode(llm=model.bind_tools([search_tool]))

def ModelCallTool(state:BasicChat):
    last_message=state["messages"][-1]
    if isinstance(last_message,AIMessage) and last_message.tool_calls:
        return "tools"
    return END

tool_node=ToolNode(tools)
graph=StateGraph(BasicChat)
graph.add_node("ModelReply",agent)
graph.set_entry_point("ModelReply")
graph.add_node("tools",tool_node)
graph.add_edge("tools","ModelReply")
graph.add_conditional_edges(
   "ModelReply",
    ModelCallTool,
    {
        "tools":"tools",
        END:END
    }
)
app=graph.compile()
while True:
    user_input=input("Enter _> : ")
    if user_input in ['exit','quit']:
        break
    result=app.invoke({
        "messages":HumanMessage(content=user_input)
    })
    print(result["messages"][-1].content)
