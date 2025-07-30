import secrets
import time
from typing import Optional
from .models import APIKey
from .schemas import APIKeyCreate, APIKeyResponse



############################################################################################################################
############# This will create a new api key ###############################################################################

async def create_api_key(api_key_data: APIKeyCreate) -> APIKeyResponse:
    """Create a new API key"""
    # Generate a secure random API key
    key = f"sk-{secrets.token_urlsafe(32)}"
    
    api_key = APIKey(
        key=key,
        name=api_key_data.name,
        created_at=int(time.time())
    )
    
    await api_key.insert()
    
    return APIKeyResponse(
        id=str(api_key.id),
        key=api_key.key,
        name=api_key.name,
        is_active=api_key.is_active,
        created_at=api_key.created_at,
        last_used=api_key.last_used
    )

################################################################################################################################
################### This function is used to update the API key and update the last used timestamps ############################

async def validate_api_key(api_key: str) -> Optional[APIKey]:
    """Validate API key and update last_used timestamp"""
    key_doc = await APIKey.find_one(APIKey.key == api_key, APIKey.is_active == True)
    
    if key_doc:
        # Update last used timestamp
        key_doc.last_used = int(time.time())
        await key_doc.save()
        
    return key_doc

#########################################################################################################################################
############## This function will fetch all the api keys that is present ################################################################

async def get_all_api_keys():
    """Get all API keys (without exposing the actual key)"""
    keys = await APIKey.find_all().to_list()
    return keys

########################################################################################################################################
########### This function will deactivate the api key that not in used #################################################################

async def deactivate_api_key(key_id: str) -> bool:
    """Deactivate an API key"""
    api_key = await APIKey.get(key_id)
    if api_key:
        api_key.is_active = False
        await api_key.save()
        return True
    return False

############################################################################################################################################