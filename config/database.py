import motor.motor_asyncio
from beanie import init_beanie
from task_management.models import Tasks
from user_auth.models import OTPStore, PhoneVerification, Users
from .settings import settings
from auth.models import APIKey


#########################################################################################################
####### Database files that have an use of beanie ODM use ################################################

# MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_url)
database = client[settings.database_name]

async def init_db():
    """Initialize database with Beanie"""
    await init_beanie(database=database, document_models=[APIKey,Users,OTPStore,PhoneVerification,Tasks])

###############################################################################################################