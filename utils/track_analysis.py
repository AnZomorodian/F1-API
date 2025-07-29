"""
Track Analysis Module
Advanced track-specific analysis and sector breakdowns
"""

import fastf1
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

class TrackAnalyzer:
    """Advanced track analysis and sector performance"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_track_characteristics(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Analyze track characteristics and layout impact"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            track_analysis = {
                'track_info': {
                    'circuit_name': grand_prix,
                    'total_distance': 0,
                    'turn_count': 0,
                    'drs_zones': 0
                },
                'sector_characteristics': {},
                'speed_analysis': {},
                'elevation_analysis': {}
            }
            
            # Analyze fastest lap telemetry for track characteristics
            fastest_lap = session_obj.laps.pick_fastest()
            if fastest_lap is not None:
                telemetry = fastest_lap.get_telemetry()
                
                if not telemetry.empty:
                    # Track distance
                    track_analysis['track_info']['total_distance'] = float(telemetry['Distance'].max())
                    
                    # Speed analysis
                    track_analysis['speed_analysis'] = {
                        'max_speed': float(telemetry['Speed'].max()),
                        'min_speed': float(telemetry['Speed'].min()),
                        'avg_speed': float(telemetry['Speed'].mean()),
                        'speed_variance': float(telemetry['Speed'].var()),
                        'high_speed_percentage': float((telemetry['Speed'] > telemetry['Speed'].quantile(0.8)).sum() / len(telemetry) * 100)
                    }
                    
                    # Turn analysis (low speed zones)
                    low_speed_zones = telemetry[telemetry['Speed'] < telemetry['Speed'].quantile(0.3)]
                    track_analysis['track_info']['turn_count'] = len(self._identify_turns(low_speed_zones))
                    
                    # DRS zones
                    if 'DRS' in telemetry.columns:
                        drs_zones = telemetry[telemetry['DRS'] > 0]
                        track_analysis['track_info']['drs_zones'] = len(self._identify_drs_zones(drs_zones))
                    
                    # Sector analysis
                    track_analysis['sector_characteristics'] = self._analyze_sector_characteristics(telemetry)
            
            return {
                'track_analysis': track_analysis,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing track characteristics: {str(e)}")
            return {'error': str(e)}
    
    def _identify_turns(self, low_speed_data: pd.DataFrame) -> List[Dict]:
        """Identify distinct turns from low speed telemetry data"""
        turns = []
        if low_speed_data.empty:
            return turns
        
        # Group consecutive low-speed zones as turns
        distance_gaps = low_speed_data['Distance'].diff()
        gap_threshold = 200  # 200m gap indicates separate turns
        
        turn_start = None
        for idx, gap in enumerate(distance_gaps):
            if pd.isna(gap) or gap <= gap_threshold:
                if turn_start is None:
                    turn_start = idx
            else:
                if turn_start is not None:
                    turn_data = low_speed_data.iloc[turn_start:idx]
                    turns.append({
                        'start_distance': float(turn_data['Distance'].iloc[0]),
                        'end_distance': float(turn_data['Distance'].iloc[-1]),
                        'min_speed': float(turn_data['Speed'].min()),
                        'turn_length': float(turn_data['Distance'].iloc[-1] - turn_data['Distance'].iloc[0])
                    })
                    turn_start = None
        
        return turns
    
    def _identify_drs_zones(self, drs_data: pd.DataFrame) -> List[Dict]:
        """Identify DRS zones from telemetry data"""
        drs_zones = []
        if drs_data.empty:
            return drs_zones
        
        # Group consecutive DRS active zones
        distance_gaps = drs_data['Distance'].diff()
        gap_threshold = 100  # 100m gap indicates separate DRS zones
        
        zone_start = None
        for idx, gap in enumerate(distance_gaps):
            if pd.isna(gap) or gap <= gap_threshold:
                if zone_start is None:
                    zone_start = idx
            else:
                if zone_start is not None:
                    zone_data = drs_data.iloc[zone_start:idx]
                    drs_zones.append({
                        'start_distance': float(zone_data['Distance'].iloc[0]),
                        'end_distance': float(zone_data['Distance'].iloc[-1]),
                        'zone_length': float(zone_data['Distance'].iloc[-1] - zone_data['Distance'].iloc[0])
                    })
                    zone_start = None
        
        return drs_zones
    
    def _analyze_sector_characteristics(self, telemetry: pd.DataFrame) -> Dict[str, Any]:
        """Analyze characteristics of each sector"""
        sector_analysis = {}
        
        # Divide track into 3 sectors approximately
        total_distance = telemetry['Distance'].max()
        sector_length = total_distance / 3
        
        for sector_num in range(1, 4):
            sector_start = (sector_num - 1) * sector_length
            sector_end = sector_num * sector_length
            
            sector_data = telemetry[
                (telemetry['Distance'] >= sector_start) & 
                (telemetry['Distance'] < sector_end)
            ]
            
            if not sector_data.empty:
                sector_analysis[f'sector_{sector_num}'] = {
                    'avg_speed': float(sector_data['Speed'].mean()),
                    'max_speed': float(sector_data['Speed'].max()),
                    'min_speed': float(sector_data['Speed'].min()),
                    'avg_throttle': float(sector_data['Throttle'].mean()),
                    'avg_brake': float(sector_data['Brake'].mean()),
                    'gear_changes': len(sector_data['nGear'].diff().dropna()[sector_data['nGear'].diff().dropna() != 0]),
                    'sector_type': self._classify_sector_type(sector_data)
                }
        
        return sector_analysis
    
    def _classify_sector_type(self, sector_data: pd.DataFrame) -> str:
        """Classify sector type based on characteristics"""
        avg_speed = sector_data['Speed'].mean()
        avg_throttle = sector_data['Throttle'].mean()
        speed_variance = sector_data['Speed'].var()
        
        if avg_speed > 200 and avg_throttle > 80:
            return "High-speed straight"
        elif avg_speed < 150 and speed_variance > 500:
            return "Technical corners"
        elif avg_throttle > 70 and speed_variance < 300:
            return "Acceleration zone"
        else:
            return "Mixed characteristics"
    
    def get_driver_track_mastery(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Analyze how well each driver has mastered the track"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            driver_mastery = {}
            
            for driver in session_obj.drivers:
                try:
                    driver_laps = session_obj.laps.pick_drivers(driver)
                    if len(driver_laps) >= 3:  # Need multiple laps for analysis
                        
                        mastery_metrics = {
                            'consistency_score': self._calculate_consistency_score(driver_laps),
                            'sector_mastery': self._analyze_sector_mastery(driver_laps),
                            'lap_time_improvement': self._calculate_improvement_rate(driver_laps),
                            'track_limits_violations': self._count_track_limits_violations(driver_laps),
                            'overall_mastery_score': 0.0
                        }
                        
                        # Calculate overall mastery score (0-100)
                        mastery_metrics['overall_mastery_score'] = self._calculate_overall_mastery(mastery_metrics)
                        
                        driver_mastery[driver] = mastery_metrics
                
                except Exception as driver_error:
                    self.logger.warning(f"Error analyzing track mastery for {driver}: {str(driver_error)}")
                    continue
            
            return {
                'track_mastery_analysis': driver_mastery,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing driver track mastery: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_consistency_score(self, driver_laps: pd.DataFrame) -> float:
        """Calculate lap time consistency score"""
        valid_laps = driver_laps['LapTime'].dropna()
        if len(valid_laps) < 2:
            return 0.0
        
        lap_times_seconds = [lt.total_seconds() for lt in valid_laps]
        cv = np.std(lap_times_seconds) / np.mean(lap_times_seconds) if np.mean(lap_times_seconds) > 0 else 0
        
        # Convert to score (lower CV = higher score)
        consistency_score = max(0, 100 * (1 - cv * 20))  # Scale factor
        return min(100.0, consistency_score)
    
    def _analyze_sector_mastery(self, driver_laps: pd.DataFrame) -> Dict[str, float]:
        """Analyze mastery of each sector"""
        sector_mastery = {}
        
        for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
            sector_times = driver_laps[sector].dropna()
            if len(sector_times) > 1:
                sector_times_seconds = [st.total_seconds() for st in sector_times]
                cv = np.std(sector_times_seconds) / np.mean(sector_times_seconds) if np.mean(sector_times_seconds) > 0 else 0
                mastery_score = max(0, 100 * (1 - cv * 25))  # Higher penalty for sector inconsistency
                sector_mastery[sector.replace('Time', '').lower()] = min(100.0, mastery_score)
            else:
                sector_mastery[sector.replace('Time', '').lower()] = 0.0
        
        return sector_mastery
    
    def _calculate_improvement_rate(self, driver_laps: pd.DataFrame) -> float:
        """Calculate rate of improvement throughout session"""
        valid_laps = driver_laps['LapTime'].dropna()
        if len(valid_laps) < 3:
            return 0.0
        
        lap_times_seconds = [lt.total_seconds() for lt in valid_laps]
        lap_numbers = list(range(len(lap_times_seconds)))
        
        # Calculate improvement trend (negative slope = improvement)
        if len(lap_times_seconds) > 1:
            correlation = np.corrcoef(lap_numbers, lap_times_seconds)[0, 1]
            improvement_score = max(0, 100 * (1 + correlation))  # Negative correlation gives higher score
            return min(100.0, improvement_score)
        
        return 0.0
    
    def _count_track_limits_violations(self, driver_laps: pd.DataFrame) -> int:
        """Count track limits violations (if available in data)"""
        # This would need specific track limits data from FastF1
        # For now, return 0 as placeholder
        return 0
    
    def _calculate_overall_mastery(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall track mastery score"""
        # Weighted average of different mastery components
        weights = {
            'consistency_score': 0.3,
            'lap_time_improvement': 0.3,
            'sector_mastery_avg': 0.4
        }
        
        sector_scores = list(metrics['sector_mastery'].values())
        sector_avg = np.mean(sector_scores) if sector_scores else 0
        
        overall_score = (
            weights['consistency_score'] * metrics['consistency_score'] +
            weights['lap_time_improvement'] * metrics['lap_time_improvement'] +
            weights['sector_mastery_avg'] * sector_avg
        )
        
        return min(100.0, overall_score)
    
    def get_optimal_racing_line_analysis(self, year: int, grand_prix: str, session: str, driver: str) -> Dict[str, Any]:
        """Analyze optimal racing line based on fastest lap telemetry"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            driver_laps = session_obj.laps.pick_drivers(driver)
            if driver_laps.empty:
                return {'error': f'No data found for driver {driver}'}
            
            fastest_lap = driver_laps.pick_fastest()
            if fastest_lap is None:
                return {'error': f'No fastest lap found for driver {driver}'}
            
            telemetry = fastest_lap.get_telemetry()
            
            racing_line_analysis = {
                'speed_optimization': self._analyze_speed_optimization(telemetry),
                'braking_optimization': self._analyze_braking_optimization(telemetry),
                'throttle_optimization': self._analyze_throttle_optimization(telemetry),
                'gear_optimization': self._analyze_gear_optimization(telemetry),
                'racing_line_efficiency': self._calculate_racing_line_efficiency(telemetry)
            }
            
            return {
                'racing_line_analysis': racing_line_analysis,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session,
                    'driver': driver
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing optimal racing line: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_speed_optimization(self, telemetry: pd.DataFrame) -> Dict[str, float]:
        """Analyze speed optimization opportunities"""
        return {
            'max_speed_achieved': float(telemetry['Speed'].max()),
            'average_corner_exit_speed': float(telemetry[telemetry['Throttle'] > 50]['Speed'].mean()),
            'speed_consistency': float(100 - (telemetry['Speed'].std() / telemetry['Speed'].mean() * 100))
        }
    
    def _analyze_braking_optimization(self, telemetry: pd.DataFrame) -> Dict[str, float]:
        """Analyze braking optimization"""
        brake_zones = telemetry[telemetry['Brake'] > 0]
        if brake_zones.empty:
            return {'efficiency': 0.0, 'consistency': 0.0}
        
        return {
            'braking_efficiency': float(brake_zones['Brake'].mean()),
            'braking_consistency': float(100 - (brake_zones['Brake'].std() / brake_zones['Brake'].mean() * 100))
        }
    
    def _analyze_throttle_optimization(self, telemetry: pd.DataFrame) -> Dict[str, float]:
        """Analyze throttle optimization"""
        return {
            'throttle_efficiency': float(telemetry['Throttle'].mean()),
            'full_throttle_percentage': float((telemetry['Throttle'] == 100).sum() / len(telemetry) * 100)
        }
    
    def _analyze_gear_optimization(self, telemetry: pd.DataFrame) -> Dict[str, float]:
        """Analyze gear usage optimization"""
        gear_changes = len(telemetry['nGear'].diff().dropna()[telemetry['nGear'].diff().dropna() != 0])
        return {
            'total_gear_changes': float(gear_changes),
            'average_gear': float(telemetry['nGear'].mean()),
            'max_gear_used': float(telemetry['nGear'].max())
        }
    
    def _calculate_racing_line_efficiency(self, telemetry: pd.DataFrame) -> float:
        """Calculate overall racing line efficiency score"""
        # Composite score based on multiple factors
        speed_factor = (telemetry['Speed'].mean() / telemetry['Speed'].max()) * 100
        throttle_factor = telemetry['Throttle'].mean()
        consistency_factor = 100 - (telemetry['Speed'].std() / telemetry['Speed'].mean() * 10)
        
        efficiency_score = (speed_factor * 0.4 + throttle_factor * 0.3 + consistency_factor * 0.3)
        return min(100.0, efficiency_score)