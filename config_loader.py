#!/usr/bin/env python3
"""
Configuration Loader for Hotel Simulator
Loads simulation parameters from hotel_sim.toml file
"""

import toml
from typing import Dict, Any, Optional
from dataclasses import dataclass
import os


@dataclass
class SimulationConfig:
    """Simulation configuration from TOML file"""
    min_occupancy_percent: float
    max_occupancy_percent: float
    cancellation_rate: float
    cancellation_probability: float
    walk_in_probability: float
    group_booking_probability: float
    loyalty_member_probability: float
    extended_stay_probability: float
    special_request_probability: float
    new_reservation_probability: float
    check_in_probability: float
    check_out_probability: float
    average_stay_days_min: int
    average_stay_days_max: int
    seasonal_price_variation: float
    weekend_price_multiplier: float
    loyalty_discount: float
    room_types: list
    total_rooms: int
    total_floors: int
    room_distribution: str
    guest_name_count: int
    international_guest_percentage: float
    revenue_goal_daily: float
    tax_rate: float
    service_fee: float


class ConfigLoader:
    """Load and manage simulation configuration"""
    
    def __init__(self, config_path: str = 'hotel_sim.toml'):
        """Initialize configuration loader"""
        self.config_path = config_path
        self.config = None
        self.simulation_config = None
        
    def load_config(self) -> SimulationConfig:
        """Load configuration from TOML file"""
        try:
            # Check if config file exists
            if not os.path.exists(self.config_path):
                print(f"⚠️  Config file not found: {self.config_path}")
                print("Using default configuration")
                return self._create_default_config()
            
            # Load TOML file
            with open(self.config_path, 'r') as f:
                self.config = toml.load(f)
            
            # Parse configuration
            self.simulation_config = self._parse_config()
            return self.simulation_config
            
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            print("Using default configuration")
            return self._create_default_config()
    
    def _parse_config(self) -> SimulationConfig:
        """Parse loaded TOML config into SimulationConfig object"""
        sim = self.config.get('simulation', {})
        hotel = self.config.get('hotel', {})
        guest = self.config.get('guest', {})
        financial = self.config.get('financial', {})
        
        return SimulationConfig(
            min_occupancy_percent=sim.get('min_occupancy_percent', 60.0),
            max_occupancy_percent=sim.get('max_occupancy_percent', 90.0),
            cancellation_rate=sim.get('cancellation_rate', 0.05),
            cancellation_probability=sim.get('cancellation_probability', 0.08),
            walk_in_probability=sim.get('walk_in_probability', 0.2),
            group_booking_probability=sim.get('group_booking_probability', 0.15),
            loyalty_member_probability=sim.get('loyalty_member_probability', 0.3),
            extended_stay_probability=sim.get('extended_stay_probability', 0.2),
            special_request_probability=sim.get('special_request_probability', 0.25),
            new_reservation_probability=sim.get('new_reservation_probability', 0.5),
            check_in_probability=sim.get('check_in_probability', 0.6),
            check_out_probability=sim.get('check_out_probability', 0.5),
            average_stay_days_min=sim.get('average_stay_days_min', 1),
            average_stay_days_max=sim.get('average_stay_days_max', 7),
            seasonal_price_variation=sim.get('seasonal_price_variation', 0.2),
            weekend_price_multiplier=sim.get('weekend_price_multiplier', 1.15),
            loyalty_discount=sim.get('loyalty_discount', 0.1),
            room_types=sim.get('room_types', [
                {"name": "Standard", "base_price": 120.00, "weight": 0.5},
                {"name": "Deluxe", "base_price": 180.00, "weight": 0.3},
                {"name": "Suite", "base_price": 300.00, "weight": 0.2}
            ]),
            total_rooms=hotel.get('total_rooms', 100),
            total_floors=hotel.get('total_floors', 5),
            room_distribution=hotel.get('room_distribution', 'balanced'),
            guest_name_count=guest.get('guest_name_count', 50),
            international_guest_percentage=guest.get('international_guest_percentage', 0.2),
            revenue_goal_daily=financial.get('revenue_goal_daily', 10000.00),
            tax_rate=financial.get('tax_rate', 0.10),
            service_fee=financial.get('service_fee', 0.05)
        )
    
    def _create_default_config(self) -> SimulationConfig:
        """Create default configuration if TOML file is missing"""
        return SimulationConfig(
            min_occupancy_percent=60.0,
            max_occupancy_percent=90.0,
            cancellation_rate=0.05,
            cancellation_probability=0.08,
            walk_in_probability=0.2,
            group_booking_probability=0.15,
            loyalty_member_probability=0.3,
            extended_stay_probability=0.2,
            special_request_probability=0.25,
            new_reservation_probability=0.5,
            check_in_probability=0.6,
            check_out_probability=0.5,
            average_stay_days_min=1,
            average_stay_days_max=7,
            seasonal_price_variation=0.2,
            weekend_price_multiplier=1.15,
            loyalty_discount=0.1,
            room_types=[
                {"name": "Standard", "base_price": 120.00, "weight": 0.5},
                {"name": "Deluxe", "base_price": 180.00, "weight": 0.3},
                {"name": "Suite", "base_price": 300.00, "weight": 0.2}
            ],
            total_rooms=100,
            total_floors=5,
            room_distribution='balanced',
            guest_name_count=50,
            international_guest_percentage=0.2,
            revenue_goal_daily=10000.00,
            tax_rate=0.10,
            service_fee=0.05
        )
    
    def get_config(self) -> SimulationConfig:
        """Get current configuration (load if not loaded)"""
        if self.simulation_config is None:
            return self.load_config()
        return self.simulation_config


def load_simulation_config() -> SimulationConfig:
    """Convenience function to load configuration"""
    loader = ConfigLoader()
    return loader.load_config()


if __name__ == "__main__":
    # Test the configuration loader
    config = load_simulation_config()
    print("✅ Configuration loaded successfully!")
    print(f"Occupancy range: {config.min_occupancy_percent}% - {config.max_occupancy_percent}%")
    print(f"Cancellation rate: {config.cancellation_rate * 100}%")
    print(f"Room types: {len(config.room_types)}")