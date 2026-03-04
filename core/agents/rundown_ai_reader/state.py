import operator
from typing import Annotated

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class RundownItemInfo(BaseModel):
    id: str
    headline: str
    summary: str
    content: str
    link: str


class RundownItemRecommendation(BaseModel):
    id: str
    recommendation_reason: str
    risk_items: list[str]


class RundownReadResult(BaseModel):
    recommended_items: list[RundownItemRecommendation] = Field(default_factory=list)


class RundownAiReaderState(MessagesState):
    found_items: list[RundownItemInfo] = Field(default_factory=list)
    recommended_items: list[RundownItemRecommendation] = Field(default_factory=list)
    messages: Annotated[list[MessageLikeRepresentation], operator.add] = Field(default_factory=list)
