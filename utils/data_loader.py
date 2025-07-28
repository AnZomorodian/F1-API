import fastf1
import pandas as pd
import numpy as np
import logging
import os
import tempfile
from datetime import datetime

class DataLoader:
    """Handles F1 data loading using FastF1"""
    
    def __init__(self):
        # Configure FastF1 cache
        cache_dir = os.path.join(tempfile.gettempdir(), 'fastf1_cache')
        os.makedirs(cache_dir, exist_ok=True)
        fastf1.Cache.enable_cache(cache_dir)
        
        # Suppress FastF1 warnings
        fastf1.set_log_level('WARNING')
        
        logging.info(f"FastF1 cache configured at: {cache_dir}")
    
    def load_session_data(self, year, grand_prix, session):
        """Load session data from FastF1"""
        try:
            logging.info(f"Loading session data: {year} {grand_prix} {session}")
            
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            logging.info(f"Successfully loaded session data for {year} {grand_prix} {session}")
            return session_obj
            
        except Exception as e:
            logging.error(f"Error loading session data: {str(e)}")
            return None
    
    def get_available_drivers(self, session_data):
        """Get available drivers from session data"""
        try:
            if hasattr(session_data, 'drivers'):
                return session_data.drivers.tolist()
            return []
        except Exception as e:
            logging.error(f"Error getting drivers: {str(e)}")
            return []
    
    def get_driver_laps(self, session_data, driver):
        """Get laps for a specific driver"""
        try:
            return session_data.laps.pick_driver(driver)
        except Exception as e:
            logging.error(f"Error getting driver laps: {str(e)}")
            return None
    
    def get_fastest_lap(self, driver_laps):
        """Get fastest lap from driver laps"""
        try:
            return driver_laps.pick_fastest()
        except Exception as e:
            logging.error(f"Error getting fastest lap: {str(e)}")
            return None
    
    def get_telemetry_data(self, lap):
        """Get telemetry data for a specific lap"""
        try:
            return lap.get_telemetry()
        except Exception as e:
            logging.error(f"Error getting telemetry data: {str(e)}")
            return None
    
    def get_car_data(self, lap):
        """Get car data for a specific lap"""
        try:
            return lap.get_car_data()
        except Exception as e:
            logging.error(f"Error getting car data: {str(e)}")
            return None
    
    def get_weather_data(self, session_data):
        """Get weather data from session"""
        try:
            return session_data.weather_data
        except Exception as e:
            logging.error(f"Error getting weather data: {str(e)}")
            return None
    
    def get_session_results(self, session_data):
        """Get session results"""
        try:
            return session_data.results
        except Exception as e:
            logging.error(f"Error getting session results: {str(e)}")
            return None
