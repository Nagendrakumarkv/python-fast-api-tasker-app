from pydantic import BaseModel, field_validator, ConfigDict

class TaskBase(BaseModel):
    title: str
    description: str | None = None
    is_completed: bool = False

    # Validation
    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v


class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_completed: bool | None = None

class TaskOut(TaskBase):
    id: int
    model_config = ConfigDict(from_attributes=True)