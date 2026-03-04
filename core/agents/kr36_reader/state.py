import operator
from typing import Annotated

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class Kr36ArticleInfo(BaseModel):
    id: str
    title: str
    description: str
    published_at: str
    link: str


class Kr36ArticleRecommendation(BaseModel):
    id: str
    recommendation_reason: str
    risk_items: list[str]


class Kr36ReadResult(BaseModel):
    recommended_articles: list[Kr36ArticleRecommendation] = Field(default_factory=list)


class Kr36ReaderState(MessagesState):
    found_articles: list[Kr36ArticleInfo] = Field(default_factory=list)
    recommended_articles: list[Kr36ArticleRecommendation] = Field(default_factory=list)
    messages: Annotated[list[MessageLikeRepresentation], operator.add] = Field(default_factory=list)
