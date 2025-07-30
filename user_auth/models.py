from beanie import Document
from pydantic import Field, EmailStr, field_validator
from typing import Optional
import time
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# #####################################################################################################
# ################# users collection that stores the unique users #####################################

class Users(Document):
    first_name: str
    last_name: str
    password: str
    mobile_number: int = Field(..., unique=True, index=True)
    email_address: EmailStr = Field(..., unique=True, index=True)
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: Optional[int] = None
    is_active: bool = True
    is_phone_verified: bool = False

    @field_validator('mobile_number')
    def validate_mobile_number(cls, v):
        """Validate that mobile number is exactly 10 digits"""
        if not isinstance(v, int):
            raise ValueError('Mobile number must be an integer')
        
        mobile_str = str(v)
        
        if not mobile_str.isdigit() or len(mobile_str) != 10:
            raise ValueError('Mobile number must be exactly 10 digits')
        
        if mobile_str.startswith('0'):
            raise ValueError('Mobile number cannot start with 0')
        
        return v

    class Settings:
        name = "users"

    def hash_password(self, password: str):
        """Hash the password before storing"""
        self.password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(password, self.password)

    @classmethod
    def hash_password_static(cls, password: str) -> str:
        """Static method to hash password"""
        return pwd_context.hash(password)



###############################################################################################################
# New OTP model for storing temporary OTPs

class OTPStore(Document):
    mobile_number: int
    otp_code: str
    created_at: int = Field(default_factory=lambda: int(time.time()))
    expires_at: int
    is_used: bool = False
    attempts: int = 0

    class Settings:
        name = "otp_store"
        
########################################################################################################################
### model to track verified phone numbers

class PhoneVerification(Document):
    mobile_number: int = Field(..., unique=True, index=True)
    verification_token: str = Field(..., unique=True, index=True)
    verified_at: int = Field(default_factory=lambda: int(time.time()))
    expires_at: int  # Verification expires after some time
    is_used: bool = False  # Track if this verification was used for registration

    class Settings:
        name = "phone_verifications"
        
##########################################################################################################################