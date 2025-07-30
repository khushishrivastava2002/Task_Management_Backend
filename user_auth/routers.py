from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from .schemas import (
    UserCreate, UserUpdate, UserResponse, UserLogin, UserLoginResponse,
    OTPRequest, OTPVerify, OTPResponse, PhoneVerificationResponse
)
from .services import (
    send_otp, verify_phone_otp, register_verified_user, login_user, 
    get_user_by_id, update_user, delete_user, get_all_users
)
from auth.routers import get_current_api_key

################################################################################################################################
############### API routers for users ###########################################################################################

user_auth_router = APIRouter(prefix="/users", tags=["User Management"])

################################################################################################################################
######## Step 1: Send OTP to verify phone number ##############################################################################

@user_auth_router.post("/send_otp", response_model=OTPResponse)
async def send_phone_verification_otp(
    otp_request: OTPRequest,
    current_key = Depends(get_current_api_key)
):
    """Send OTP for phone number verification (requires API key authentication)"""
    return await send_otp(otp_request)

##################################################################################################################################
######## Step 2: Verify phone number with OTP ##################################################################################

@user_auth_router.post("/verify_phone", response_model=PhoneVerificationResponse)
async def verify_phone_number(
    otp_verify: OTPVerify,
    current_key = Depends(get_current_api_key)
):
    """Verify phone number with OTP (requires API key authentication)"""
    return await verify_phone_otp(otp_verify)

##################################################################################################################################
######## Step 3: Register user with verified phone number ######################################################################

@user_auth_router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    current_key = Depends(get_current_api_key)
):
    """Register user with verified phone number (requires API key authentication)"""
    return await register_verified_user(user_data)

#####################################################################################################################################
########### API endpoint for user login #############################################################################################

@user_auth_router.post("/login", response_model=UserLoginResponse)
async def login_user_endpoint(
    login_data: UserLogin,
    current_key = Depends(get_current_api_key)
):
    """Login user with email or phone and password (requires API key authentication)"""
    return await login_user(login_data)

########################################################################################################################################
############## API endpoint that shows all users ######################################################################################

@user_auth_router.get("/", response_model=List[UserResponse])
async def get_users(current_key = Depends(get_current_api_key)):
    """Get all users (requires API key authentication)"""
    return await get_all_users()

#########################################################################################################################################
################# API endpoint to get a particular user ################################################################################

@user_auth_router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_key = Depends(get_current_api_key)
):
    """Get user by ID (requires API key authentication)"""
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

############################################################################################################################################
######################### API endpoint to update a specific user ##########################################################################

@user_auth_router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: str,
    user_data: UserUpdate,
    current_key = Depends(get_current_api_key)
):
    """Update user information (requires API key authentication)"""
    user = await update_user(user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

##############################################################################################################################################
###################### API endpoint to delete a particular user #############################################################################

@user_auth_router.delete("/{user_id}")
async def delete_user_endpoint(
    user_id: str,
    current_key = Depends(get_current_api_key)
):
    """Delete user (soft delete - requires API key authentication)"""
    success = await delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}

####################################################################################################################################################