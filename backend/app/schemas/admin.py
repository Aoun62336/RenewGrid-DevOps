from pydantic import BaseModel, EmailStr

class AssignPickupIn(BaseModel):
    collector_id: int
    recycler_id: int | None = None

class CreateUserIn(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str  # "user" | "collector" | "recycler"

class RecyclerStatusIn(BaseModel):
    status: str  # "approved" | "rejected"

class UpdateUserIn(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    role: str | None = None
