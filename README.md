# Dialogue State Tracking

An implementation of dialogue state tracking for restaurant booking systems, featuring advanced NLP techniques, ML-based intent recognition, and real-time conversation management.

## Features

- **Advanced ML-based Intent Classification**: Uses transformer models and rule-based patterns for accurate intent recognition
- **Multi-modal Slot Extraction**: Combines NER, regex patterns, and heuristics for robust slot filling
- **Real-time Dialogue State Tracking**: Maintains conversation context across multiple turns
- **RESTful API**: Modern FastAPI-based web service with comprehensive endpoints
- **Interactive Web Interface**: Beautiful, responsive chat interface for testing
- **Mock Database**: Complete restaurant and booking data for realistic testing
- **Comprehensive Testing**: Full test suite with unit and integration tests
- **Modern Architecture**: Clean, modular code with type hints and documentation

## Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kryptologyst/Dialogue-State-Tracking.git
   cd Dialogue-State-Tracking
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

4. **Run the demo**
   ```bash
   python 0182.py
   ```

5. **Start the web application**
   ```bash
   python api.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8000` to use the interactive chat interface.

## 📁 Project Structure

```
dialogue-state-tracking/
├── 0182.py                 # Main demo script
├── api.py                  # FastAPI web application
├── dialogue_tracker.py     # Advanced dialogue state tracker
├── database.py             # Mock database implementation
├── test_dialogue_tracking.py # Comprehensive test suite
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── mock_restaurant.db     # SQLite database (created automatically)
```

## 🔧 Components

### AdvancedDialogueStateTracker

The core component that handles dialogue state management:

- **Intent Classification**: Identifies user intents using ML models and pattern matching
- **Slot Extraction**: Extracts structured information from natural language
- **State Management**: Maintains conversation context across turns
- **Confidence Scoring**: Provides confidence metrics for decisions

### MockDatabase

A realistic restaurant booking database:

- **Restaurant Data**: 10+ sample restaurants with ratings, cuisine types, and locations
- **Reservation Management**: Create, query, and manage reservations
- **Availability Checking**: Real-time availability validation
- **SQLite Backend**: Lightweight, file-based database

### FastAPI Web Service

Modern RESTful API with:

- **Chat Endpoint**: Real-time dialogue interaction
- **Restaurant Search**: Filter restaurants by location and cuisine
- **Booking Management**: Create and manage reservations
- **Health Monitoring**: System health and status endpoints

## Usage Examples

### Basic Dialogue Tracking

```python
from dialogue_tracker import AdvancedDialogueStateTracker

tracker = AdvancedDialogueStateTracker()

# Process user input
state = tracker.update_state("I want to book a table in New York")

print(f"Intent: {state.intent}")
print(f"Location: {state.slots['location']}")
```

### API Usage

```python
import requests

# Chat with the system
response = requests.post("http://localhost:8000/chat", json={
    "message": "I want to book a table",
    "session_id": "user123"
})

data = response.json()
print(data["response"])
print(data["state"])
```

### Restaurant Search

```python
from database import MockDatabase

db = MockDatabase()

# Find Chinese restaurants in New York
restaurants = db.get_restaurants(location="New York", cuisine="Chinese")
for restaurant in restaurants:
    print(f"{restaurant.name} - {restaurant.rating} stars")
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest test_dialogue_tracking.py -v

# Run specific test categories
pytest test_dialogue_tracking.py::TestDialogueStateTracker -v
pytest test_dialogue_tracking.py::TestAPI -v
pytest test_dialogue_tracking.py::TestIntegration -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Interactive web interface |
| `POST` | `/chat` | Chat with the dialogue system |
| `GET` | `/restaurants` | Get restaurant listings |
| `POST` | `/book` | Make a reservation |
| `GET` | `/health` | Health check |

### Chat API Example

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "I want to book a table", "session_id": "test"}'
```

## Supported Intents

- **book_table**: Make a restaurant reservation
- **find_restaurant**: Search for restaurants
- **modify_reservation**: Change existing reservation
- **cancel_reservation**: Cancel a reservation
- **get_info**: Get restaurant information

## Supported Slots

- **location**: Restaurant location (e.g., "New York", "Los Angeles")
- **cuisine**: Type of cuisine (e.g., "Chinese", "Italian", "Japanese")
- **party_size**: Number of people (e.g., 2, 4, 6)
- **reservation_time**: Preferred time (e.g., "7 PM", "8:30 PM")
- **restaurant_name**: Specific restaurant name
- **customer_name**: Customer's name
- **special_requests**: Special requirements

## 🛠️ Advanced Features

### ML-Based Intent Classification

The system uses transformer models for intent classification:

```python
# Uses microsoft/DialoGPT-medium for intent classification
intent_classifier = pipeline(
    "text-classification",
    model="microsoft/DialoGPT-medium"
)
```

### Multi-Modal Slot Extraction

Combines multiple techniques for robust slot extraction:

1. **Named Entity Recognition** (spaCy)
2. **Regex Pattern Matching**
3. **Heuristic Rules**
4. **Context-Aware Processing**

### Session Management

Maintains separate dialogue states for multiple users:

```python
# Each session has its own dialogue state
sessions = {
    "user123": AdvancedDialogueStateTracker(),
    "user456": AdvancedDialogueStateTracker()
}
```

## Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Run the application
python api.py
```

### Production Deployment

For production deployment, consider:

1. **Database**: Replace SQLite with PostgreSQL/MySQL
2. **Session Storage**: Use Redis for session management
3. **Model Caching**: Cache ML models for better performance
4. **Load Balancing**: Use multiple API instances
5. **Monitoring**: Add logging and metrics collection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **spaCy**: For excellent NLP capabilities
- **Transformers**: For state-of-the-art ML models
- **FastAPI**: For modern web API framework
- **SQLite**: For lightweight database functionality

## Support

For questions, issues, or contributions:

- Open an issue on GitHub
- Check the documentation
- Review the test cases for usage examples

 
# Dialogue-State-Tracking
