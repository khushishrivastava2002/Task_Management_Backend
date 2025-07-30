import random
import string

####################################################################################################################
################## This will generate a 6 digit random OTp and this will send to the peoples #######################

def generate_otp(length: int = 6) -> str:
    """Generate random OTP"""
    return ''.join(random.choices(string.digits, k=length))

##################################################################################################################