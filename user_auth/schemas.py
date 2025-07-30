from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Union

# #################################################################################################
# ######## request and response model of schemas.py file ##########################################

class UserCreate(BaseModel):
    first_name: str = Field(
        ...,
        description="The user's first name.",
        examples=["Khushi"]
    )
    last_name: str = Field(
        ...,
        description="The user's last name.",
        examples=["shrivastava"]
    )
    password: str = Field(
        ...,
        description="The user's password.",
        examples=["securepassword123"]
    )
    mobile_number: int = Field(
        ...,
        description="A 10-digit mobile number (as an integer) that does not start with 0.",
        examples=[9876543210]
    )
    email_address: EmailStr = Field(
        ...,
        description="A valid email address.",
        examples=["shrivastavakhushi@example.com"]
    )
    verification_token: str = Field(
        ...,
        description="Token received after phone verification",
        examples=["ver_abc123def456"]
    )

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

#####################################################################################################
########## OTPRequest ###############################################################################

class OTPRequest(BaseModel):
    mobile_number: int
    
    @field_validator('mobile_number')
    def validate_mobile_number(cls, v):
        if not isinstance(v, int):
            raise ValueError('Mobile number must be an integer')
        
        mobile_str = str(v)
        
        if not mobile_str.isdigit() or len(mobile_str) != 10:
            raise ValueError('Mobile number must be exactly 10 digits')
        
        if mobile_str.startswith('0'):
            raise ValueError('Mobile number cannot start with 0')
        
        return v

########################################################################################################################
############ Verify user data ##########################################################################################

class OTPVerify(BaseModel):
    mobile_number: int
    otp_code: str
    
    @field_validator('mobile_number')
    def validate_mobile_number(cls, v):
        if not isinstance(v, int):
            raise ValueError('Mobile number must be an integer')
        
        mobile_str = str(v)
        
        if not mobile_str.isdigit() or len(mobile_str) != 10:
            raise ValueError('Mobile number must be exactly 10 digits')
        
        if mobile_str.startswith('0'):
            raise ValueError('Mobile number cannot start with 0')
        
        return v

####################################################################################################################
############## user update request #################################################################################

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(
        None,
        description="The user's first name. Optional, provide to update.",
        examples=["Khushi"]
    )
    last_name: Optional[str] = Field(
        None,
        description="The user's last name. Optional, provide to update.",
        examples=["shrivastava"]
    )
    password: Optional[str] = Field(
        None,
        description="The user's password. Optional, provide to update.",
        examples=["newpassword123"]
    )
    mobile_number: Optional[int] = Field(
        None,
        description="A 10-digit mobile number (as an integer) that does not start with 0. Optional, provide to update.",
        examples=[9876543210]
    )
    email_address: Optional[EmailStr] = Field(
        None,
        description="A valid email address. Optional, provide to update.",
        examples=["john.doe@example.com"]
    )

    @field_validator('mobile_number')
    def validate_mobile_number(cls, v):
        """Validate that mobile number is exactly 10 digits if provided"""
        if v is None:
            return v
        
        if not isinstance(v, int):
            raise ValueError('Mobile number must be an integer')
        
        mobile_str = str(v)
        
        if not mobile_str.isdigit() or len(mobile_str) != 10:
            raise ValueError('Mobile number must be exactly 10 digits')
        
        if mobile_str.startswith('0'):
            raise ValueError('Mobile number cannot start with 0')
        
        return v

#############################################################################################################################
#################### user response ##########################################################################################

class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    mobile_number: int
    email_address: str
    created_at: int
    updated_at: Optional[int] = None
    is_active: bool
    is_phone_verified: bool 

###############################################################################################################################
############## user login request #############################################################################################

class UserLogin(BaseModel):
    identifier: Union[EmailStr, int] = Field(
        ...,
        description="The user's email address or phone number. Use an email address if `login_type` is 'email', or a 10-digit phone number (as an integer) if `login_type` is 'phone'.",
        examples=["user@example.com", 9876543210]
    )
    password: str = Field(
        ...,
        description="The user's password.",
        examples=["securepassword123"]
    )
    login_type: str = Field(
        ...,
        description="The type of login. Must be either 'email' or 'phone'.",
        examples=["email", "phone"]
    )

    @field_validator('identifier')
    def validate_identifier(cls, v, info):
        login_type = info.data.get('login_type')
        
        if login_type == "phone":
            if not isinstance(v, int):
                raise ValueError('Phone number must be an integer')
            
            mobile_str = str(v)
            
            if not mobile_str.isdigit() or len(mobile_str) != 10:
                raise ValueError('Mobile number must be exactly 10 digits')
            
            if mobile_str.startswith('0'):
                raise ValueError('Mobile number cannot start with 0')
        
        elif login_type == "email":
            if not isinstance(v, str) or '@' not in str(v):
                raise ValueError('Invalid email format')
        
        return v
    
#####################################################################################################################################
########## user login response #######################################################################################################

class UserLoginResponse(BaseModel):
    message: str
    user: UserResponse
    login_time: int

###########################################################################################################################################
############ OTP response ###############################################################################################################

class OTPResponse(BaseModel):
    message: str
    expires_in: int  # seconds
    
###########################################################################################################################################\
    
class PhoneVerificationResponse(BaseModel):
    message: str
    mobile_number: int
    verified: bool
    verification_token: str