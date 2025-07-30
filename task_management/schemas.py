from pydantic import BaseModel, Field, field_validator
from typing import Optional
from task_management.helper import human_time_to_epoch

##################################################################################################################
################################## Schema for creating a new task ################################################

class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        description="Title of the task",
        examples=["Complete project documentation"]
    )
    description: str = Field(
        ...,
        description="Detailed description of the task",
        examples=["Write comprehensive documentation for the user authentication system"]
    )
    start_task_time: str = Field(
        ...,
        description="Start time in human readable format (YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM or YYYY-MM-DD)",
        examples=["2024-12-31 09:00:00", "2024-12-31 09:00", "2024-12-31"]
    )
    end_task_time: str = Field(
        ...,
        description="End time in human readable format (YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM or YYYY-MM-DD)",
        examples=["2024-12-31 17:00:00", "2024-12-31 17:00", "2024-12-31"]
    )
    priority: Optional[str] = Field(
        default="medium",
        description="Task priority: low, medium, high",
        examples=["high", "medium", "low"]
    )
    status: Optional[str] = Field(
        default="pending",
        description="Task status: pending, in_progress, completed, cancelled",
        examples=["pending", "in_progress", "completed"]
    )

    @field_validator('start_task_time', 'end_task_time')
    def validate_time_format(cls, v):
        """Validate and convert human readable time"""
        try:
            epoch_time = human_time_to_epoch(v)
            return v  # Return original for now, will convert in service
        except ValueError as e:
            raise ValueError(f"Invalid time format: {str(e)}")

###################################################################################################################
######################### Schema for updating a task ##############################################################

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        description="Title of the task",
        examples=["Updated project documentation"]
    )
    description: Optional[str] = Field(
        None,
        description="Detailed description of the task",
        examples=["Updated documentation for the user authentication system"]
    )
    start_task_time: Optional[str] = Field(
        None,
        description="Start time in human readable format",
        examples=["2024-12-31 10:00:00"]
    )
    end_task_time: Optional[str] = Field(
        None,
        description="End time in human readable format",
        examples=["2024-12-31 18:00:00"]
    )
    priority: Optional[str] = Field(
        None,
        description="Task priority: low, medium, high",
        examples=["high"]
    )
    status: Optional[str] = Field(
        None,
        description="Task status: pending, in_progress, completed, cancelled",
        examples=["in_progress"]
    )
    is_completed: Optional[bool] = Field(
        None,
        description="Mark task as completed",
        examples=[True, False]
    )

    @field_validator('start_task_time', 'end_task_time')
    def validate_time_format(cls, v):
        """Validate time format if provided"""
        if v is not None:
            try:
                human_time_to_epoch(v)
                return v
            except ValueError as e:
                raise ValueError(f"Invalid time format: {str(e)}")
        return v

################################################################################################################################
####################################### Schema for task response ###############################################################

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    user_id: str
    created_at: int
    updated_at: Optional[int] = None
    start_task_time: int
    end_task_time: int
    start_task_time_human: str  # Human readable format
    end_task_time_human: str    # Human readable format
    is_completed: bool
    is_active: bool
    priority: str
    status: str

##########################################################################################################################
####################################### Schema for task filtering and searching ##########################################

class TaskFilter(BaseModel):
    status: Optional[str] = Field(None, description="Filter by status")
    priority: Optional[str] = Field(None, description="Filter by priority")
    is_completed: Optional[bool] = Field(None, description="Filter by completion status")
    start_date: Optional[str] = Field(None, description="Filter tasks starting from this date")
    end_date: Optional[str] = Field(None, description="Filter tasks ending before this date")

########################################################################################################################
####################################### Schema for task statistics ######################################################

class TaskStats(BaseModel):
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    cancelled_tasks: int
    completion_rate: float
    
#############################################################################################################################