from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from langchain_google_genai import ChatGoogleGenerativeAI

def user_gmail():
    credentials = get_gmail_credentials(
        token_file="token.json",
        scopes=["https://mail.google.com/"],
        client_secrets_file="credentials.json",
    )
    api_resource=build_resource_service(credentials=credentials)
    toolkit=GmailToolkit(api_resource=api_resource)
    return toolkit.get_tools()
    exit()
    llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash",temperature=0.7)
    llm_with_tools=llm.bind_tools(gmail_tools)
    from langgraph.prebuilt import create_react_agent

    agent_executor = create_react_agent(llm, gmail_tools)
    example_query = "Read the summarise my last 5 mails from inbox only and remove promotions/social from the message using filters"

    events = agent_executor.stream(
        {"messages": [("user", example_query)]},
        stream_mode="values",
    )
    for event in events:
        event["messages"][-1].pretty_print()

if __name__=="__main__":
    user_gmail()
