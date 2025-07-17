from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_async_playwright_browser,create_sync_playwright_browser
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

llm=ChatGoogleGenerativeAI(model="gemini-2.0-flash")
async_browser=create_async_playwright_browser()
sync_browser=create_sync_playwright_browser()
toolkit=PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
# print(toolkit.get_tools())

llm_with_tools=llm.bind_tools(toolkit.get_tools())
agent_chain=create_react_agent(model=llm,tools=toolkit.get_tools())

async def run_agent():
    result = await agent_chain.ainvoke(
        {"messages": [("user", "What are the headers on langchain.com?")]}
    )
    print(result)

if __name__=="__main__":
    res=run_agent()
