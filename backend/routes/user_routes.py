from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.yield_models import User, WaitlistSignup, NewsletterSignup, UserCreate
import logging

router = APIRouter(prefix="/users", tags=["User Management"])
logger = logging.getLogger(__name__)

# In-memory storage for now (will be replaced with MongoDB)
users_storage = []

@router.post("/waitlist", response_model=User)
async def join_waitlist(signup_data: WaitlistSignup):
    """Join the StableYield waitlist"""
    try:
        # Check if user already exists
        existing_user = next(
            (user for user in users_storage if user.email == signup_data.email and user.signupType == "waitlist"),
            None
        )
        
        if existing_user:
            return existing_user
            
        # Create new user
        user = User(
            email=signup_data.email,
            name=signup_data.name,
            signupType="waitlist",
            interest=signup_data.interest,
            signupDate=datetime.utcnow(),
            isActive=True
        )
        
        users_storage.append(user)
        
        # In production, this would also:
        # 1. Save to MongoDB
        # 2. Send welcome email
        # 3. Add to email marketing list
        
        logger.info(f"New waitlist signup: {signup_data.email}")
        
        return user
        
    except Exception as e:
        logger.error(f"Waitlist signup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to join waitlist: {str(e)}")

@router.post("/newsletter", response_model=User)
async def subscribe_newsletter(signup_data: NewsletterSignup):
    """Subscribe to StableYield newsletter"""
    try:
        # Check if user already exists
        existing_user = next(
            (user for user in users_storage if user.email == signup_data.email and user.signupType == "newsletter"),
            None
        )
        
        if existing_user:
            return existing_user
            
        # Create new user
        user = User(
            email=signup_data.email,
            name=signup_data.name,
            signupType="newsletter",
            signupDate=datetime.utcnow(),
            isActive=True
        )
        
        users_storage.append(user)
        
        # In production, this would also:
        # 1. Save to MongoDB
        # 2. Send confirmation email
        # 3. Add to newsletter list
        
        logger.info(f"New newsletter subscription: {signup_data.email}")
        
        return user
        
    except Exception as e:
        logger.error(f"Newsletter subscription error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to subscribe: {str(e)}")

@router.get("/{email}")
async def get_user(email: str):
    """Get user data by email"""
    try:
        users = [user for user in users_storage if user.email == email]
        
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
            
        return {
            "email": email,
            "signups": users,
            "total_signups": len(users)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")

@router.put("/{email}")
async def update_user(email: str, user_data: dict):
    """Update user preferences"""
    try:
        updated_users = []
        found = False
        
        for user in users_storage:
            if user.email == email:
                found = True
                # Update user fields
                if 'name' in user_data:
                    user.name = user_data['name']
                if 'interest' in user_data:
                    user.interest = user_data['interest']
                if 'isActive' in user_data:
                    user.isActive = user_data['isActive']
                    
                updated_users.append(user)
            else:
                updated_users.append(user)
                
        if not found:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Update storage
        users_storage.clear()
        users_storage.extend(updated_users)
        
        return {"message": "User updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@router.get("/stats/summary")
async def get_user_stats():
    """Get user registration statistics"""
    try:
        waitlist_users = [user for user in users_storage if user.signupType == "waitlist" and user.isActive]
        newsletter_users = [user for user in users_storage if user.signupType == "newsletter" and user.isActive]
        
        # Count by interest for waitlist users
        interest_breakdown = {}
        for user in waitlist_users:
            interest = user.interest or "unknown"
            interest_breakdown[interest] = interest_breakdown.get(interest, 0) + 1
            
        stats = {
            "total_users": len(users_storage),
            "waitlist_signups": len(waitlist_users),
            "newsletter_subscribers": len(newsletter_users),
            "interest_breakdown": interest_breakdown,
            "recent_signups": len([
                user for user in users_storage 
                if (datetime.utcnow() - user.signupDate).days <= 7
            ]),
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate stats: {str(e)}")

@router.delete("/{email}/{signup_type}")
async def unsubscribe_user(email: str, signup_type: str):
    """Unsubscribe user from waitlist or newsletter"""
    try:
        if signup_type not in ["waitlist", "newsletter"]:
            raise HTTPException(status_code=400, detail="Invalid signup type")
            
        updated_users = []
        found = False
        
        for user in users_storage:
            if user.email == email and user.signupType == signup_type:
                found = True
                user.isActive = False
                updated_users.append(user)
            else:
                updated_users.append(user)
                
        if not found:
            raise HTTPException(status_code=404, detail="User subscription not found")
            
        # Update storage
        users_storage.clear()
        users_storage.extend(updated_users)
        
        return {"message": f"Successfully unsubscribed from {signup_type}"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unsubscribe: {str(e)}")

@router.post("/export")
async def export_users(signup_type: Optional[str] = None):
    """Export user data (admin endpoint)"""
    try:
        if signup_type:
            filtered_users = [user for user in users_storage if user.signupType == signup_type and user.isActive]
        else:
            filtered_users = [user for user in users_storage if user.isActive]
            
        # Convert to dict for JSON serialization
        export_data = [
            {
                "email": user.email,
                "name": user.name,
                "signup_type": user.signupType,
                "interest": user.interest,
                "signup_date": user.signupDate.isoformat(),
                "is_active": user.isActive
            }
            for user in filtered_users
        ]
        
        return {
            "total_users": len(export_data),
            "export_date": datetime.utcnow().isoformat(),
            "users": export_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export users: {str(e)}")