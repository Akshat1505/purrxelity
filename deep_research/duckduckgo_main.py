from langgraph.graph import StateGraph
from langgraph.constants import START,END
from langchain_community.tools import DuckDuckGoSearchRun,DuckDuckGoSearchResults

search=DuckDuckGoSearchRun()
# print(search.invoke(("What's the capital of India")))
search = DuckDuckGoSearchResults(output_format="list")

print(search.invoke("What's the capital of India"))
