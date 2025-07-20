from langchain_core.messages import AIMessage, BaseMessage,HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import add_messages,StateGraph
from langgraph.constants import START,END
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Annotated,Sequence,List, TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from dotenv import load_dotenv
import uuid
from train_status import search_train
from gmail_integr import user_gmail
from rag_main import rag_tool
from flight_status import search_flight
from datetime_tool import get_curr_date
load_dotenv()

class BasicChat(TypedDict):
    messages:Annotated[Sequence[BaseMessage],add_messages]

class LLMNode():
    def __init__(self,llm):
        self.llm=llm

    def __call__(self,state:BasicChat):
        last_message=state["messages"]
        prompt_template=ChatPromptTemplate.from_messages([
            ("system", 
            "You are a helpful AI built to solve user queries using a set of specialized tools. Use them appropriately based on the user's request:"
            "Search Tool: Use this when the user asks questions that require up-to-date information from the web"
            "Train Search Tool: Use the `search_train` tool to find trains between two railway stations and provide a concise answer about available trains and coach classes."
            "Gmail Tool: Use the Gmail tool to perform actions related to email, like reading, sending, or searching emails from the user's account."
            "Document Retriever Tool: Use this to search and return relevant information from user-uploaded documents using retrieval-augmented generation (RAG)."
            "Answer normally when the query does not require any tool usage."
            "Flight Search Tool: Use the `search_flight` tool to find available flight between two airports and provide a concise answer about available flights. Always use the date tool first to accurately get the date for the date parameter. Specify the user how flight has been searched (e.g. Here are options for single adult, Here are options for two adult and a child)"
            "Get Current Date Tool : Use the get_curr_date to get the current date in the format %Y%m%d"
            ),
            ("user","User input is {input}")
        ])
        filled_template=prompt_template.format(input=last_message)
        return{
            "messages":[self.llm.invoke(filled_template)]
        }

model=ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=1.0)
sql_conn=sqlite3.connect("checkpoint.sqlite",check_same_thread=False)
memory=SqliteSaver(sql_conn)
search_tool=TavilySearchResults(max_result=5)
tools=[search_tool,search_train,*user_gmail(),*rag_tool(),search_flight,get_curr_date]
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
app=graph.compile(checkpointer=memory)
random_thread_id=uuid.uuid4()
while True:
    user_input=input("Enter _> : ")
    if user_input in ['exit','quit']:
        break
    result=app.invoke({
        "messages":HumanMessage(content=user_input)
    },{"configurable":{"thread_id":random_thread_id}}
    )
    print(result["messages"][-1].content)
