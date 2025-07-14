from langchain_core.messages import AIMessage, BaseMessage,HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import add_messages,StateGraph
from langgraph.constants import START,END
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Annotated,Sequence,List, TypedDict
from train_status import search_train
from dotenv import load_dotenv
load_dotenv()

class BasicChat(TypedDict):
    messages:Annotated[Sequence[BaseMessage],add_messages]

class LLMNode():
    def __init__(self,llm):
        self.llm=llm

    def __call__(self,state:BasicChat):
        last_message=state["messages"]
        prompt_template=ChatPromptTemplate.from_messages([
            ("system","You are a helpful AI built to solve user queries with access to Search Feature if user asks for question that needs up to date information otherwise answer normally. You can also use the search_train tool to find trains between two railway station to give user a consise answer for available train and coach classes available"),
            ("user","User input is {input}")
        ])
        filled_template=prompt_template.format(input=last_message)
        return{
            "messages":[self.llm.invoke(filled_template)]
        }

model=ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=1.0)
search_tool=TavilySearchResults(max_result=5)
tools=[search_tool,search_train]
agent=LLMNode(llm=model.bind_tools(tools))

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
