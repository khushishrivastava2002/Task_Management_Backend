import time
from typing import Optional, List
from fastapi import HTTPException, status
from task_management.helper import epoch_to_human_time, validate_user_exists
from .models import Tasks
from .schemas import TaskCreate, TaskUpdate, TaskResponse, TaskFilter, TaskStats, human_time_to_epoch


#################################################################################################################
############################## Create a new task for a user #####################################################

async def create_task(user_id: str, task_data: TaskCreate) -> TaskResponse:
    """Create a new task for the authenticated user"""
    
    # Validate user exists and is active
    if not await validate_user_exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    # Convert human readable times to epoch
    try:
        start_epoch = human_time_to_epoch(task_data.start_task_time)
        end_epoch = human_time_to_epoch(task_data.end_task_time)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid time format: {str(e)}"
        )
    
    # Validate that end time is after start time
    if end_epoch <= start_epoch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Create task
    task = Tasks(
        title=task_data.title,
        description=task_data.description,
        user_id=user_id,
        start_task_time=start_epoch,
        end_task_time=end_epoch,
        priority=task_data.priority or "medium",
        status=task_data.status or "pending",
        created_at=int(time.time())
    )
    
    await task.insert()
    
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        start_task_time=task.start_task_time,
        end_task_time=task.end_task_time,
        start_task_time_human=epoch_to_human_time(task.start_task_time),
        end_task_time_human=epoch_to_human_time(task.end_task_time),
        is_completed=task.is_completed,
        is_active=task.is_active,
        priority=task.priority,
        status=task.status
    )

#####################################################################################################################
################### Get all tasks for a user with optional filtering ################################################

async def get_user_tasks(user_id: str, task_filter: Optional[TaskFilter] = None) -> List[TaskResponse]:
    """Get all tasks for a specific user with optional filtering"""
    
    # Validate user exists
    if not await validate_user_exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    # Build query
    query = {"user_id": user_id, "is_active": True}
    
    # Apply filters if provided
    if task_filter:
        if task_filter.status:
            query["status"] = task_filter.status.lower()
        if task_filter.priority:
            query["priority"] = task_filter.priority.lower()
        if task_filter.is_completed is not None:
            query["is_completed"] = task_filter.is_completed
        
        # Date range filtering
        if task_filter.start_date:
            try:
                start_epoch = human_time_to_epoch(task_filter.start_date)
                query["start_task_time"] = {"$gte": start_epoch}
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format"
                )
        
        if task_filter.end_date:
            try:
                end_epoch = human_time_to_epoch(task_filter.end_date)
                if "end_task_time" not in query:
                    query["end_task_time"] = {}
                query["end_task_time"]["$lte"] = end_epoch
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format"
                )
    
    # Get tasks
    tasks = await Tasks.find(query).sort("-created_at").to_list()
    
    return [
        TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            start_task_time=task.start_task_time,
            end_task_time=task.end_task_time,
            start_task_time_human=epoch_to_human_time(task.start_task_time),
            end_task_time_human=epoch_to_human_time(task.end_task_time),
            is_completed=task.is_completed,
            is_active=task.is_active,
            priority=task.priority,
            status=task.status
        ) for task in tasks
    ]


##############################################################################################################
############################# Get a specific task by ID ######################################################

async def get_task_by_id(user_id: str, task_id: str) -> TaskResponse:
    """Get a specific task by ID for a user"""
    
    # Validate user exists
    if not await validate_user_exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    try:
        task = await Tasks.get(task_id)
        if not task or not task.is_active or task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        start_task_time=task.start_task_time,
        end_task_time=task.end_task_time,
        start_task_time_human=epoch_to_human_time(task.start_task_time),
        end_task_time_human=epoch_to_human_time(task.end_task_time),
        is_completed=task.is_completed,
        is_active=task.is_active,
        priority=task.priority,
        status=task.status
    )

#########################################################################################################################
######################################## Update a task ##################################################################

