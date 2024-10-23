from pydantic.v1 import BaseModel, Field, validator
class EmbeddingConfig(BaseModel):
    name: str = Field(..., description="The name of the SentenceTransformer model")

    @validator('name', allow_reuse=True)
    def check_model_name(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Model name must be a non-empty string")
        return value
