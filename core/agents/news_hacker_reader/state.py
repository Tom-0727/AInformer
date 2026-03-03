import operator
from typing import Annotated

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class StoryInfo(BaseModel):
    id: str
    title: str
    url: str
    hn_url: str
    score: int
    comments: int


class StoryRecommendation(BaseModel):
    id: str
    recommendation_reason: str
    risk_items: list[str]


class StoryReadResult(BaseModel):
    recommended_stories: list[StoryRecommendation] = Field(default_factory=list)


class NewsHackerReaderState(MessagesState):
    found_stories: list[StoryInfo] = Field(default_factory=list)
    recommended_stories: list[StoryRecommendation] = Field(default_factory=list)
    messages: Annotated[list[MessageLikeRepresentation], operator.add] = Field(default_factory=list)
