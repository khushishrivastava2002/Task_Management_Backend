from pydantic import BaseModel
from typing import Optional


########################################################################################################
########## request and response model that create a API ###############################################

class APIKeyCreate(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: str
    key: str
    name: str
    is_active: bool
    created_at: int
    last_used: Optional[int] = None

class APIKeyList(BaseModel):
    id: str
    name: str
    is_active: bool
    created_at: int
    last_used: Optional[int] = None
    
###################################################################################################################