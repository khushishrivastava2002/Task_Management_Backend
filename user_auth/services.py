############## SMS OTP with Twilio ######################################### 

import secrets
import time
from typing import Optional, List
from twilio.rest import Client

from user_auth.helper import generate_otp
from .models import PhoneVerification, Users, OTPStore
from .schemas import (
    PhoneVerificationResponse, UserCreate, UserUpdate, UserResponse, UserLogin, 
    UserLoginResponse, OTPRequest, OTPVerify, OTPResponse
)
from fastapi import HTTPException, status
from config.settings import settings



############################################################################################################
###########  Initialize Twilio client ######################################################################

twilio_client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

#############################################################################################################
############### function that send the OTP to all peoples ####################################################

async def send_sms(mobile_number: int, message: str) -> bool:
    """Send SMS using Twilio service"""
    try:
        phone_number = f"+91{mobile_number}"
        message = twilio_client.messages.create(
            body=message,
            from_=settings.twilio_phone_number,
            to=phone_number
        )
        print(f"SMS sent successfully to {phone_number}. Message SID: {message.sid}")
        return True
    except Exception as e:
        print(f"Failed to send SMS to {mobile_number}: {str(e)}")
        return False

###################################################################################################################
################## This function will send OTP to the mobile number ###############################################

async def send_otp(otp_request: OTPRequest) -> OTPResponse:
    """Send OTP to mobile number for verification"""
    
    # Check if user already exists with this mobile number
    existing_user = await Users.find_one(Users.mobile_number == otp_request.mobile_number)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this mobile number already exists"
        )
    
    # Check for recent OTP requests (rate limiting)
    recent_otp = await OTPStore.find_one({
        "mobile_number": otp_request.mobile_number,
        "created_at": {"$gte": int(time.time()) - 60}
    })
    
    if recent_otp:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait before requesting another OTP"
        )
    
    # Generate OTP
    otp_code = generate_otp()
    expires_at = int(time.time()) + 300  # 5 minutes expiry
    
    # Store OTP
    otp_record = OTPStore(
        mobile_number=otp_request.mobile_number,
        otp_code=otp_code,
        expires_at=expires_at
    )
    await otp_record.insert()
    
    # Send SMS via Twilio
    sms_message = f"Your OTP for phone verification is: {otp_code}. Valid for 5 minutes. Do not share this OTP with anyone."
    sms_sent = await send_sms(otp_request.mobile_number, sms_message)
    
    if not sms_sent:
        await otp_record.delete()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP. Please try again."
        )
    
    return OTPResponse(
        message="OTP sent successfully for phone verification",
        expires_in=300
    )

##########################################################################################################################
##################### function that verify the otp that goes on phone number #############################################
    
async def verify_phone_otp(otp_verify: OTPVerify) -> PhoneVerificationResponse:
    """Verify OTP and mark phone as verified"""
    
    # Find valid OTP
    otp_record = await OTPStore.find_one({
        "mobile_number": otp_verify.mobile_number,
        "is_used": False,
        "expires_at": {"$gt": int(time.time())}
    })
    
    if not otp_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP"
        )
    
    # Check attempts
    if otp_record.attempts >= 3:
        await otp_record.update({"$set": {"is_used": True}})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many failed attempts. Please request a new OTP."
        )
    
    # Verify OTP
    if otp_record.otp_code != otp_verify.otp_code:
        await otp_record.update({"$inc": {"attempts": 1}})
        remaining = 3 - (otp_record.attempts + 1)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OTP. {remaining} attempts remaining."
        )
    
    # Mark OTP as used
    await otp_record.update({"$set": {"is_used": True}})
    
    # Generate verification token
    verification_token = f"ver_{secrets.token_urlsafe(32)}"
    
    # Store phone verification
    phone_verification = PhoneVerification(
        mobile_number=otp_verify.mobile_number,
        verification_token=verification_token,
        expires_at=int(time.time()) + 3600  # Valid for 1 hour
    )
    
    # Remove any existing verification for this number
    await PhoneVerification.find({
        "mobile_number": otp_verify.mobile_number
    }).delete()
    
    await phone_verification.insert()
    
    return PhoneVerificationResponse(
        message="Phone number verified successfully",
        mobile_number=otp_verify.mobile_number,
        verified=True,
        verification_token=verification_token
    )

#########################################################################################################################
################ function that only register the verified user only #####################################################
   
