from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from .schemas import APIKeyCreate, APIKeyResponse, APIKeyList
from .services import create_api_key, validate_api_key, get_all_api_keys, deactivate_api_key

########################################################################################

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

############################################################################################
#############################################################################################


"""
The line security = HTTPBearer() is used to define a security scheme for handling Bearer token authentication in the FastAPI application. Specifically, it’s part of the FastAPI security module (fastapi.security) and is used to extract and validate API keys (or tokens) from the Authorization header of incoming HTTP requests

It implements the Bearer authentication scheme, which is commonly used to authenticate requests by including a token (e.g., an API key) in the Authorization header of an HTTP request in the format:

Authorization: Bearer <token>

"""
security = HTTPBearer()

#####################################################################################################
# The security instance is used in the get_current_api_key dependency ############################

"""
Here, Depends(security) injects the HTTPBearer scheme, which provides the HTTPAuthorizationCredentials object containing the token (credentials.credentials)
The dependency then validates the token using validate_api_key
"""
async def get_current_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to validate API key from Authorization header"""
    api_key = credentials.credentials
    
    key_doc = await validate_api_key(api_key)
    if not key_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )
    
    return key_doc

################################################################################################################
################## Post API this will create a new API for the access #########################################

@auth_router.post("/api-keys", response_model=APIKeyResponse)
async def create_new_api_key(api_key_data: APIKeyCreate):
    """Create a new API key"""
    return await create_api_key(api_key_data)


#####################################################################################################################
############## get API to access the all the apis that is present till now ##############################################

@auth_router.get("/api-keys", response_model=List[APIKeyList])
async def list_api_keys(current_key = Depends(get_current_api_key)):
    """List all API keys (protected endpoint)"""
    keys = await get_all_api_keys()
    return [
        APIKeyList(
            id=str(key.id),
            name=key.name,
            is_active=key.is_active,
            created_at=key.created_at,
            last_used=key.last_used
        ) for key in keys
    ]

###################################################################################################################
################ The delete api this will deactivate the api key when not in use ##################################

@auth_router.delete("/api-keys/{key_id}")
async def delete_api_key(key_id: str, current_key = Depends(get_current_api_key)):
    """Deactivate an API key (protected endpoint)"""
    success = await deactivate_api_key(key_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    return {"message": "API key deactivated successfully"}

####################################################################################################################
# Custom dependency for docs authentication
########## this is validate the api key #################################

async def docs_auth_dependency(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Special dependency for docs authentication"""
    return await get_current_api_key(credentials)

#####################################################################################################################