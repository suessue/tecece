import uvicorn
import hmac
import hashlib
import time
import json
import os
from fastapi import FastAPI, Request, HTTPException, Depends, Header
from typing import Optional

import config

app = FastAPI(title="API Spec Change Webhook Server")

# Store received notifications in memory for demo purposes
notifications = []

async def verify_signature(
    request: Request,
    x_webhook_timestamp: Optional[str] = Header(None),
    x_webhook_signature: Optional[str] = Header(None)
):
    """Verify the webhook signature to ensure it's coming from our API monitor."""
    if not config.WEBHOOK_SECRET:
        # If no secret is set, skip verification
        return True
    
    if not x_webhook_timestamp or not x_webhook_signature:
        raise HTTPException(status_code=401, detail="Missing webhook signature headers")
    
    # Check if timestamp is recent (within 5 minutes)
    try:
        timestamp = int(x_webhook_timestamp)
        current_time = int(time.time())
        if abs(current_time - timestamp) > 300:  # 5 minutes
            raise HTTPException(status_code=401, detail="Webhook timestamp expired")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid webhook timestamp")
    
    # Get request body to verify signature
    body = await request.body()
    body_str = body.decode('utf-8')
    
    # Calculate expected signature
    signature_message = f"{x_webhook_timestamp}.{body_str}"
    expected_signature = hmac.new(
        config.WEBHOOK_SECRET.encode('utf-8'),
        signature_message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Verify signature
    if not hmac.compare_digest(expected_signature, x_webhook_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    return True

@app.post("/webhook")
async def webhook_handler(request: Request, verified: bool = Depends(verify_signature)):
    """Handle incoming webhook notifications from API specification monitor."""
    payload = await request.json()
    
    # Add notification to our list
    notifications.append({
        "received_at": time.time(),
        "payload": payload
    })
    
    print(f"\n=== API SPECIFICATION CHANGE DETECTED ===\n")
    print(f"Event Type: {payload.get('event_type')}")
    print(f"Timestamp: {payload.get('timestamp')}")
    print(f"Source: {payload.get('source')}")
    print(f"\nSummary:\n{payload.get('summary')}")
    print("\n============================================\n")
    
    return {"status": "success", "message": "Webhook notification received"}

@app.get("/notifications")
async def list_notifications():
    """List all received notifications for demo purposes."""
    return {"notifications": notifications}

def start_server():
    """Start the webhook server."""
    print(f"Starting webhook server at http://{config.WEBHOOK_SERVER_HOST}:{config.WEBHOOK_SERVER_PORT}")
    print(f"Send webhook notifications to http://{config.WEBHOOK_SERVER_HOST}:{config.WEBHOOK_SERVER_PORT}/webhook")
    
    uvicorn.run(
        app, 
        host=config.WEBHOOK_SERVER_HOST, 
        port=config.WEBHOOK_SERVER_PORT
    )

if __name__ == "__main__":
    start_server() 