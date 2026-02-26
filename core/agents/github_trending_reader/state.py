import operator
from typing import Annotated

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class RepoInfo(BaseModel):
    id: str
    title: str
    link: str
    description: str
    recommendation_reason: str
    risk_items: list[str]


class RepoReadResult(BaseModel):
    recommended_repos: list[RepoInfo] = Field(default_factory=list)


class GithubTrendingReaderState(MessagesState):
    since: str = Field(default="daily")
    found_repos: list[RepoInfo] = Field(default=[])
    recommended_repos: list[RepoInfo] = Field(default=[])
    messages: Annotated[list[MessageLikeRepresentation], operator.add] = Field(default=[])
