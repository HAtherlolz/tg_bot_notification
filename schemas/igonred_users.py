from pydantic import BaseModel


class IgnoredUserSchema(BaseModel):
    username: str
