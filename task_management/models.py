from beanie import Document
from pydantic import Field, field_validator
from typing import Optional
import time


##############################################################################################################################
################## Task model for storing user tasks #########################################################################

class Tasks(Document):
    title: str = Field(..., description="Title of the task")
    description: str = Field(..., description="Description of the task")
    user_id: str = Field(..., description="ID of the user who created the task")
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: Optional[int] = None
    start_task_time: int = Field(..., description="Start time of task in epoch")
    end_task_time: int = Field(..., description="End time of task in epoch")
    is_completed: bool = False
    is_active: bool = True
    priority: str = Field(default="medium", description="Priority: low, medium, high")
    status: str = Field(default="pending", description="Status: pending, in_progress, completed, cancelled")

    @field_validator('priority')
    def validate_priority(cls, v):
        """Validate task priority"""
        allowed_priorities = ['low', 'medium', 'high']
        if v.lower() not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v.lower()

    @field_validator('status')
    def validate_status(cls, v):
        """Validate task status"""
        allowed_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if v.lower() not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v.lower()

    @field_validator('start_task_time', 'end_task_time')
    def validate_task_times(cls, v):
        """Validate that task times are valid timestamps"""
        if v <= 0:
            raise ValueError('Task time must be a valid positive timestamp')
        return v

    class Settings:
        name = "tasks"
        
########################################################################################################