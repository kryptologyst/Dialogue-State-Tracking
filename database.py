import os
import json
import sqlite3
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import random
from pathlib import Path

@dataclass
class Restaurant:
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

@dataclass
class Reservation:
    id: int
    restaurant_id: int
    customer_name: str
    party_size: int
    reservation_time: str
    status: str
    created_at: str

class MockDatabase:
    def __init__(self, db_path: str = "mock_restaurant.db"):
        self.db_path = db_path
        self.init_database()
        self.populate_sample_data()
    
    def init_database(self):
        """Initialize the SQLite database with tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create restaurants table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS restaurants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                location TEXT NOT NULL,
                cuisine TEXT NOT NULL,
                rating REAL NOT NULL,
                price_range TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                phone TEXT NOT NULL,
                address TEXT NOT NULL,
                description TEXT NOT NULL
            )
        ''')
        
        # Create reservations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                restaurant_id INTEGER NOT NULL,
                customer_name TEXT NOT NULL,
                party_size INTEGER NOT NULL,
                reservation_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY (restaurant_id) REFERENCES restaurants (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def populate_sample_data(self):
        """Populate database with sample restaurant data"""
        restaurants = [
            Restaurant(1, "Golden Dragon", "New York", "Chinese", 4.5, "$$", 50, "555-0101", "123 Chinatown St", "Authentic Chinese cuisine with dim sum"),
            Restaurant(2, "Mario's Italian", "New York", "Italian", 4.3, "$$$", 40, "555-0102", "456 Little Italy Ave", "Traditional Italian pasta and pizza"),
            Restaurant(3, "Tokyo Sushi", "New York", "Japanese", 4.7, "$$$", 30, "555-0103", "789 East Village St", "Fresh sushi and sashimi"),
            Restaurant(4, "Spice Palace", "New York", "Indian", 4.4, "$$", 45, "555-0104", "321 Curry Lane", "Spicy Indian curries and tandoor"),
            Restaurant(5, "Le Bistro", "New York", "French", 4.6, "$$$$", 25, "555-0105", "654 French Quarter", "Elegant French fine dining"),
            Restaurant(6, "Taco Libre", "Los Angeles", "Mexican", 4.2, "$", 60, "555-0201", "987 Sunset Blvd", "Authentic Mexican street food"),
            Restaurant(7, "Mediterranean Garden", "Los Angeles", "Mediterranean", 4.3, "$$", 35, "555-0202", "147 Olive Grove", "Fresh Mediterranean flavors"),
            Restaurant(8, "BBQ Pit", "Austin", "American", 4.5, "$$", 80, "555-0301", "258 Smoke St", "Texas-style barbecue"),
            Restaurant(9, "Pho Saigon", "San Francisco", "Vietnamese", 4.4, "$", 40, "555-0401", "369 Market St", "Traditional Vietnamese pho"),
            Restaurant(10, "Greek Taverna", "Chicago", "Greek", 4.1, "$$", 50, "555-0501", "741 Greektown Ave", "Authentic Greek cuisine")
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM restaurants")
        
        # Insert sample restaurants
        for restaurant in restaurants:
            cursor.execute('''
                INSERT INTO restaurants (id, name, location, cuisine, rating, price_range, capacity, phone, address, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                restaurant.id, restaurant.name, restaurant.location, restaurant.cuisine,
                restaurant.rating, restaurant.price_range, restaurant.capacity,
                restaurant.phone, restaurant.address, restaurant.description
            ))
        
        conn.commit()
        conn.close()
    
    def get_restaurants(self, location: Optional[str] = None, cuisine: Optional[str] = None) -> List[Restaurant]:
        """Get restaurants with optional filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM restaurants WHERE 1=1"
        params = []
        
        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")
        
        if cuisine:
            query += " AND cuisine LIKE ?"
            params.append(f"%{cuisine}%")
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        return [Restaurant(*row) for row in rows]
    
    def get_restaurant_by_id(self, restaurant_id: int) -> Optional[Restaurant]:
        """Get a specific restaurant by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM restaurants WHERE id = ?", (restaurant_id,))
        row = cursor.fetchone()
        conn.close()
        
        return Restaurant(*row) if row else None
    
    def create_reservation(self, restaurant_id: int, customer_name: str, party_size: int, reservation_time: str) -> int:
        """Create a new reservation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reservations (restaurant_id, customer_name, party_size, reservation_time, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (restaurant_id, customer_name, party_size, reservation_time, datetime.now().isoformat()))
        
        reservation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return reservation_id
    
    def get_reservations(self, restaurant_id: Optional[int] = None) -> List[Reservation]:
        """Get reservations with optional restaurant filter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if restaurant_id:
            cursor.execute("SELECT * FROM reservations WHERE restaurant_id = ?", (restaurant_id,))
        else:
            cursor.execute("SELECT * FROM reservations")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [Reservation(*row) for row in rows]
    
    def check_availability(self, restaurant_id: int, party_size: int, reservation_time: str) -> bool:
        """Check if a restaurant can accommodate a party at a specific time"""
        restaurant = self.get_restaurant_by_id(restaurant_id)
        if not restaurant:
            return False
        
        # Check capacity
        if party_size > restaurant.capacity:
            return False
        
        # Check existing reservations (simplified - in real app would check time conflicts)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) FROM reservations 
            WHERE restaurant_id = ? AND reservation_time = ? AND status != 'cancelled'
        ''', (restaurant_id, reservation_time))
        
        existing_count = cursor.fetchone()[0]
        conn.close()
        
        # Simple availability check (max 80% capacity for reservations)
        max_reservations = int(restaurant.capacity * 0.8)
        return existing_count < max_reservations

# Initialize the mock database
db = MockDatabase()
