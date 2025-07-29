"""
Advanced Performance Analysis Module
Comprehensive F1 performance metrics and analytics
"""

import fastf1
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import scipy.stats as stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

class AdvancedPerformanceAnalyzer:
    """Advanced performance analysis and metrics for F1 data"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze_overtaking_opportunities(self, year: int, grand_prix: str) -> Dict[str, Any]:
        """Analyze overtaking opportunities and success rates"""
        try:
            race_session = fastf1.get_session(year, grand_prix, 'Race')
            race_session.load()
            
            overtaking_data = {
                'total_overtakes': 0,
                'overtaking_zones': {},
                'driver_overtakes': {},
                'drs_effectiveness': {}
            }
            
            if hasattr(race_session, 'laps') and not race_session.laps.empty:
                laps = race_session.laps
                
                # Analyze position changes between laps
                for driver in race_session.drivers:
                    try:
                        driver_laps = laps.pick_driver(driver)
                        if len(driver_laps) > 1:
                            position_changes = []
                            overtakes_made = 0
                            overtakes_lost = 0
                            
                            for i in range(1, len(driver_laps)):
                                prev_pos = driver_laps.iloc[i-1]['Position']
                                curr_pos = driver_laps.iloc[i]['Position']
                                
                                if pd.notna(prev_pos) and pd.notna(curr_pos):
                                    change = prev_pos - curr_pos  # Positive = gained positions
                                    if change > 0:
                                        overtakes_made += change
                                    elif change < 0:
                                        overtakes_lost += abs(change)
                                    
                                    position_changes.append(change)
                            
                            overtaking_data['driver_overtakes'][driver] = {
                                'overtakes_made': int(overtakes_made),
                                'overtakes_lost': int(overtakes_lost),
                                'net_overtakes': int(overtakes_made - overtakes_lost),
                                'position_volatility': float(np.std(position_changes)) if position_changes else 0
                            }
                            
                            overtaking_data['total_overtakes'] += overtakes_made
                    
                    except Exception as driver_error:
                        self.logger.warning(f"Error analyzing overtaking for {driver}: {str(driver_error)}")
                        continue
            
            return {
                'overtaking_analysis': overtaking_data,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing overtaking opportunities: {str(e)}")
            return {'error': str(e)}
    
    def analyze_cornering_performance(self, year: int, grand_prix: str, session: str, 
                                    driver: str) -> Dict[str, Any]:
        """Analyze cornering performance and techniques"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            driver_laps = session_obj.laps.pick_driver(driver)
            if driver_laps.empty:
                return {'error': f'No data found for driver {driver}'}
            
            fastest_lap = driver_laps.pick_fastest()
            if fastest_lap is None:
                return {'error': f'No fastest lap found for driver {driver}'}
            
            telemetry = fastest_lap.get_telemetry()
            
            # Identify cornering zones (low speed + high lateral G-force indicators)
            speed_threshold = telemetry['Speed'].quantile(0.3)  # Bottom 30% of speeds
            cornering_zones = telemetry[telemetry['Speed'] <= speed_threshold]
            
            cornering_analysis = {
                'corner_count': len(self._identify_corner_sequences(cornering_zones)),
                'avg_corner_speed': float(cornering_zones['Speed'].mean()) if not cornering_zones.empty else 0,
                'min_corner_speed': float(cornering_zones['Speed'].min()) if not cornering_zones.empty else 0,
                'corner_acceleration': [],
                'braking_zones': [],
                'throttle_application': []
            }
            
            # Analyze braking and acceleration patterns
            if not cornering_zones.empty:
                # Find braking zones (high brake values before corners)
                brake_zones = telemetry[telemetry['Brake'] > 0.5]
                cornering_analysis['braking_zones'] = self._analyze_braking_patterns(brake_zones, telemetry)
                
                # Analyze throttle application out of corners
                throttle_zones = telemetry[telemetry['Throttle'] > 0.5]
                cornering_analysis['throttle_application'] = self._analyze_throttle_patterns(throttle_zones, telemetry)
            
            return {
                'cornering_analysis': cornering_analysis,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session,
                    'driver': driver
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing cornering performance: {str(e)}")
            return {'error': str(e)}
    
    def _identify_corner_sequences(self, cornering_data: pd.DataFrame) -> List[Dict]:
        """Identify distinct corner sequences from telemetry data"""
        corners = []
        if cornering_data.empty:
            return corners
        
        # Group consecutive low-speed zones as corners
        distance_gaps = cornering_data['Distance'].diff()
        gap_threshold = 100  # 100m gap indicates separate corners
        
        corner_start = None
        for idx, gap in enumerate(distance_gaps):
            if pd.isna(gap) or gap <= gap_threshold:
                if corner_start is None:
                    corner_start = idx
            else:
                if corner_start is not None:
                    corner_data = cornering_data.iloc[corner_start:idx]
                    corners.append({
                        'start_distance': float(corner_data['Distance'].iloc[0]),
                        'end_distance': float(corner_data['Distance'].iloc[-1]),
                        'min_speed': float(corner_data['Speed'].min()),
                        'avg_speed': float(corner_data['Speed'].mean())
                    })
                    corner_start = None
        
        return corners
    
    def _analyze_braking_patterns(self, brake_zones: pd.DataFrame, full_telemetry: pd.DataFrame) -> Dict[str, Any]:
        """Analyze braking patterns and effectiveness"""
        if brake_zones.empty:
            return {}
        
        return {
            'total_braking_distance': float((brake_zones['Distance'].max() - brake_zones['Distance'].min())),
            'max_brake_pressure': float(brake_zones['Brake'].max()),
            'avg_brake_pressure': float(brake_zones['Brake'].mean()),
            'braking_zones_count': len(self._identify_braking_sequences(brake_zones))
        }
    
    def _analyze_throttle_patterns(self, throttle_zones: pd.DataFrame, full_telemetry: pd.DataFrame) -> Dict[str, Any]:
        """Analyze throttle application patterns"""
        if throttle_zones.empty:
            return {}
        
        return {
            'total_throttle_distance': float((throttle_zones['Distance'].max() - throttle_zones['Distance'].min())),
            'max_throttle': float(throttle_zones['Throttle'].max()),
            'avg_throttle': float(throttle_zones['Throttle'].mean()),
            'throttle_zones_count': len(self._identify_throttle_sequences(throttle_zones))
        }
    
    def _identify_braking_sequences(self, brake_data: pd.DataFrame) -> List[Dict]:
        """Identify distinct braking sequences"""
        sequences = []
        if brake_data.empty:
            return sequences
        
        # Similar logic to corner identification
        distance_gaps = brake_data['Distance'].diff()
        gap_threshold = 50  # 50m gap for braking zones
        
        seq_start = None
        for idx, gap in enumerate(distance_gaps):
            if pd.isna(gap) or gap <= gap_threshold:
                if seq_start is None:
                    seq_start = idx
            else:
                if seq_start is not None:
                    seq_data = brake_data.iloc[seq_start:idx]
                    sequences.append({
                        'start_distance': float(seq_data['Distance'].iloc[0]),
                        'end_distance': float(seq_data['Distance'].iloc[-1]),
                        'max_pressure': float(seq_data['Brake'].max())
                    })
                    seq_start = None
        
        return sequences
    
    def _identify_throttle_sequences(self, throttle_data: pd.DataFrame) -> List[Dict]:
        """Identify distinct throttle application sequences"""
        sequences = []
        if throttle_data.empty:
            return sequences
        
        distance_gaps = throttle_data['Distance'].diff()
        gap_threshold = 50
        
        seq_start = None
        for idx, gap in enumerate(distance_gaps):
            if pd.isna(gap) or gap <= gap_threshold:
                if seq_start is None:
                    seq_start = idx
            else:
                if seq_start is not None:
                    seq_data = throttle_data.iloc[seq_start:idx]
                    sequences.append({
                        'start_distance': float(seq_data['Distance'].iloc[0]),
                        'end_distance': float(seq_data['Distance'].iloc[-1]),
                        'max_throttle': float(seq_data['Throttle'].max())
                    })
                    seq_start = None
        
        return sequences
    
    def analyze_fuel_effect(self, year: int, grand_prix: str) -> Dict[str, Any]:
        """Analyze fuel effect on lap times throughout the race"""
        try:
            race_session = fastf1.get_session(year, grand_prix, 'Race')
            race_session.load()
            
            fuel_analysis = {}
            
            for driver in race_session.drivers:
                try:
                    driver_laps = race_session.laps.pick_driver(driver)
                    if len(driver_laps) > 5:  # Need sufficient laps for analysis
                        lap_times = []
                        lap_numbers = []
                        
                        for _, lap in driver_laps.iterrows():
                            if pd.notna(lap['LapTime']) and lap['LapTime'].total_seconds() > 0:
                                lap_times.append(lap['LapTime'].total_seconds())
                                lap_numbers.append(lap['LapNumber'])
                        
                        if len(lap_times) > 5:
                            # Calculate fuel effect (lap time increase per lap)
                            correlation = np.corrcoef(lap_numbers, lap_times)[0, 1] if len(lap_times) > 1 else 0
                            
                            # Estimate fuel effect (seconds per lap)
                            if len(lap_times) > 1:
                                slope, intercept, r_value, p_value, std_err = stats.linregress(lap_numbers, lap_times)
                                fuel_effect = slope
                            else:
                                fuel_effect = 0
                            
                            fuel_analysis[driver] = {
                                'fuel_effect_per_lap': float(fuel_effect),
                                'correlation_coefficient': float(correlation),
                                'fastest_lap_time': float(min(lap_times)),
                                'slowest_lap_time': float(max(lap_times)),
                                'lap_time_variance': float(np.var(lap_times)),
                                'total_laps': len(lap_times)
                            }
                
                except Exception as driver_error:
                    self.logger.warning(f"Error analyzing fuel effect for {driver}: {str(driver_error)}")
                    continue
            
            return {
                'fuel_analysis': fuel_analysis,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing fuel effect: {str(e)}")
            return {'error': str(e)}
    
    def analyze_consistency_metrics(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Analyze driver consistency across multiple metrics"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            consistency_metrics = {}
            
            for driver in session_obj.drivers:
                try:
                    driver_laps = session_obj.laps.pick_driver(driver)
                    if len(driver_laps) >= 3:  # Need at least 3 laps for consistency analysis
                        
                        # Lap time consistency
                        valid_lap_times = []
                        sector_1_times = []
                        sector_2_times = []
                        sector_3_times = []
                        
                        for _, lap in driver_laps.iterrows():
                            if pd.notna(lap['LapTime']) and lap['LapTime'].total_seconds() > 0:
                                valid_lap_times.append(lap['LapTime'].total_seconds())
                            
                            if pd.notna(lap['Sector1Time']):
                                sector_1_times.append(lap['Sector1Time'].total_seconds())
                            if pd.notna(lap['Sector2Time']):
                                sector_2_times.append(lap['Sector2Time'].total_seconds())
                            if pd.notna(lap['Sector3Time']):
                                sector_3_times.append(lap['Sector3Time'].total_seconds())
                        
                        if valid_lap_times:
                            consistency_metrics[driver] = {
                                'lap_time_std': float(np.std(valid_lap_times)),
                                'lap_time_cv': float(np.std(valid_lap_times) / np.mean(valid_lap_times)) if np.mean(valid_lap_times) > 0 else 0,
                                'sector_1_std': float(np.std(sector_1_times)) if sector_1_times else 0,
                                'sector_2_std': float(np.std(sector_2_times)) if sector_2_times else 0,
                                'sector_3_std': float(np.std(sector_3_times)) if sector_3_times else 0,
                                'total_valid_laps': len(valid_lap_times),
                                'fastest_lap': float(min(valid_lap_times)),
                                'consistency_score': self._calculate_consistency_score(valid_lap_times)
                            }
                
                except Exception as driver_error:
                    self.logger.warning(f"Error analyzing consistency for {driver}: {str(driver_error)}")
                    continue
            
            return {
                'consistency_analysis': consistency_metrics,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing consistency metrics: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_consistency_score(self, lap_times: List[float]) -> float:
        """Calculate a normalized consistency score (0-100, higher is more consistent)"""
        if len(lap_times) < 2:
            return 0.0
        
        # Use coefficient of variation, inverted and scaled
        mean_time = np.mean(lap_times)
        std_time = np.std(lap_times)
        
        if mean_time == 0:
            return 0.0
        
        cv = std_time / mean_time
        # Convert to score (lower CV = higher score)
        consistency_score = max(0, 100 * (1 - cv * 10))  # Scale factor of 10
        
        return min(100.0, consistency_score)
    
    def analyze_racecraft_metrics(self, year: int, grand_prix: str) -> Dict[str, Any]:
        """Analyze racecraft skills like defending, attacking, and race management"""
        try:
            race_session = fastf1.get_session(year, grand_prix, 'Race')
            race_session.load()
            
            racecraft_metrics = {}
            
            if hasattr(race_session, 'laps') and not race_session.laps.empty:
                laps = race_session.laps
                
                for driver in race_session.drivers:
                    try:
                        driver_laps = laps.pick_driver(driver)
                        if len(driver_laps) > 5:
                            
                            # Calculate various racecraft metrics
                            position_data = driver_laps['Position'].dropna()
                            lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
                            
                            if len(position_data) > 1 and lap_times:
                                # Position stability (how much position changed)
                                position_changes = abs(position_data.diff().dropna())
                                position_stability = float(position_changes.mean())
                                
                                # Race pace consistency
                                race_pace_std = float(np.std(lap_times))
                                
                                # Starting vs finishing position
                                start_pos = position_data.iloc[0] if len(position_data) > 0 else None
                                end_pos = position_data.iloc[-1] if len(position_data) > 0 else None
                                position_gain = float(start_pos - end_pos) if start_pos and end_pos else 0
                                
                                racecraft_metrics[driver] = {
                                    'position_stability': position_stability,
                                    'race_pace_consistency': race_pace_std,
                                    'position_gain': position_gain,
                                    'average_position': float(position_data.mean()),
                                    'best_position': float(position_data.min()),
                                    'worst_position': float(position_data.max()),
                                    'total_laps_completed': len(driver_laps)
                                }
                    
                    except Exception as driver_error:
                        self.logger.warning(f"Error analyzing racecraft for {driver}: {str(driver_error)}")
                        continue
            
            return {
                'racecraft_analysis': racecraft_metrics,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing racecraft metrics: {str(e)}")
            return {'error': str(e)}