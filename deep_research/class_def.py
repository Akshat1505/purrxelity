from typing import Annotated,Literal,Sequence,TypedDict,List
from langchain_core import messages
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
import operator
from pydantic import BaseModel,Field

class SectionState(BaseModel):
    name:str=Field(description="name of the section")
    description:str=Field(description="brief description of the section")
    content:str=Field(description="content of the section",default="")
    # content:Annotated[Sequence[str],add_messages,Field(description="content of the section",default="")]

class ReportState(TypedDict):
    topic:str
    sections:List[SectionState]
    completed_sections:Annotated[List[SectionState],operator.add]
    # completed_sections:List[SectionState]
    messages:Annotated[List[BaseMessage],add_messages]
    # messages:List[BaseMessage]
    final_report:str
