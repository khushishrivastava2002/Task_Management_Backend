
from datetime import datetime
from user_auth.models import Users



# Helper function to convert epoch to human readable format
def epoch_to_human_time(epoch_time: int) -> str:
    """Convert epoch timestamp to human readable format"""
    try:
        dt = datetime.fromtimestamp(epoch_time)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "Invalid timestamp"


# Helper function to validate if user exists and is active
async def validate_user_exists(user_id: str) -> bool:
    """Check if user exists and is active"""
    try:
        user = await Users.get(user_id)
        return user is not None and user.is_active
    except:
        return False
    
    
# Helper function to convert human readable time to epoch
def human_time_to_epoch(human_time: str) -> int:
    """Convert human readable time to epoch timestamp
    Supports formats: 'YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DD HH:MM', 'YYYY-MM-DD'
    """
    try:
        # Try different datetime formats
        formats = [
            '%Y-%m-%d %H:%M:%S',  # 2024-12-31 23:59:59
            '%Y-%m-%d %H:%M',     # 2024-12-31 23:59
            '%Y-%m-%d',           # 2024-12-31 (defaults to 00:00:00)
            '%d-%m-%Y %H:%M:%S',  # 31-12-2024 23:59:59
            '%d-%m-%Y %H:%M',     # 31-12-2024 23:59
            '%d-%m-%Y',           # 31-12-2024
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(human_time, fmt)
                return int(dt.timestamp())
            except ValueError:
                continue
        
        raise ValueError(f"Invalid datetime format: {human_time}")
    except Exception as e:
        raise ValueError(f"Failed to parse datetime: {str(e)}")