async def update_task(user_id: str, task_id: str, task_data: TaskUpdate) -> TaskResponse:
    """Update a specific task for a user"""
    
    # Validate user exists
    if not await validate_user_exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    try:
        task = await Tasks.get(task_id)
        if not task or not task.is_active or task.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Prepare update data
    update_data = {}
    
    if task_data.title is not None:
        update_data["title"] = task_data.title
    if task_data.description is not None:
        update_data["description"] = task_data.description
    if task_data.priority is not None:
        update_data["priority"] = task_data.priority.lower()
    if task_data.status is not None:
        update_data["status"] = task_data.status.lower()
        # Auto-complete task if status is completed
        if task_data.status.lower() == "completed":
            update_data["is_completed"] = True
    if task_data.is_completed is not None:
        update_data["is_completed"] = task_data.is_completed
        # Auto-update status if marked as completed
        if task_data.is_completed:
            update_data["status"] = "completed"
    
    # Handle time updates
    start_epoch = task.start_task_time
    end_epoch = task.end_task_time
    
    if task_data.start_task_time is not None:
        try:
            start_epoch = human_time_to_epoch(task_data.start_task_time)
            update_data["start_task_time"] = start_epoch
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid start time format: {str(e)}"
            )
    
    if task_data.end_task_time is not None:
        try:
            end_epoch = human_time_to_epoch(task_data.end_task_time)
            update_data["end_task_time"] = end_epoch
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid end time format: {str(e)}"
            )
    
    # Validate time logic
    if end_epoch <= start_epoch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Update task
    if update_data:
        update_data["updated_at"] = int(time.time())
        await task.update({"$set": update_data})
        task = await Tasks.get(task_id)
    
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        created_at=task.created_at,
        updated_at=task.updated_at,
        start_task_time=task.start_task_time,
        end_task_time=task.end_task_time,
        start_task_time_human=epoch_to_human_time(task.start_task_time),
        end_task_time_human=epoch_to_human_time(task.end_task_time),
        is_completed=task.is_completed,
        is_active=task.is_active,
        priority=task.priority,
        status=task.status
    )

###############################################################################################################################
#################################### Delete a task (soft delete) ###############################################################

async def delete_task(user_id: str, task_id: str) -> bool:
    """Soft delete a task for a user"""
    
    # Validate user exists
    if not await validate_user_exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    try:
        task = await Tasks.get(task_id)
        if not task or not task.is_active or task.user_id != user_id:
            return False
    except:
        return False
    
    await task.update({"$set": {
        "is_active": False,
        "updated_at": int(time.time())
    }})
    
    return True

###############################################################################################################################
################################## Get task statistics for a user #############################################################

async def get_user_task_stats(user_id: str) -> TaskStats:
    """Get task statistics for a user"""
    
    # Validate user exists
    if not await validate_user_exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    # Get all active tasks for user
    tasks = await Tasks.find({"user_id": user_id, "is_active": True}).to_list()
    
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t.is_completed])
    pending_tasks = len([t for t in tasks if t.status == "pending"])
    in_progress_tasks = len([t for t in tasks if t.status == "in_progress"])
    cancelled_tasks = len([t for t in tasks if t.status == "cancelled"])
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    
    return TaskStats(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        in_progress_tasks=in_progress_tasks,
        cancelled_tasks=cancelled_tasks,
        completion_rate=round(completion_rate, 2)
    )

#############################################################################################################################
################################## Mark task as completed ###################################################################

async def mark_task_completed(user_id: str, task_id: str) -> TaskResponse:
    """Mark a task as completed"""
    
    update_data = TaskUpdate(
        is_completed=True,
        status="completed"
    )
    
    return await update_task(user_id, task_id, update_data)

##############################################################################################################################
################################### Get overdue tasks for a user #############################################################

async def get_overdue_tasks(user_id: str) -> List[TaskResponse]:
    """Get overdue tasks for a user"""
    
    # Validate user exists
    if not await validate_user_exists(user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    current_time = int(time.time())
    
    # Find tasks that are not completed and past their end time
    tasks = await Tasks.find({
        "user_id": user_id,
        "is_active": True,
        "is_completed": False,
        "end_task_time": {"$lt": current_time}
    }).sort("-end_task_time").to_list()
    
    return [
        TaskResponse(
            id=str(task.id),
            title=task.title,
            description=task.description,
            user_id=task.user_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            start_task_time=task.start_task_time,
            end_task_time=task.end_task_time,
            start_task_time_human=epoch_to_human_time(task.start_task_time),
            end_task_time_human=epoch_to_human_time(task.end_task_time),
            is_completed=task.is_completed,
            is_active=task.is_active,
            priority=task.priority,
            status=task.status
        ) for task in tasks
    ]
    
####################################################################################################################