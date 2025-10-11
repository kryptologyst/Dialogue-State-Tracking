#!/usr/bin/env python3
"""
Project Summary and Demo Script
===============================

This script provides a comprehensive overview and demonstration
of the Advanced Dialogue State Tracking project.
"""

import json
import time
from datetime import datetime
from dialogue_tracker import AdvancedDialogueStateTracker
from database import MockDatabase

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"🎯 {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_conversation_flow():
    """Demonstrate a complete conversation flow"""
    print_header("Complete Conversation Flow Demo")
    
    tracker = AdvancedDialogueStateTracker()
    db = MockDatabase()
    
    # Simulate a realistic conversation
    conversation = [
        "Hi, I'd like to make a reservation",
        "We're looking for something in New York",
        "Chinese food would be great",
        "There will be 4 of us",
        "Can we get a table for 7:30 PM?",
        "Actually, make that 8 PM instead"
    ]
    
    print("🗣️  Simulating a restaurant booking conversation:")
    print()
    
    for i, user_input in enumerate(conversation, 1):
        print(f"Turn {i}: {user_input}")
        
        # Update dialogue state
        state = tracker.update_state(user_input)
        
        # Show extracted information
        print(f"   Intent: {state.intent} (confidence: {state.confidence:.2f})")
        
        filled_slots = {k: v for k, v in state.slots.items() if v is not None}
        if filled_slots:
            print(f"   Slots: {filled_slots}")
        
        # Check completion status
        if tracker.is_booking_complete():
            print("   ✅ Booking information complete!")
        else:
            missing = tracker.get_missing_slots()
            print(f"   ⏳ Still need: {', '.join(missing)}")
        
        print()
        time.sleep(1)  # Pause for readability
    
    # Show final state
    print_section("Final Dialogue State")
    final_state = tracker.get_state_summary()
    print(json.dumps(final_state, indent=2))
    
    # Find matching restaurants
    print_section("Matching Restaurants")
    restaurants = db.get_restaurants(
        location=state.slots.get("location"),
        cuisine=state.slots.get("cuisine")
    )
    
    if restaurants:
        print(f"Found {len(restaurants)} restaurants:")
        for restaurant in restaurants[:3]:
            print(f"  🍽️  {restaurant.name}")
            print(f"     📍 {restaurant.location} • {restaurant.cuisine}")
            print(f"     ⭐ {restaurant.rating} • {restaurant.price_range}")
            print(f"     👥 Capacity: {restaurant.capacity}")
            print()
    else:
        print("No restaurants found matching the criteria.")

def demo_intent_classification():
    """Demonstrate intent classification capabilities"""
    print_header("Intent Classification Demo")
    
    tracker = AdvancedDialogueStateTracker()
    
    test_inputs = [
        ("I want to book a table", "book_table"),
        ("Find me Italian restaurants", "find_restaurant"),
        ("Cancel my reservation", "cancel_reservation"),
        ("What's on the menu?", "get_info"),
        ("Change my booking to 8 PM", "modify_reservation")
    ]
    
    print("🧠 Testing intent classification:")
    print()
    
    for user_input, expected_intent in test_inputs:
        intent, confidence = tracker.extract_intent(user_input)
        status = "✅" if intent == expected_intent else "❌"
        
        print(f"{status} Input: '{user_input}'")
        print(f"   Expected: {expected_intent}")
        print(f"   Detected: {intent} (confidence: {confidence:.2f})")
        print()

def demo_slot_extraction():
    """Demonstrate slot extraction capabilities"""
    print_header("Slot Extraction Demo")
    
    tracker = AdvancedDialogueStateTracker()
    
    test_cases = [
        "Book a table for 6 people at Mario's Italian in New York for 7 PM",
        "I want Chinese food in Los Angeles for 4 people",
        "Reservation for John Smith at 8:30 PM",
        "Find restaurants near me with good ratings"
    ]
    
    print("🎯 Testing slot extraction:")
    print()
    
    for test_input in test_cases:
        print(f"Input: '{test_input}'")
        slots = tracker.extract_slots(test_input)
        
        if slots:
            print("Extracted slots:")
            for slot, value in slots.items():
                print(f"  • {slot}: {value}")
        else:
            print("No slots extracted")
        print()

def demo_api_capabilities():
    """Demonstrate API capabilities"""
    print_header("API Capabilities Overview")
    
    print("🌐 Available API Endpoints:")
    print()
    
    endpoints = [
        ("GET", "/", "Interactive web interface"),
        ("POST", "/chat", "Chat with the dialogue system"),
        ("GET", "/restaurants", "Get restaurant listings"),
        ("POST", "/book", "Make a reservation"),
        ("GET", "/health", "Health check"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"  {method:4} {endpoint:20} - {description}")
    
    print()
    print("📝 Example API Usage:")
    print()
    print("```bash")
    print("# Start the server")
    print("python api.py")
    print()
    print("# Chat with the system")
    print('curl -X POST "http://localhost:8000/chat" \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"message": "I want to book a table", "session_id": "user123"}\'')
    print("```")

def demo_database_features():
    """Demonstrate database features"""
    print_header("Database Features Demo")
    
    db = MockDatabase()
    
    print("🍽️  Restaurant Database:")
    print()
    
    # Show all restaurants
    restaurants = db.get_restaurants()
    print(f"Total restaurants: {len(restaurants)}")
    
    # Group by cuisine
    cuisines = {}
    for restaurant in restaurants:
        cuisine = restaurant.cuisine
        if cuisine not in cuisines:
            cuisines[cuisine] = []
        cuisines[cuisine].append(restaurant)
    
    print("\nRestaurants by cuisine:")
    for cuisine, rest_list in cuisines.items():
        print(f"  • {cuisine}: {len(rest_list)} restaurants")
    
    # Show sample restaurants
    print("\nSample restaurants:")
    for restaurant in restaurants[:5]:
        print(f"  🍽️  {restaurant.name} ({restaurant.cuisine})")
        print(f"     📍 {restaurant.location} • ⭐ {restaurant.rating}")
    
    # Test filtering
    print("\n🔍 Filtering examples:")
    chinese_ny = db.get_restaurants(location="New York", cuisine="Chinese")
    print(f"Chinese restaurants in New York: {len(chinese_ny)}")
    
    italian_restaurants = db.get_restaurants(cuisine="Italian")
    print(f"Italian restaurants: {len(italian_restaurants)}")

def main():
    """Main demonstration function"""
    print("🎯 Advanced Dialogue State Tracking - Project Demo")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("This demo showcases the complete functionality of the")
    print("Advanced Dialogue State Tracking system for restaurant booking.")
    
    try:
        # Run all demonstrations
        demo_conversation_flow()
        demo_intent_classification()
        demo_slot_extraction()
        demo_database_features()
        demo_api_capabilities()
        
        print_header("Demo Complete!")
        print("✅ All demonstrations completed successfully!")
        print()
        print("🚀 To run the full application:")
        print("   1. python setup.py  # Initial setup")
        print("   2. python api.py    # Start web server")
        print("   3. Open http://localhost:8000")
        print()
        print("🧪 To run tests:")
        print("   pytest test_dialogue_tracking.py -v")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        print("Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        print("python -m spacy download en_core_web_sm")

if __name__ == "__main__":
    main()
