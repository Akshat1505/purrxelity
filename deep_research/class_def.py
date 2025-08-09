from typing import Annotated,Literal,Sequence,TypedDict,List
from langchain_core import messages
from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages
import operator
from pydantic import BaseModel,Field

class SectionState(TypedDict):
    name:str
    description:str
    content:Annotated[Sequence[BaseMessage],add_messages]

class SectionOutput(BaseModel):
    name:str=Field(description="name of the section")
    description:str=Field(description="brief description of the section")

class ReportState(TypedDict):
    topic:str
    sections:List[SectionOutput]
    completed_sections:Annotated[List[SectionState],operator.add]
    messages:Annotated[List[BaseMessage],add_messages]
    final_report:str
