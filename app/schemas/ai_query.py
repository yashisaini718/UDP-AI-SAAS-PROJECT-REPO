from pydantic import BaseModel

class QueryText(BaseModel):
    query: str