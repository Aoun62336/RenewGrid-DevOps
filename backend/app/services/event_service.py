"""
services/event_service.py — Centralized event dispatching system.
"""
from fastapi import BackgroundTasks
from app.services.notification_service import create_notification_bg
from app.services.reward_service import create_reward_for_pickup
from app.models.core import PickupRequest
from app.models.user import User

def handle_pickup_completed(background_tasks: BackgroundTasks, pickup: PickupRequest):
    background_tasks.add_task(
        create_notification_bg,
        user_id=pickup.user_id,
        title="Pickup Completed",
        message=f"Your pickup request #{pickup.id} has been successfully completed!"
    )
    background_tasks.add_task(
        create_reward_for_pickup,
        pickup_id=pickup.id,
        user_id=pickup.user_id,
        weight_kg=pickup.final_collected_weight or 0.0,
    )

def handle_pickup_assigned(background_tasks: BackgroundTasks, pickup: PickupRequest, collector: User):
    background_tasks.add_task(
        create_notification_bg,
        user_id=pickup.user_id,
        title="Pickup Assigned",
        message=f"Your pickup request #{pickup.id} has been assigned to a collector."
    )
    background_tasks.add_task(
        create_notification_bg,
        user_id=collector.id,
        title="New Pickup Assigned",
        message=f"You have been assigned to pickup request #{pickup.id} at {pickup.address}."
    )

def handle_waste_uploaded(background_tasks: BackgroundTasks, user_id: int, waste_id: int):
    background_tasks.add_task(
        create_notification_bg,
        user_id=user_id,
        title="Waste Uploaded Successfully",
        message=f"Your waste upload #{waste_id} has been recorded and is awaiting review."
    )
