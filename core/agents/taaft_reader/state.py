import operator
from typing import Annotated

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class AiToolInfo(BaseModel):
    id: str
    name: str
    description: str
    use_case: str
    link: str


class AiToolRecommendation(BaseModel):
    id: str
    recommendation_reason: str
    risk_items: list[str]


class AiToolReadResult(BaseModel):
    recommended_tools: list[AiToolRecommendation] = Field(default_factory=list)


class TaaftReaderState(MessagesState):
    found_tools: list[AiToolInfo] = Field(default_factory=list)
    recommended_tools: list[AiToolRecommendation] = Field(default_factory=list)
    messages: Annotated[list[MessageLikeRepresentation], operator.add] = Field(default_factory=list)
