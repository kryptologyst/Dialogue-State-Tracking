#!/usr/bin/env python3
"""
Project 182: Advanced Dialogue State Tracking
============================================

A modern implementation of dialogue state tracking for restaurant booking systems.
This project demonstrates advanced NLP techniques, ML-based intent recognition,
and real-time dialogue state management.

Features:
- Advanced ML-based intent classification
- Multi-modal slot extraction (NER + patterns + heuristics)
- Real-time dialogue state tracking
- RESTful API with FastAPI
- Modern web interface
- Comprehensive testing suite
- Mock database integration

Author: AI Assistant
Date: 2024
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import our modern components
from dialogue_tracker import AdvancedDialogueStateTracker
from database import MockDatabase
from api import app

def demo_basic_dialogue_tracking():
    """Demonstrate basic dialogue state tracking functionality"""
    print("🍽️ Advanced Dialogue State Tracking Demo")
    print("=" * 50)
    
    # Initialize components
    tracker = AdvancedDialogueStateTracker()
    db = MockDatabase()
    
    # Sample conversation turns
    conversation_turns = [
        "Hi, I'd like to book a table.",
        "It should be in New York.",
        "We want Chinese food.",
        "There are four of us.",
        "Make it for 7 pm tonight."
    ]
    
    print("\n📝 Processing conversation turns:")
    print("-" * 30)
    
    for i, turn in enumerate(conversation_turns, 1):
        print(f"\nTurn {i}: {turn}")
        
        # Update dialogue state
        state = tracker.update_state(turn)
        
        # Display current state
        print(f"Intent: {state.intent} (confidence: {state.confidence:.2f})")
        print("Slots:")
        for slot, value in state.slots.items():
            if value:
                print(f"  ✓ {slot}: {value}")
        
        # Check if booking is complete
        if tracker.is_booking_complete():
            print("🎉 Booking information complete!")
            break
    
    # Display final state summary
    print("\n🧠 Final Dialogue State Summary:")
    print("-" * 35)
    summary = tracker.get_state_summary()
    print(json.dumps(summary, indent=2))
    
    # Find matching restaurants
    print("\n🔍 Finding matching restaurants:")
    print("-" * 32)
    restaurants = db.get_restaurants(
        location=state.slots.get("location"),
        cuisine=state.slots.get("cuisine")
    )
    
    if restaurants:
        print(f"Found {len(restaurants)} restaurants:")
        for restaurant in restaurants[:3]:  # Show top 3
            print(f"  • {restaurant.name} - {restaurant.cuisine} ({restaurant.location})")
            print(f"    ⭐ {restaurant.rating} • {restaurant.price_range} • Capacity: {restaurant.capacity}")
    else:
        print("No restaurants found matching the criteria.")

def demo_advanced_features():
    """Demonstrate advanced features"""
    print("\n\n🚀 Advanced Features Demo")
    print("=" * 30)
    
    tracker = AdvancedDialogueStateTracker()
    
    # Test various intents and slot extractions
    test_cases = [
        "Find me Italian restaurants in Los Angeles",
        "I want to cancel my reservation",
        "What's the menu at Mario's Italian?",
        "Change my reservation to 8 PM",
        "Book a table for 6 people at Tokyo Sushi for 7:30 PM"
    ]
    
    for test_input in test_cases:
        print(f"\nInput: {test_input}")
        state = tracker.update_state(test_input)
        
        print(f"Intent: {state.intent}")
        print(f"Confidence: {state.confidence:.2f}")
        
        filled_slots = {k: v for k, v in state.slots.items() if v is not None}
        if filled_slots:
            print(f"Extracted slots: {filled_slots}")
        else:
            print("No slots extracted")
        
        tracker.reset_state()  # Reset for next test

async def demo_api_features():
    """Demonstrate API features"""
    print("\n\n🌐 API Features Demo")
    print("=" * 20)
    
    # This would normally require running the server
    print("To test the API features:")
    print("1. Run: python api.py")
    print("2. Open: http://localhost:8000")
    print("3. Use the web interface or API endpoints:")
    print("   - POST /chat - Chat with the system")
    print("   - GET /restaurants - Get restaurant listings")
    print("   - POST /book - Make a reservation")
    print("   - GET /health - Health check")

def main():
    """Main demo function"""
    print("🎯 Project 182: Advanced Dialogue State Tracking")
    print("=" * 55)
    print("This demo showcases modern dialogue state tracking techniques")
    print("including ML-based intent recognition, advanced slot extraction,")
    print("and real-time conversation management.\n")
    
    try:
        # Run basic demo
        demo_basic_dialogue_tracking()
        
        # Run advanced features demo
        demo_advanced_features()
        
        # Show API info
        asyncio.run(demo_api_features())
        
        print("\n\n✅ Demo completed successfully!")
        print("\nTo run the full web application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Download spaCy model: python -m spacy download en_core_web_sm")
        print("3. Run the API: python api.py")
        print("4. Open browser: http://localhost:8000")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        print("Make sure all dependencies are installed and spaCy model is downloaded.")

if __name__ == "__main__":
    main()