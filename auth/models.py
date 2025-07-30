from beanie import Document
from pydantic import Field
from typing import Optional
import time


#######################################################################################################################
############### Models that directly access the database and stored all the keys ######################################

class APIKey(Document):
    key: str = Field(..., unique=True, index=True)
    name: str
    is_active: bool = True
    created_at: int = Field(default_factory=lambda: int(time.time()))
    last_used: Optional[int] = None
    
    class Settings:
        name = "api_keys"
        
##########################################################################################################