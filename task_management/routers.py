from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from .schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TaskFilter, TaskStats
)
from .services import (
    create_task, get_user_tasks, get_task_by_id, update_task, 
    delete_task, get_user_task_stats, mark_task_completed, get_overdue_tasks
)
from datetime import datetime, date
from auth.routers import get_current_api_key


################################################################################################################################
############### API routers for task management ###############################################################################

task_router = APIRouter(prefix="/tasks", tags=["Task Management"])

################################################################################################################################
############ Create a new task for authenticated user ##########################################################################

@task_router.post("/", response_model=TaskResponse)
async def create_user_task(
    task_data: TaskCreate,
    user_id: str = Query(..., description="ID of the user creating the task"),
    current_key = Depends(get_current_api_key)
):
    """Create a new task for a user (requires API key authentication)"""
    return await create_task(user_id, task_data)

################################################################################################################################
########### Get all tasks for a user with optional filtering ###################################################################

@task_router.get("/", response_model=List[TaskResponse])
async def get_tasks_for_user(
    user_id: str = Query(..., description="ID of the user"),
    status: Optional[str] = Query(None, description="Filter by status: pending, in_progress, completed, cancelled"),
    priority: Optional[str] = Query(None, description="Filter by priority: low, medium, high"),
    is_completed: Optional[bool] = Query(None, description="Filter by completion status"),
    start_date: Optional[str] = Query(None, description="Filter tasks starting from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter tasks ending before this date (YYYY-MM-DD)"),
    current_key = Depends(get_current_api_key)
):
    """Get all tasks for a user with optional filtering (requires API key authentication)"""
    
    # Create filter object if any filters are provided
    task_filter = None
    if any([status, priority, is_completed, start_date, end_date]):
        task_filter = TaskFilter(
            status=status,
            priority=priority,
            is_completed=is_completed,
            start_date=start_date,
            end_date=end_date
        )
    
    return await get_user_tasks(user_id, task_filter)

################################################################################################################################
############ Get a specific task by ID ########################################################################################

@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    user_id: str = Query(..., description="ID of the user who owns the task"),
    current_key = Depends(get_current_api_key)
):
    """Get a specific task by ID (requires API key authentication)"""
    return await get_task_by_id(user_id, task_id)

################################################################################################################################
############ Update a specific task #########################################################################################

@task_router.put("/{task_id}", response_model=TaskResponse)
async def update_user_task(
    task_id: str,
    task_data: TaskUpdate,
    user_id: str = Query(..., description="ID of the user who owns the task"),
    current_key = Depends(get_current_api_key)
):
    """Update a specific task (requires API key authentication)"""
    return await update_task(user_id, task_id, task_data)

################################################################################################################################
############ Delete a specific task (soft delete) ##########################################################################

@task_router.delete("/{task_id}")
async def delete_user_task(
    task_id: str,
    user_id: str = Query(..., description="ID of the user who owns the task"),
    current_key = Depends(get_current_api_key)
):
    """Delete a specific task (soft delete - requires API key authentication)"""
    success = await delete_task(user_id, task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return {"message": "Task deleted successfully"}

################################################################################################################################
############ Mark a task as completed ######################################################################################

@task_router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    user_id: str = Query(..., description="ID of the user who owns the task"),
    current_key = Depends(get_current_api_key)
):
    """Mark a task as completed (requires API key authentication)"""
    return await mark_task_completed(user_id, task_id)

################################################################################################################################
############ Get task statistics for a user ################################################################################

@task_router.get("/stats/summary", response_model=TaskStats)
async def get_task_statistics(
    user_id: str = Query(..., description="ID of the user"),
    current_key = Depends(get_current_api_key)
):
    """Get task statistics for a user (requires API key authentication)"""
    return await get_user_task_stats(user_id)

################################################################################################################################
############ Get overdue tasks for a user ##################################################################################

@task_router.get("/overdue/list", response_model=List[TaskResponse])
async def get_user_overdue_tasks(
    user_id: str = Query(..., description="ID of the user"),
    current_key = Depends(get_current_api_key)
):
    """Get overdue tasks for a user (requires API key authentication)"""
    return await get_overdue_tasks(user_id)

################################################################################################################################
############ Get tasks by priority ##########################################################################################

@task_router.get("/priority/{priority}", response_model=List[TaskResponse])
async def get_tasks_by_priority(
    priority: str,
    user_id: str = Query(..., description="ID of the user"),
    current_key = Depends(get_current_api_key)
):
    """Get tasks filtered by priority (requires API key authentication)"""
    task_filter = TaskFilter(priority=priority)
    return await get_user_tasks(user_id, task_filter)

################################################################################################################################
############ Get tasks by status ############################################################################################

@task_router.get("/status/{status}", response_model=List[TaskResponse])
async def get_tasks_by_status(
    status: str,
    user_id: str = Query(..., description="ID of the user"),
    current_key = Depends(get_current_api_key)
):
    """Get tasks filtered by status (requires API key authentication)"""
    task_filter = TaskFilter(status=status)
    return await get_user_tasks(user_id, task_filter)

################################################################################################################################
############ Get today's tasks for a user ###################################################################################

@task_router.get("/today/list", response_model=List[TaskResponse])
async def get_today_tasks(
    user_id: str = Query(..., description="ID of the user"),
    current_key = Depends(get_current_api_key)
):
    """Get tasks scheduled for today (requires API key authentication)"""
        
    today = date.today()
    today_str = today.strftime('%Y-%m-%d')
    
    task_filter = TaskFilter(
        start_date=today_str,
        end_date=today_str
    )
    return await get_user_tasks(user_id, task_filter)

##########################################################################################################################