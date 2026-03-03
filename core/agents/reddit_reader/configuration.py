import os
from typing import Any

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class RedditReaderConfig(BaseModel):
    read_model: str = Field(
        default="deepseek",
        description="The model to use for reading reddit posts",
    )
    max_read_posts: int = Field(
        default=30,
        description="The maximum total number of posts to fetch",
    )
    per_sub_limit: int = Field(
        default=5,
        description="The maximum number of posts per subreddit",
    )

    @classmethod
    def from_runnable_config(cls, config: RunnableConfig) -> "RedditReaderConfig":
        configurable = config.get("configurable", {}) if config else {}
        field_names = list(cls.model_fields.keys())
        values: dict[str, Any] = {
            field_name: os.environ.get(field_name.upper(), configurable.get(field_name))
            for field_name in field_names
        }
        return cls(**{k: v for k, v in values.items() if v is not None})
