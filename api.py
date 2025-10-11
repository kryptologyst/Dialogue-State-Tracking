from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import uvicorn
import json
from datetime import datetime

from dialogue_tracker import AdvancedDialogueStateTracker, DialogueState
from database import MockDatabase, Restaurant, Reservation

# Initialize FastAPI app
app = FastAPI(
    title="Advanced Dialogue State Tracking API",
    description="A modern dialogue state tracking system for restaurant booking",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
dialogue_tracker = AdvancedDialogueStateTracker()
db = MockDatabase()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Pydantic models
class UserMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class SystemResponse(BaseModel):
    response: str
    state: Dict[str, Any]
    suggestions: List[str]
    restaurants: Optional[List[Dict[str, Any]]] = None
    session_id: str

class RestaurantResponse(BaseModel):
    id: int
    name: str
    location: str
    cuisine: str
    rating: float
    price_range: str
    capacity: int
    phone: str
    address: str
    description: str

class BookingRequest(BaseModel):
    restaurant_id: int
    customer_name: str
    party_size: int
    reservation_time: str

# Session management (in production, use Redis or database)
sessions: Dict[str, AdvancedDialogueStateTracker] = {}

def get_session(session_id: str) -> AdvancedDialogueStateTracker:
    """Get or create a session"""
    if session_id not in sessions:
        sessions[session_id] = AdvancedDialogueStateTracker()
    return sessions[session_id]

def generate_session_id() -> str:
    """Generate a unique session ID"""
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now())}"

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main chat interface"""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dialogue State Tracking Demo</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
            }
            .chat-container {
                height: 500px;
                overflow-y: auto;
                padding: 20px;
                background: #f8f9fa;
            }
            .message {
                margin: 10px 0;
                padding: 15px;
                border-radius: 10px;
                max-width: 70%;
            }
            .user-message {
                background: #667eea;
                color: white;
                margin-left: auto;
                text-align: right;
            }
            .bot-message {
                background: white;
                border: 1px solid #e9ecef;
                margin-right: auto;
            }
            .input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e9ecef;
            }
            .input-group {
                display: flex;
                gap: 10px;
            }
            input[type="text"] {
                flex: 1;
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 25px;
                outline: none;
                font-size: 16px;
            }
            button {
                padding: 12px 24px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background: #5a6fd8;
            }
            .state-display {
                background: #e3f2fd;
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
                border-left: 4px solid #2196f3;
            }
            .suggestions {
                margin-top: 10px;
            }
            .suggestion {
                display: inline-block;
                background: #f0f0f0;
                padding: 5px 10px;
                margin: 2px;
                border-radius: 15px;
                cursor: pointer;
                font-size: 12px;
            }
            .suggestion:hover {
                background: #e0e0e0;
            }
            .restaurant-card {
                background: white;
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🍽️ Restaurant Booking Assistant</h1>
                <p>Advanced Dialogue State Tracking Demo</p>
            </div>
            <div class="chat-container" id="chatContainer">
                <div class="bot-message">
                    <p>Hello! I'm your restaurant booking assistant. I can help you find and book a table at a restaurant. What would you like to do?</p>
                    <div class="suggestions">
                        <span class="suggestion" onclick="sendMessage('I want to book a table')">Book a table</span>
                        <span class="suggestion" onclick="sendMessage('Find restaurants in New York')">Find restaurants</span>
                        <span class="suggestion" onclick="sendMessage('Show me Chinese restaurants')">Chinese food</span>
                    </div>
                </div>
            </div>
            <div class="input-container">
                <div class="input-group">
                    <input type="text" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>

        <script>
            let sessionId = null;

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }

            async function sendMessage(message = null) {
                const input = document.getElementById('messageInput');
                const messageText = message || input.value.trim();
                
                if (!messageText) return;

                // Add user message to chat
                addMessage(messageText, 'user');
                input.value = '';

                // Get or create session ID
                if (!sessionId) {
                    sessionId = 'session_' + Date.now();
                }

                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            message: messageText,
                            session_id: sessionId
                        })
                    });

                    const data = await response.json();
                    
                    // Add bot response to chat
                    addMessage(data.response, 'bot', data.state, data.suggestions, data.restaurants);
                    
                } catch (error) {
                    console.error('Error:', error);
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                }
            }

            function addMessage(text, sender, state = null, suggestions = [], restaurants = []) {
                const chatContainer = document.getElementById('chatContainer');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                
                let content = `<p>${text}</p>`;
                
                if (state && sender === 'bot') {
                    const filledSlots = Object.entries(state.slots).filter(([k, v]) => v !== null);
                    if (filledSlots.length > 0) {
                        content += `<div class="state-display">
                            <strong>Current Booking Info:</strong><br>
                            ${filledSlots.map(([key, value]) => `${key}: ${value}`).join('<br>')}
                        </div>`;
                    }
                }
                
                if (suggestions && suggestions.length > 0) {
                    content += `<div class="suggestions">
                        ${suggestions.map(s => `<span class="suggestion" onclick="sendMessage('${s}')">${s}</span>`).join('')}
                    </div>`;
                }
                
                if (restaurants && restaurants.length > 0) {
                    content += '<div><strong>Restaurant Suggestions:</strong></div>';
                    restaurants.forEach(restaurant => {
                        content += `<div class="restaurant-card">
                            <strong>${restaurant.name}</strong><br>
                            ${restaurant.cuisine} • ${restaurant.location}<br>
                            ⭐ ${restaurant.rating} • ${restaurant.price_range}<br>
                            <small>${restaurant.description}</small>
                        </div>`;
                    });
                }
                
                messageDiv.innerHTML = content;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.post("/chat", response_model=SystemResponse)
async def chat(user_message: UserMessage):
    """Main chat endpoint for dialogue state tracking"""
    try:
        # Get session
        session_id = user_message.session_id or generate_session_id()
        tracker = get_session(session_id)
        
        # Update dialogue state
        state = tracker.update_state(user_message.message)
        
        # Generate system response
        response, suggestions, restaurants = await generate_response(tracker, user_message.message)
        
        return SystemResponse(
            response=response,
            state=tracker.get_state_summary(),
            suggestions=suggestions,
            restaurants=restaurants,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def generate_response(tracker: AdvancedDialogueStateTracker, user_input: str) -> tuple:
    """Generate appropriate system response based on dialogue state"""
    state = tracker.state
    suggestions = []
    restaurants = []
    
    # Intent-based responses
    if state.intent == "book_table":
        missing_slots = tracker.get_missing_slots()
        
        if not missing_slots:
            # All slots filled, proceed with booking
            response = "Great! I have all the information needed for your reservation. Let me find suitable restaurants and make a booking for you."
            
            # Find restaurants based on slots
            found_restaurants = db.get_restaurants(
                location=state.slots.get("location"),
                cuisine=state.slots.get("cuisine")
            )
            
            if found_restaurants:
                restaurants = [asdict(r) for r in found_restaurants[:3]]  # Top 3
                response += f" I found {len(found_restaurants)} restaurants matching your criteria."
                suggestions = ["Book this restaurant", "Show me more options", "Change my preferences"]
            else:
                response += " I couldn't find any restaurants matching your criteria. Would you like to try different preferences?"
                suggestions = ["Change location", "Change cuisine", "Try again"]
        else:
            # Missing slots, ask for them
            slot_questions = {
                "location": "Where would you like to dine?",
                "cuisine": "What type of cuisine would you prefer?",
                "party_size": "How many people will be dining?",
                "reservation_time": "What time would you like to make the reservation for?"
            }
            
            next_slot = missing_slots[0]
            response = slot_questions.get(next_slot, f"Could you please provide {next_slot}?")
            
            # Add suggestions based on missing slots
            if next_slot == "location":
                suggestions = ["New York", "Los Angeles", "Chicago", "San Francisco"]
            elif next_slot == "cuisine":
                suggestions = ["Chinese", "Italian", "Japanese", "Indian", "French"]
            elif next_slot == "party_size":
                suggestions = ["2 people", "4 people", "6 people", "8 people"]
            elif next_slot == "reservation_time":
                suggestions = ["7 PM", "8 PM", "7:30 PM", "8:30 PM"]
    
    elif state.intent == "find_restaurant":
        # Find restaurants based on current slots
        found_restaurants = db.get_restaurants(
            location=state.slots.get("location"),
            cuisine=state.slots.get("cuisine")
        )
        
        if found_restaurants:
            restaurants = [asdict(r) for r in found_restaurants[:5]]
            response = f"I found {len(found_restaurants)} restaurants for you:"
            suggestions = ["Book a table", "Show more details", "Filter by rating"]
        else:
            response = "I couldn't find any restaurants matching your criteria. Could you provide more details?"
            suggestions = ["Try different location", "Try different cuisine", "Show all restaurants"]
    
    elif state.intent == "get_info":
        response = "I can help you with restaurant information. What would you like to know?"
        suggestions = ["Show menu", "Show prices", "Show hours", "Show location"]
    
    else:
        response = "I'm here to help you with restaurant bookings. What would you like to do?"
        suggestions = ["Book a table", "Find restaurants", "Get restaurant info"]
    
    return response, suggestions, restaurants

@app.get("/restaurants", response_model=List[RestaurantResponse])
async def get_restaurants(location: Optional[str] = None, cuisine: Optional[str] = None):
    """Get restaurants with optional filters"""
    restaurants = db.get_restaurants(location=location, cuisine=cuisine)
    return [RestaurantResponse(**asdict(r)) for r in restaurants]

@app.post("/book")
async def make_booking(booking_request: BookingRequest):
    """Make a restaurant booking"""
    try:
        # Check availability
        if not db.check_availability(
            booking_request.restaurant_id,
            booking_request.party_size,
            booking_request.reservation_time
        ):
            raise HTTPException(status_code=400, detail="Restaurant not available at requested time")
        
        # Create reservation
        reservation_id = db.create_reservation(
            booking_request.restaurant_id,
            booking_request.customer_name,
            booking_request.party_size,
            booking_request.reservation_time
        )
        
        return {
            "success": True,
            "reservation_id": reservation_id,
            "message": "Reservation created successfully!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
