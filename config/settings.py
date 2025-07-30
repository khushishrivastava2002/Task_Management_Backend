import os
from pydantic_settings import BaseSettings



##################################################################################################################################
################## This is settings all the main credentials that we used will use by here #######################################

class Settings(BaseSettings):
    mongodb_url: str 
    database_name: str 
    secret_key: str
    
    # Twilio SMS Configuration
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_phone_number: str
    
    class Config:
        ENV = os.getenv("ENV")
        print(f"{ENV=}")
        if ENV == 'PRODUCTION':
            dotenv_file = '.env.production'
        elif ENV == 'STAGE':
            dotenv_file = '.env.stage'
        elif ENV == 'LOCAL':
            dotenv_file = '.env.local'
        else:
            print("ENVIRONMENT SETTINGS NOT FOUND")
            
        env_file = dotenv_file

settings = Settings()


##########################################################################################################################################