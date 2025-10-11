import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
from datetime import datetime

from api import app, get_session, generate_response
from dialogue_tracker import AdvancedDialogueStateTracker, DialogueState
from database import MockDatabase, Restaurant, Reservation

# Initialize test client
client = TestClient(app)

class TestDialogueStateTracker:
    """Test cases for the dialogue state tracker"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.tracker = AdvancedDialogueStateTracker()
    
    def test_initial_state(self):
        """Test initial dialogue state"""
        assert self.tracker.state.intent is None
        assert self.tracker.state.turn_count == 0
        assert all(v is None for v in self.tracker.state.slots.values())
    
    def test_intent_extraction(self):
        """Test intent extraction"""
        # Test booking intent
        intent, confidence = self.tracker.extract_intent("I want to book a table")
        assert intent == "book_table"
        assert confidence > 0
        
        # Test finding restaurant intent
        intent, confidence = self.tracker.extract_intent("Find restaurants in New York")
        assert intent == "find_restaurant"
        assert confidence > 0
    
    def test_slot_extraction(self):
        """Test slot extraction"""
        # Test location extraction
        slots = self.tracker.extract_slots("I want to book a table in New York")
        assert slots.get("location") == "New York"
        
        # Test cuisine extraction
        slots = self.tracker.extract_slots("I want Chinese food")
        assert slots.get("cuisine") == "Chinese"
        
        # Test party size extraction
        slots = self.tracker.extract_slots("We are 4 people")
        assert slots.get("party_size") == 4
        
        # Test time extraction
        slots = self.tracker.extract_slots("Make it for 7 PM")
        assert slots.get("reservation_time") == "7 PM"
    
    def test_state_update(self):
        """Test dialogue state update"""
        # Update with booking request
        state = self.tracker.update_state("I want to book a table in New York for 4 people")
        
        assert state.intent == "book_table"
        assert state.slots["location"] == "New York"
        assert state.slots["party_size"] == 4
        assert state.turn_count == 1
        assert len(self.tracker.dialogue_history) == 1
    
    def test_missing_slots(self):
        """Test missing slots detection"""
        # Partial booking request
        self.tracker.update_state("I want to book a table")
        missing = self.tracker.get_missing_slots()
        
        assert "location" in missing
        assert "cuisine" in missing
        assert "party_size" in missing
        assert "reservation_time" in missing
    
    def test_booking_complete(self):
        """Test booking completion check"""
        # Complete booking request
        self.tracker.update_state("I want to book a table in New York for Chinese food for 4 people at 7 PM")
        
        assert self.tracker.is_booking_complete() == True
    
    def test_reset_state(self):
        """Test state reset"""
        self.tracker.update_state("I want to book a table")
        self.tracker.reset_state()
        
        assert self.tracker.state.intent is None
        assert self.tracker.state.turn_count == 0
        assert len(self.tracker.dialogue_history) == 0

class TestDatabase:
    """Test cases for the mock database"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.db = MockDatabase("test.db")
    
    def test_get_restaurants(self):
        """Test getting restaurants"""
        restaurants = self.db.get_restaurants()
        assert len(restaurants) > 0
        assert all(isinstance(r, Restaurant) for r in restaurants)
    
    def test_get_restaurants_with_filters(self):
        """Test getting restaurants with filters"""
        # Filter by location
        restaurants = self.db.get_restaurants(location="New York")
        assert all("New York" in r.location for r in restaurants)
        
        # Filter by cuisine
        restaurants = self.db.get_restaurants(cuisine="Chinese")
        assert all("Chinese" in r.cuisine for r in restaurants)
    
    def test_get_restaurant_by_id(self):
        """Test getting restaurant by ID"""
        restaurant = self.db.get_restaurant_by_id(1)
        assert restaurant is not None
        assert restaurant.id == 1
    
    def test_create_reservation(self):
        """Test creating a reservation"""
        reservation_id = self.db.create_reservation(
            restaurant_id=1,
            customer_name="John Doe",
            party_size=4,
            reservation_time="7 PM"
        )
        
        assert reservation_id is not None
        assert reservation_id > 0
    
    def test_check_availability(self):
        """Test availability checking"""
        # Test available restaurant
        available = self.db.check_availability(1, 4, "7 PM")
        assert available == True
        
        # Test unavailable (over capacity)
        available = self.db.check_availability(1, 100, "7 PM")
        assert available == False

class TestAPI:
    """Test cases for the FastAPI application"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns HTML"""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_chat_endpoint(self):
        """Test chat endpoint"""
        response = client.post("/chat", json={
            "message": "I want to book a table",
            "session_id": "test_session"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "state" in data
        assert "suggestions" in data
        assert "session_id" in data
    
    def test_restaurants_endpoint(self):
        """Test restaurants endpoint"""
        response = client.get("/restaurants")
        assert response.status_code == 200
        
        restaurants = response.json()
        assert isinstance(restaurants, list)
        assert len(restaurants) > 0
    
    def test_restaurants_with_filters(self):
        """Test restaurants endpoint with filters"""
        response = client.get("/restaurants?location=New York&cuisine=Chinese")
        assert response.status_code == 200
        
        restaurants = response.json()
        assert all("New York" in r["location"] for r in restaurants)
        assert all("Chinese" in r["cuisine"] for r in restaurants)
    
    def test_booking_endpoint(self):
        """Test booking endpoint"""
        response = client.post("/book", json={
            "restaurant_id": 1,
            "customer_name": "John Doe",
            "party_size": 4,
            "reservation_time": "7 PM"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "reservation_id" in data
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

@pytest.mark.asyncio
class TestAsyncFunctions:
    """Test cases for async functions"""
    
    async def test_generate_response(self):
        """Test response generation"""
        tracker = AdvancedDialogueStateTracker()
        tracker.update_state("I want to book a table")
        
        response, suggestions, restaurants = await generate_response(
            tracker, "I want to book a table"
        )
        
        assert isinstance(response, str)
        assert isinstance(suggestions, list)
        assert isinstance(restaurants, list)

class TestIntegration:
    """Integration tests"""
    
    def test_full_booking_flow(self):
        """Test complete booking flow"""
        # Start conversation
        response1 = client.post("/chat", json={
            "message": "I want to book a table",
            "session_id": "integration_test"
        })
        assert response1.status_code == 200
        
        # Provide location
        response2 = client.post("/chat", json={
            "message": "In New York",
            "session_id": "integration_test"
        })
        assert response2.status_code == 200
        
        # Provide cuisine
        response3 = client.post("/chat", json={
            "message": "Chinese food",
            "session_id": "integration_test"
        })
        assert response3.status_code == 200
        
        # Provide party size
        response4 = client.post("/chat", json={
            "message": "4 people",
            "session_id": "integration_test"
        })
        assert response4.status_code == 200
        
        # Provide time
        response5 = client.post("/chat", json={
            "message": "7 PM",
            "session_id": "integration_test"
        })
        assert response5.status_code == 200
        
        # Check final state
        final_state = response5.json()["state"]
        assert final_state["slots"]["location"] == "New York"
        assert final_state["slots"]["cuisine"] == "Chinese"
        assert final_state["slots"]["party_size"] == 4
        assert final_state["slots"]["reservation_time"] == "7 PM"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
