from langchain_core.messages import AIMessage, BaseMessage,HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langgraph.graph import add_messages,StateGraph
from langgraph.constants import START,END
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from typing import Annotated,Sequence,List, TypedDict
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import asyncio
from dotenv import load_dotenv
import uuid
from train_status import search_train
from gmail_integr import user_gmail
from rag_main import rag_tool
from flight_status import search_flight
from datetime_tool import get_curr_date
from code_tool import CodeExecutor
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
            "THE CURRENT YEAR IS 2025, DO NOT ASK THE USER FOR YEAR CONFIRMATION WHILE MAKING TOOL CALLS"
            "You are a helpful AI built to solve user queries using a set of specialized tools. Use them appropriately based on the user's request:"
            "Search Tool: Use this when the user asks questions that require up-to-date information from the web"
            "Train Search Tool: Use the `search_train` tool to find trains between two railway stations and provide a concise answer about available trains and coach classes."
            "Gmail Tool: Use the Gmail tool to perform actions related to email, like reading, sending, or searching emails from the user's account."
            "Document Retriever Tool: Use this to search and return relevant information from user-uploaded documents using retrieval-augmented generation (RAG)."
            "Answer normally when the query does not require any tool usage."
            "Flight Search Tool: Use the `search_flight` tool to find available flight between two airports and provide a concise answer about available flights. Always use the date tool first to accurately get the date for the date parameter. Specify the user how flight has been searched (e.g. Here are options for single adult, Here are options for two adult and a child)"
            "Get Current Date Tool : Use the get_curr_date to get the current date in the format %Y%m%d"
            "Code Executor Tool : Use the CodeExecutor tool to safely execute any C++,Python,Rust code. Use this either when user explictly demands it, or for any complex calculation or computation Input: language and code string. Output: execution result" 
            ),
            MessagesPlaceholder(variable_name="input")
        ])
        filled_template=prompt_template.format_messages(input=last_message)
        return{
            "messages":[self.llm.invoke(filled_template)]
        }

model=ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=1.0)
memory=AsyncSqliteSaver.from_conn_string("checkpoint.sqlite")
search_tool=TavilySearchResults(max_result=5)
tools=[search_tool,search_train,*rag_tool(),search_flight,get_curr_date,CodeExecutor()] #*user_gmail() token expired
agent=LLMNode(llm=model.bind_tools(tools)) #improve train search function

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

def get_chat_response(user_input:str,thread_id:str):
    sql_conn=sqlite3.connect("checkpoint_sync.sqlite",check_same_thread=False)
    memory_sync=SqliteSaver(sql_conn)
    without_stream_app=graph.compile(checkpointer=memory_sync)
    result=without_stream_app.invoke({
        "messages":HumanMessage(content=user_input)
    },{"configurable":{"thread_id":thread_id}}
    )
    return result["messages"][-1].content

async def run_chat_turn(main_graph, thread_id):
    user_input = input("Enter _> : ")
    if user_input.lower() in ['exit', 'quit']:
        return False  

    async for chunk,_ in main_graph.astream(
        {"messages": [HumanMessage(content=user_input)]},
        config={"configurable": {"thread_id": thread_id}},
        stream_mode="messages"  
    ):
        if isinstance(chunk,AIMessage) and chunk.content:
            print(chunk.content,end="",flush=True)
    print('\n')
    return True 

async def main():
    thread_id = str(uuid.uuid4())
    print(f"Starting new chat session with Thread ID: {thread_id}")

    async with AsyncSqliteSaver.from_conn_string("checkpoint.sqlite") as memory:
        main_graph = graph.compile(checkpointer=memory)

        while True:
            should_continue = await run_chat_turn(main_graph, thread_id)
            if not should_continue:
                break

async def stream_chat_response(user_input:str,thread_id:str):
    async with AsyncSqliteSaver.from_conn_string("checkpoint.sqlite") as memory:
        main_graph = graph.compile(checkpointer=memory)

        async for message_chunk,_ in main_graph.astream(
            {"messages": [HumanMessage(content=user_input)]},
            config={"configurable": {"thread_id": thread_id}},
            stream_mode="messages"
        ):
            if isinstance(message_chunk,AIMessage) and message_chunk.content:
                yield message_chunk.content

if __name__ == "__main__":
    asyncio.run(main())
