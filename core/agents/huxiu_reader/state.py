import operator
from typing import Annotated

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class HuxiuArticleInfo(BaseModel):
    id: str
    title: str
    summary: str
    link: str


class HuxiuArticleRecommendation(BaseModel):
    id: str
    recommendation_reason: str
    risk_items: list[str]


class HuxiuReadResult(BaseModel):
    recommended_articles: list[HuxiuArticleRecommendation] = Field(default_factory=list)


class HuxiuReaderState(MessagesState):
    found_articles: list[HuxiuArticleInfo] = Field(default_factory=list)
    recommended_articles: list[HuxiuArticleRecommendation] = Field(default_factory=list)
    messages: Annotated[list[MessageLikeRepresentation], operator.add] = Field(default_factory=list)
