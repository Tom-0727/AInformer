import os
from typing import Any

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class ProductHuntReaderConfig(BaseModel):
    read_model: str = Field(
        default="deepseek",
        description="The model to use for reading Product Hunt products",
    )
    max_read_products: int = Field(
        default=20,
        description="The maximum number of products to fetch from Product Hunt",
    )

    @classmethod
    def from_runnable_config(cls, config: RunnableConfig) -> "ProductHuntReaderConfig":
        configurable = config.get("configurable", {}) if config else {}
        field_names = list(cls.model_fields.keys())
        values: dict[str, Any] = {
            field_name: os.environ.get(field_name.upper(), configurable.get(field_name))
            for field_name in field_names
        }
        return cls(**{k: v for k, v in values.items() if v is not None})
