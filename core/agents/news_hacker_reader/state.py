import operator
from typing import Annotated

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, BeforeValidator, Field


class StoryInfo(BaseModel):
    id: str
    title: str
    url: str
    hn_url: str
    score: int
    comments: int
    story_text: str = ""
    article_preview: str = ""
    discussion_preview: str = ""


class StoryRecommendation(BaseModel):
    id: Annotated[str, BeforeValidator(str)]
    recommendation_reason: str
    risk_items: list[str]


class StoryShortlistResult(BaseModel):
    shortlisted_ids: list[Annotated[str, BeforeValidator(str)]] = Field(default_factory=list)


class StoryReadResult(BaseModel):
    recommended_stories: list[StoryRecommendation] = Field(default_factory=list)


class NewsHackerReaderState(MessagesState):
    found_stories: list[StoryInfo] = Field(default_factory=list)
    recommended_stories: list[StoryRecommendation] = Field(default_factory=list)
    messages: Annotated[list[MessageLikeRepresentation], operator.add] = Field(default_factory=list)