async def register_verified_user(user_data: UserCreate) -> UserResponse:
    """Register user with verified phone number"""
    
    # Check if phone verification exists and is valid
    phone_verification = await PhoneVerification.find_one({
        "mobile_number": user_data.mobile_number,
        "verification_token": user_data.verification_token,
        "expires_at": {"$gt": int(time.time())},
        "is_used": False
    })
    
    if not phone_verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired phone verification. Please verify your phone number again."
        )
    
    # Check for existing user with email or mobile
    existing_user = await Users.find_one(
        {"$or": [
            {"email_address": user_data.email_address},
            {"mobile_number": user_data.mobile_number}
        ]}
    )
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or mobile number already exists"
        )
    
    # Create user
    user = Users(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password=Users.hash_password_static(user_data.password),
        mobile_number=user_data.mobile_number,
        email_address=user_data.email_address,
        created_at=int(time.time()),
        is_phone_verified=True
    )
    
    await user.insert()
    
    # Mark phone verification as used
    await phone_verification.update({"$set": {"is_used": True}})
    
    return UserResponse(
        id=str(user.id),
        first_name=user.first_name,
        last_name=user.last_name,
        mobile_number=user.mobile_number,
        email_address=user.email_address,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_active=user.is_active,
        is_phone_verified=user.is_phone_verified
    )

#############################################################################################################################
################# Login only authenticate user ##############################################################################

############ will login either by phone or by email ##########################################################################

async def login_user(login_data: UserLogin) -> UserLoginResponse:
    """Authenticate user login with email or phone"""
    
    # Build query based on login type
    if login_data.login_type == "email":
        query = {
            "email_address": login_data.identifier,
            "is_active": True
        }
    elif login_data.login_type == "phone":
        query = {
            "mobile_number": login_data.identifier,
            "is_active": True
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid login type. Use 'email' or 'phone'"
        )
    
    # Find user
    user = await Users.find_one(query)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Verify password
    if not user.verify_password(login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Update last login time
    login_time = int(time.time())
    
    return UserLoginResponse(
        message="Login successful",
        user=UserResponse(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            mobile_number=user.mobile_number,
            email_address=user.email_address,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active,
            is_phone_verified=user.is_phone_verified
        ),
        login_time=login_time
    )

###############################################################################################################
############## get user by id #################################################################################

async def get_user_by_id(user_id: str) -> Optional[UserResponse]:
    """Get user by ID"""
    try:
        user = await Users.get(user_id)
        if not user or not user.is_active:
            return None
    except:
        return None
    
    return UserResponse(
        id=str(user.id),
        first_name=user.first_name,
        last_name=user.last_name,
        mobile_number=user.mobile_number,
        email_address=user.email_address,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_active=user.is_active,
        is_phone_verified=user.is_phone_verified
    )

########################################################################################################################
############ update the user ###########################################################################################

async def update_user(user_id: str, user_data: UserUpdate) -> Optional[UserResponse]:
    """Update user information"""
    try:
        user = await Users.get(user_id)
        if not user or not user.is_active:
            return None
    except:
        return None
    
    # Check for duplicate email/mobile if they're being updated
    if user_data.email_address and user_data.email_address != user.email_address:
        existing_user = await Users.find_one(Users.email_address == user_data.email_address)
        if existing_user and str(existing_user.id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
    
    if user_data.mobile_number and user_data.mobile_number != user.mobile_number:
        existing_user = await Users.find_one(Users.mobile_number == user_data.mobile_number)
        if existing_user and str(existing_user.id) != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this mobile number already exists"
            )
    
    # Update fields
    update_data = {}
    if user_data.first_name is not None:
        update_data["first_name"] = user_data.first_name
    if user_data.last_name is not None:
        update_data["last_name"] = user_data.last_name
    if user_data.password is not None:
        update_data["password"] = Users.hash_password_static(user_data.password)
    if user_data.mobile_number is not None:
        update_data["mobile_number"] = user_data.mobile_number
        # If mobile number is updated, mark as not verified
        update_data["is_phone_verified"] = False
    if user_data.email_address is not None:
        update_data["email_address"] = user_data.email_address
    
    if update_data:
        update_data["updated_at"] = int(time.time())
        await user.update({"$set": update_data})
        user = await Users.get(user_id)
    
    return UserResponse(
        id=str(user.id),
        first_name=user.first_name,
        last_name=user.last_name,
        mobile_number=user.mobile_number,
        email_address=user.email_address,
        created_at=user.created_at,
        updated_at=user.updated_at,
        is_active=user.is_active,
        is_phone_verified=user.is_phone_verified
    )

###############################################################################################################
################ delete user as soft delete as is_active : false ##############################################

async def delete_user(user_id: str) -> bool:
    """Soft delete user (set is_active to False)"""
    try:
        user = await Users.get(user_id)
        if not user or not user.is_active:
            return False
    except:
        return False
    
    await user.update({"$set": {
        "is_active": False,
        "updated_at": int(time.time())
    }})
    
    return True

########################################################################################################################
####################### get all the users ###############################################################################

async def get_all_users() -> List[UserResponse]:
    """Get all active users"""
    users = await Users.find(Users.is_active == True).to_list()
    
    return [
        UserResponse(
            id=str(user.id),
            first_name=user.first_name,
            last_name=user.last_name,
            mobile_number=user.mobile_number,
            email_address=user.email_address,
            created_at=user.created_at,
            updated_at=user.updated_at,
            is_active=user.is_active,
            is_phone_verified=user.is_phone_verified
        ) for user in users
    ]

#############################################################################################################################