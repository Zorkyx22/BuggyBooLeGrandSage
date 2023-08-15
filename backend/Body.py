from typing import List, Dict
from pydantic import BaseModel

class Body(BaseModel):
    conversation: list[dict[str, str]]