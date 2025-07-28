import pandas as pd
import numpy as np
from utils.data_loader import DataLoader

def create_track_dominance_map(year, grand_prix, session):
    """Create track dominance analysis"""
    try:
        data_loader = DataLoader()
        session_data = data_loader.load_session_data(year, grand_prix, session)
        
        if session_data is None:
            return None
        
        dominance_data = {
            'sector_dominance': {},
            'speed_dominance': {},
            'overall_dominance': {},
            'track_segments': []
        }
        
        # Analyze sector performance
        for driver in session_data.drivers:
            try:
                driver_laps = session_data.laps.pick_driver(driver)
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()
                    
                    # Sector times
                    dominance_data['sector_dominance'][driver] = {
                        'sector_1': float(fastest_lap['Sector1Time'].total_seconds()) if pd.notna(fastest_lap['Sector1Time']) else None,
                        'sector_2': float(fastest_lap['Sector2Time'].total_seconds()) if pd.notna(fastest_lap['Sector2Time']) else None,
                        'sector_3': float(fastest_lap['Sector3Time'].total_seconds()) if pd.notna(fastest_lap['Sector3Time']) else None,
                        'lap_time': float(fastest_lap['LapTime'].total_seconds()) if pd.notna(fastest_lap['LapTime']) else None
                    }
                    
                    # Speed analysis
                    telemetry = fastest_lap.get_telemetry()
                    if not telemetry.empty:
                        dominance_data['speed_dominance'][driver] = {
                            'max_speed': float(telemetry['Speed'].max()) if not telemetry['Speed'].empty else None,
                            'avg_speed': float(telemetry['Speed'].mean()) if not telemetry['Speed'].empty else None,
                            'speed_segments': analyze_speed_segments(telemetry)
                        }
            except Exception as e:
                continue
        
        # Calculate overall dominance
        dominance_data['overall_dominance'] = calculate_overall_dominance(dominance_data)
        
        return dominance_data
        
    except Exception as e:
        return None

def analyze_speed_segments(telemetry):
    """Analyze speed in different track segments"""
    try:
        if telemetry.empty:
            return {}
        
        total_distance = telemetry['Distance'].max()
        segment_length = total_distance / 10  # Divide track into 10 segments
        
        segments = {}
        for i in range(10):
            start_dist = i * segment_length
            end_dist = (i + 1) * segment_length
            
            segment_data = telemetry[
                (telemetry['Distance'] >= start_dist) & 
                (telemetry['Distance'] < end_dist)
            ]
            
            if not segment_data.empty:
                segments[f'segment_{i+1}'] = {
                    'avg_speed': float(segment_data['Speed'].mean()),
                    'max_speed': float(segment_data['Speed'].max()),
                    'min_speed': float(segment_data['Speed'].min())
                }
        
        return segments
        
    except Exception as e:
        return {}

def calculate_overall_dominance(dominance_data):
    """Calculate overall track dominance rankings"""
    try:
        overall_scores = {}
        
        # Sector dominance scoring
        for sector in ['sector_1', 'sector_2', 'sector_3']:
            sector_times = {}
            for driver, data in dominance_data['sector_dominance'].items():
                if data[sector] is not None:
                    sector_times[driver] = data[sector]
            
            if sector_times:
                sorted_drivers = sorted(sector_times.items(), key=lambda x: x[1])
                for rank, (driver, time) in enumerate(sorted_drivers):
                    if driver not in overall_scores:
                        overall_scores[driver] = 0
                    overall_scores[driver] += (len(sorted_drivers) - rank)
        
        # Speed dominance scoring
        for driver, data in dominance_data['speed_dominance'].items():
            if data['max_speed'] is not None:
                if driver not in overall_scores:
                    overall_scores[driver] = 0
                # Add bonus points for high speeds
                overall_scores[driver] += data['max_speed'] / 10
        
        # Normalize and rank
        if overall_scores:
            max_score = max(overall_scores.values())
            normalized_scores = {
                driver: (score / max_score) * 100 
                for driver, score in overall_scores.items()
            }
            
            return dict(sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True))
        
        return {}
        
    except Exception as e:
        return {}
