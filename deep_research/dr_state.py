from typing import Annotated,Literal,Sequence,TypedDict,List
from langgraph.graph import add_messages
import operator

class ReportState(TypedDict):
    sections:List[str]
    completed_sections:Annotated[List[str],add_messages]
    final_report:str

class SectionState(TypedDict):
    section:str
    content:str


