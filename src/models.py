from pydantic import BaseModel


class CommandString(BaseModel):
    command: str