import operator
from typing import Annotated

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, BeforeValidator, Field


class ProductInfo(BaseModel):
    id: str
    name: str
    tagline: str
    description: str
    link: str


class ProductRecommendation(BaseModel):
    id: Annotated[str, BeforeValidator(str)]
    recommendation_reason: str
    risk_items: list[str]


class ProductReadResult(BaseModel):
    recommended_products: list[ProductRecommendation] = Field(default_factory=list)


class ProductHuntReaderState(MessagesState):
    found_products: list[ProductInfo] = Field(default_factory=list)
    recommended_products: list[ProductRecommendation] = Field(default_factory=list)
    messages: Annotated[list[MessageLikeRepresentation], operator.add] = Field(default_factory=list)
