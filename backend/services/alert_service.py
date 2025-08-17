import os
from typing import List, Dict, Any
from datetime import datetime
from ..models.ai_models import AIAlert, AIAlertCreate, AIAlertTrigger
from ..mock.data import mockYieldData

class AlertService:
    def __init__(self):
        self.alerts_storage = []  # In production, this would be MongoDB
        
    def create_alert(self, alert_data: AIAlertCreate) -> AIAlert:
        """Create a new AI alert"""
        alert = AIAlert(**alert_data.dict())
        self.alerts_storage.append(alert)
        return alert
    
    def get_user_alerts(self, user_email: str) -> List[AIAlert]:
        """Get all alerts for a user"""
        return [alert for alert in self.alerts_storage if alert.user_email == user_email]
    
    def delete_alert(self, alert_id: str, user_email: str) -> bool:
        """Delete an alert (user can only delete their own)"""
        for i, alert in enumerate(self.alerts_storage):
            if alert.id == alert_id and alert.user_email == user_email:
                del self.alerts_storage[i]
                return True
        return False
    
    def check_alerts(self) -> List[AIAlertTrigger]:
        """Check all active alerts against current data"""
        triggered_alerts = []
        
        try:
            # Get current yield data
            current_yields = {item['stablecoin']: item['currentYield'] for item in mockYieldData}
            
            for alert in self.alerts_storage:
                if not alert.is_active:
                    continue
                    
                stablecoin = alert.stablecoin.upper()
                if stablecoin not in current_yields:
                    continue
                
                current_value = current_yields[stablecoin]
                threshold = alert.threshold
                condition = alert.condition
                
                # Check if condition is met
                triggered = False
                if condition == ">" and current_value > threshold:
                    triggered = True
                elif condition == "<" and current_value < threshold:
                    triggered = True
                elif condition == ">=" and current_value >= threshold:
                    triggered = True
                elif condition == "<=" and current_value <= threshold:
                    triggered = True
                elif condition == "=" and abs(current_value - threshold) < 0.01:
                    triggered = True
                
                if triggered:
                    # Create trigger record
                    trigger = AIAlertTrigger(
                        alert_id=alert.id,
                        triggered_at=datetime.utcnow(),
                        current_value=current_value,
                        threshold=threshold,
                        message=f"🚨 StableYield Alert: {stablecoin} yield is now {current_value:.2f}% (condition: {condition} {threshold:.2f}%)"
                    )
                    
                    triggered_alerts.append(trigger)
                    
                    # Update alert last_triggered
                    alert.last_triggered = datetime.utcnow()
        
        except Exception as e:
            print(f"Error checking alerts: {e}")
            
        return triggered_alerts
    
    def format_alert_email(self, trigger: AIAlertTrigger, alert: AIAlert) -> Dict[str, str]:
        """Format alert for email sending"""
        subject = f"StableYield Alert: {alert.stablecoin} Yield Update"
        
        body = f"""
StableYield AI Alert Triggered

Hello,

Your yield alert has been triggered:

🪙 Stablecoin: {alert.stablecoin}
📊 Current Yield: {trigger.current_value:.2f}%
🎯 Your Threshold: {alert.condition} {trigger.threshold:.2f}%
⏰ Triggered At: {trigger.triggered_at.strftime('%Y-%m-%d %H:%M:%S UTC')}

{trigger.message}

---
Manage your alerts: [Dashboard Link]

⚠️ Disclaimer: This alert is based on simulation data. Not financial advice. Always verify current rates before making investment decisions.

Best regards,
StableYield Team
        """
        
        return {
            "subject": subject,
            "body": body.strip(),
            "recipient": alert.user_email
        }
    
    def get_alert_conditions(self) -> List[Dict[str, str]]:
        """Get available alert conditions"""
        return [
            {"value": ">", "label": "Greater than (>)"},
            {"value": ">=", "label": "Greater than or equal (≥)"},
            {"value": "<", "label": "Less than (<)"},
            {"value": "<=", "label": "Less than or equal (≤)"},
            {"value": "=", "label": "Equal to (=)"}
        ]
    
    def get_available_stablecoins(self) -> List[str]:
        """Get list of stablecoins available for alerts"""
        return [item['stablecoin'] for item in mockYieldData]