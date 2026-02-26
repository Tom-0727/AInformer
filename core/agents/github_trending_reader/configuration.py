import os
from typing import Any
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class GithubTrendingReaderConfig(BaseModel):
    read_model: str = Field(
        default="glm-5",
        description="The model to use for reading the github trending repos"
    )
    max_read_repos: int = Field(
        default=5,
        description="The maximum number of repos to read"
    )

    @classmethod
    def from_runnable_config(cls, config: RunnableConfig) -> "GithubTrendingReaderConfig":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = config.get("configurable", {}) if config else {}
        field_names = list(cls.model_fields.keys())
        values: dict[str, Any] = {
            field_name: os.environ.get(field_name.upper(), configurable.get(field_name))
            for field_name in field_names
        }
        return cls(**{k: v for k, v in values.items() if v is not None})