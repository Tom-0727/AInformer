import os
from typing import Any

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class TaaftReaderConfig(BaseModel):
    read_model: str = Field(
        default="deepseek",
        description="The model to use for reading TAAFT AI tools",
    )
    max_read_tools: int = Field(
        default=20,
        description="The maximum number of AI tools to fetch from TAAFT",
    )

    @classmethod
    def from_runnable_config(cls, config: RunnableConfig) -> "TaaftReaderConfig":
        configurable = config.get("configurable", {}) if config else {}
        field_names = list(cls.model_fields.keys())
        values: dict[str, Any] = {
            field_name: os.environ.get(field_name.upper(), configurable.get(field_name))
            for field_name in field_names
        }
        return cls(**{k: v for k, v in values.items() if v is not None})
