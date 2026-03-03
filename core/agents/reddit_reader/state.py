import operator
from typing import Annotated

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class PostInfo(BaseModel):
    id: str
    subreddit: str
    title: str
    selftext: str
    url: str
    reddit_url: str
    score: int
    num_comments: int


class PostRecommendation(BaseModel):
    id: str
    recommendation_reason: str
    risk_items: list[str]


class PostReadResult(BaseModel):
    recommended_posts: list[PostRecommendation] = Field(default_factory=list)


class RedditReaderState(MessagesState):
    found_posts: list[PostInfo] = Field(default_factory=list)
    recommended_posts: list[PostRecommendation] = Field(default_factory=list)
    messages: Annotated[list[MessageLikeRepresentation], operator.add] = Field(default_factory=list)
