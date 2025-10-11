import json
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import spacy
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class DialogueState:
    """Represents the current state of a dialogue"""
    intent: Optional[str] = None
    slots: Dict[str, Any] = None
    confidence: float = 0.0
    turn_count: int = 0
    last_updated: str = ""
    
    def __post_init__(self):
        if self.slots is None:
            self.slots = {
                "location": None,
                "cuisine": None,
                "party_size": None,
                "reservation_time": None,
                "restaurant_name": None,
                "customer_name": None,
                "special_requests": None
            }
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

@dataclass
class DialogueTurn:
    """Represents a single turn in the dialogue"""
    user_input: str
    system_response: str
    extracted_slots: Dict[str, Any]
    intent: str
    confidence: float
    timestamp: str

class AdvancedDialogueStateTracker:
    """Advanced dialogue state tracker using modern ML techniques"""
    
    def __init__(self):
        self.state = DialogueState()
        self.dialogue_history: List[DialogueTurn] = []
        
        # Initialize NLP models
        self._init_nlp_models()
        
        # Intent classification patterns
        self.intent_patterns = {
            "book_table": [
                "book", "reserve", "table", "reservation", "dinner", "lunch",
                "make a reservation", "get a table", "book a table"
            ],
            "find_restaurant": [
                "find", "search", "look for", "recommend", "suggest",
                "where can I", "what restaurants", "show me"
            ],
            "modify_reservation": [
                "change", "modify", "update", "reschedule", "move",
                "different time", "different date"
            ],
            "cancel_reservation": [
                "cancel", "remove", "delete", "no longer need"
            ],
            "get_info": [
                "info", "information", "details", "tell me about",
                "what is", "how much", "price", "menu"
            ]
        }
        
        # Slot extraction patterns
        self.slot_patterns = {
            "location": [
                r"\b(?:in|at|near|around)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:area|district|neighborhood)"
            ],
            "cuisine": [
                r"\b(chinese|italian|japanese|indian|french|mexican|thai|korean|vietnamese|greek|mediterranean|american|bbq|barbecue)\b",
                r"\b(?:chinese|italian|japanese|indian|french|mexican|thai|korean|vietnamese|greek|mediterranean|american|bbq|barbecue)\s+(?:food|cuisine|restaurant)"
            ],
            "party_size": [
                r"\b(\d+)\s+(?:people|persons|guests|diners)",
                r"\b(?:party of|table for|group of)\s+(\d+)",
                r"\b(\d+)\s+(?:of us|people|guests)"
            ],
            "reservation_time": [
                r"\b(?:at|for|around)\s+(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?)",
                r"\b(?:at|for|around)\s+(\d{1,2}\s*(?:am|pm|AM|PM))",
                r"\b(?:tonight|tomorrow|today)\s+(?:at|for)\s+(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?)",
                r"\b(\d{1,2}:\d{2}\s*(?:am|pm|AM|PM))\s+(?:tonight|tomorrow|today)"
            ],
            "restaurant_name": [
                r"\b(?:at|restaurant called|named)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:restaurant|place)"
            ],
            "customer_name": [
                r"\b(?:my name is|i'm|i am|call me)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
                r"\b(name|reservation)\s+(?:for|under)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
            ]
        }
    
    def _init_nlp_models(self):
        """Initialize NLP models"""
        try:
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        
        # Initialize intent classification model (using a lightweight model)
        try:
            self.intent_classifier = pipeline(
                "text-classification",
                model="microsoft/DialoGPT-medium",
                return_all_scores=True
            )
        except Exception:
            print("Warning: Could not load transformer model. Using rule-based approach.")
            self.intent_classifier = None
    
    def extract_intent(self, text: str) -> Tuple[str, float]:
        """Extract intent from user input using ML and rule-based approaches"""
        text_lower = text.lower()
        
        # Rule-based intent classification
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text_lower:
                    score += 1
            intent_scores[intent] = score / len(patterns)
        
        # Find best intent
        best_intent = max(intent_scores, key=intent_scores.get)
        confidence = intent_scores[best_intent]
        
        # If confidence is low, try ML-based approach
        if confidence < 0.3 and self.intent_classifier:
            try:
                ml_results = self.intent_classifier(text)
                # This is a simplified approach - in practice you'd train a custom model
                pass
            except Exception:
                pass
        
        return best_intent, confidence
    
    def extract_slots(self, text: str) -> Dict[str, Any]:
        """Extract slots from user input using multiple techniques"""
        slots = {}
        
        # Pattern-based extraction
        for slot_name, patterns in self.slot_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    slots[slot_name] = matches[0]
                    break
        
        # NER-based extraction using spaCy
        if self.nlp:
            doc = self.nlp(text)
            
            # Extract locations
            for ent in doc.ents:
                if ent.label_ in ["GPE", "LOC"] and not slots.get("location"):
                    slots["location"] = ent.text
            
            # Extract time expressions
            for ent in doc.ents:
                if ent.label_ in ["TIME", "DATE"] and not slots.get("reservation_time"):
                    slots["reservation_time"] = ent.text
            
            # Extract cardinal numbers for party size
            for ent in doc.ents:
                if ent.label_ == "CARDINAL" and not slots.get("party_size"):
                    try:
                        num = int(ent.text)
                        if 1 <= num <= 20:  # Reasonable party size
                            slots["party_size"] = num
                    except ValueError:
                        pass
        
        # Additional heuristics
        self._apply_heuristics(text, slots)
        
        return slots
    
    def _apply_heuristics(self, text: str, slots: Dict[str, Any]):
        """Apply additional heuristics for slot extraction"""
        text_lower = text.lower()
        
        # Extract party size from common phrases
        if not slots.get("party_size"):
            party_patterns = [
                r"\b(?:just|only)\s+(\d+)\s+(?:of us|people)",
                r"\b(\d+)\s+(?:people|guests|diners)",
                r"\b(?:table for|party of)\s+(\d+)"
            ]
            for pattern in party_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    slots["party_size"] = int(match.group(1))
                    break
        
        # Extract time from common phrases
        if not slots.get("reservation_time"):
            time_patterns = [
                r"\b(?:at|around|for)\s+(\d{1,2}:\d{2})\s*(?:pm|am)?",
                r"\b(\d{1,2}:\d{2})\s*(?:pm|am)?\s*(?:tonight|tomorrow|today)",
                r"\b(?:tonight|tomorrow|today)\s+(?:at|around|for)\s+(\d{1,2}:\d{2})"
            ]
            for pattern in time_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    slots["reservation_time"] = match.group(1)
                    break
    
    def update_state(self, user_input: str) -> DialogueState:
        """Update dialogue state based on user input"""
        # Extract intent and slots
        intent, intent_confidence = self.extract_intent(user_input)
        extracted_slots = self.extract_slots(user_input)
        
        # Update state
        self.state.intent = intent
        self.state.confidence = intent_confidence
        self.state.turn_count += 1
        self.state.last_updated = datetime.now().isoformat()
        
        # Update slots (only update non-None values)
        for slot_name, slot_value in extracted_slots.items():
            if slot_value is not None:
                self.state.slots[slot_name] = slot_value
        
        # Create dialogue turn
        turn = DialogueTurn(
            user_input=user_input,
            system_response="",  # Will be filled by the system
            extracted_slots=extracted_slots,
            intent=intent,
            confidence=intent_confidence,
            timestamp=datetime.now().isoformat()
        )
        
        self.dialogue_history.append(turn)
        
        return self.state
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current dialogue state"""
        return {
            "intent": self.state.intent,
            "confidence": self.state.confidence,
            "slots": {k: v for k, v in self.state.slots.items() if v is not None},
            "turn_count": self.state.turn_count,
            "last_updated": self.state.last_updated,
            "dialogue_length": len(self.dialogue_history)
        }
    
    def reset_state(self):
        """Reset the dialogue state"""
        self.state = DialogueState()
        self.dialogue_history = []
    
    def get_missing_slots(self) -> List[str]:
        """Get list of slots that still need to be filled"""
        required_slots = ["location", "cuisine", "party_size", "reservation_time"]
        return [slot for slot in required_slots if not self.state.slots.get(slot)]
    
    def is_booking_complete(self) -> bool:
        """Check if all required slots for booking are filled"""
        required_slots = ["location", "cuisine", "party_size", "reservation_time"]
        return all(self.state.slots.get(slot) for slot in required_slots)

# Initialize the dialogue state tracker
dst = AdvancedDialogueStateTracker()
