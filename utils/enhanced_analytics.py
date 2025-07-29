"""
Enhanced Analytics Module
Advanced F1 data analysis and insights
"""

import fastf1
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import scipy.stats as stats

class EnhancedF1Analytics:
    """Enhanced F1 analytics with advanced metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_tyre_performance_degradation(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Analyze tyre performance degradation patterns"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            tyre_analysis = {}
            
            for driver in session_obj.drivers:
                try:
                    driver_laps = session_obj.laps.pick_drivers(driver)
                    if not driver_laps.empty:
                        tyre_stints = []
                        current_compound = None
                        current_stint = []
                        
                        for _, lap in driver_laps.iterrows():
                            if pd.notna(lap['Compound']) and pd.notna(lap['LapTime']):
                                if current_compound != lap['Compound']:
                                    if current_stint:
                                        tyre_stints.append({
                                            'compound': current_compound,
                                            'laps': current_stint.copy(),
                                            'degradation': self._calculate_degradation(current_stint)
                                        })
                                    current_compound = lap['Compound']
                                    current_stint = []
                                
                                current_stint.append({
                                    'lap_number': lap['LapNumber'],
                                    'lap_time': lap['LapTime'].total_seconds(),
                                    'tyre_life': lap['TyreLife'] if pd.notna(lap['TyreLife']) else 0
                                })
                        
                        if current_stint:
                            tyre_stints.append({
                                'compound': current_compound,
                                'laps': current_stint.copy(),
                                'degradation': self._calculate_degradation(current_stint)
                            })
                        
                        tyre_analysis[driver] = {
                            'tyre_stints': tyre_stints,
                            'total_stints': len(tyre_stints),
                            'compounds_used': list(set([stint['compound'] for stint in tyre_stints]))
                        }
                
                except Exception as driver_error:
                    self.logger.warning(f"Error analyzing tyre performance for {driver}: {str(driver_error)}")
                    continue
            
            return {
                'tyre_performance_analysis': tyre_analysis,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing tyre performance: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_degradation(self, stint_laps: List[Dict]) -> Dict[str, float]:
        """Calculate tyre degradation rate for a stint"""
        if len(stint_laps) < 2:
            return {'degradation_rate': 0.0, 'correlation': 0.0}
        
        lap_numbers = [lap['lap_number'] for lap in stint_laps]
        lap_times = [lap['lap_time'] for lap in stint_laps]
        
        if len(lap_times) < 2:
            return {'degradation_rate': 0.0, 'correlation': 0.0}
        
        # Calculate degradation rate (seconds per lap)
        correlation = np.corrcoef(lap_numbers, lap_times)[0, 1] if len(lap_times) > 1 else 0
        slope, _, _, _, _ = stats.linregress(lap_numbers, lap_times) if len(lap_times) > 1 else (0, 0, 0, 0, 0)
        
        return {
            'degradation_rate': float(slope),
            'correlation': float(correlation)
        }
    
    def get_weather_impact_analysis(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Analyze weather impact on performance"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            weather_data = session_obj.weather_data
            if weather_data.empty:
                return {'error': 'No weather data available'}
            
            weather_analysis = {
                'temperature_range': {
                    'air_temp_min': float(weather_data['AirTemp'].min()),
                    'air_temp_max': float(weather_data['AirTemp'].max()),
                    'track_temp_min': float(weather_data['TrackTemp'].min()),
                    'track_temp_max': float(weather_data['TrackTemp'].max())
                },
                'humidity_stats': {
                    'min': float(weather_data['Humidity'].min()),
                    'max': float(weather_data['Humidity'].max()),
                    'avg': float(weather_data['Humidity'].mean())
                },
                'pressure_stats': {
                    'min': float(weather_data['Pressure'].min()),
                    'max': float(weather_data['Pressure'].max()),
                    'avg': float(weather_data['Pressure'].mean())
                },
                'wind_analysis': {
                    'wind_speed_avg': float(weather_data['WindSpeed'].mean()),
                    'wind_speed_max': float(weather_data['WindSpeed'].max()),
                    'wind_direction_avg': float(weather_data['WindDirection'].mean())
                }
            }
            
            # Analyze performance correlation with weather
            if hasattr(session_obj, 'laps') and not session_obj.laps.empty:
                weather_performance = self._analyze_weather_performance_correlation(session_obj, weather_data)
                weather_analysis['performance_correlation'] = weather_performance
            
            return {
                'weather_analysis': weather_analysis,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing weather impact: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_weather_performance_correlation(self, session_obj, weather_data) -> Dict[str, Any]:
        """Analyze correlation between weather conditions and lap times"""
        correlations = {}
        
        try:
            # Get lap times with weather data
            laps_with_weather = []
            for _, lap in session_obj.laps.iterrows():
                if pd.notna(lap['LapTime']):
                    # Find closest weather data point
                    lap_time_seconds = lap['Time'].total_seconds() if pd.notna(lap['Time']) else 0
                    closest_weather = weather_data.iloc[(weather_data['Time'] - lap_time_seconds).abs().argsort()[:1]]
                    
                    if not closest_weather.empty:
                        weather_point = closest_weather.iloc[0]
                        laps_with_weather.append({
                            'lap_time': lap['LapTime'].total_seconds(),
                            'air_temp': weather_point['AirTemp'],
                            'track_temp': weather_point['TrackTemp'],
                            'humidity': weather_point['Humidity'],
                            'wind_speed': weather_point['WindSpeed']
                        })
            
            if len(laps_with_weather) > 5:
                df = pd.DataFrame(laps_with_weather)
                correlations = {
                    'air_temp_correlation': float(df['lap_time'].corr(df['air_temp'])),
                    'track_temp_correlation': float(df['lap_time'].corr(df['track_temp'])),
                    'humidity_correlation': float(df['lap_time'].corr(df['humidity'])),
                    'wind_speed_correlation': float(df['lap_time'].corr(df['wind_speed']))
                }
        
        except Exception as e:
            self.logger.warning(f"Error calculating weather correlations: {str(e)}")
        
        return correlations
    
    def get_session_progression_analysis(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Analyze how performance evolves throughout the session"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            progression_analysis = {}
            
            # Divide session into time segments
            session_start = session_obj.session_start_time
            session_end = session_obj.session_end_time
            
            if session_start and session_end:
                session_duration = (session_end - session_start).total_seconds()
                segment_duration = session_duration / 4  # 4 segments
                
                segments = []
                for i in range(4):
                    segment_start = session_start + pd.Timedelta(seconds=i * segment_duration)
                    segment_end = session_start + pd.Timedelta(seconds=(i + 1) * segment_duration)
                    
                    segment_laps = session_obj.laps[
                        (session_obj.laps['Time'] >= segment_start) & 
                        (session_obj.laps['Time'] < segment_end)
                    ]
                    
                    if not segment_laps.empty:
                        segment_analysis = {
                            'segment_number': i + 1,
                            'lap_count': len(segment_laps),
                            'average_lap_time': float(segment_laps['LapTime'].mean().total_seconds()) if not segment_laps['LapTime'].isna().all() else 0,
                            'fastest_lap_time': float(segment_laps['LapTime'].min().total_seconds()) if not segment_laps['LapTime'].isna().all() else 0,
                            'track_evolution': self._calculate_track_evolution(segment_laps)
                        }
                        segments.append(segment_analysis)
                
                progression_analysis['time_segments'] = segments
                progression_analysis['overall_improvement'] = self._calculate_overall_improvement(segments)
            
            return {
                'session_progression': progression_analysis,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing session progression: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_track_evolution(self, segment_laps) -> Dict[str, float]:
        """Calculate track evolution metrics for a segment"""
        if segment_laps.empty:
            return {'improvement_rate': 0.0, 'lap_time_variance': 0.0}
        
        valid_lap_times = segment_laps['LapTime'].dropna()
        if len(valid_lap_times) < 2:
            return {'improvement_rate': 0.0, 'lap_time_variance': 0.0}
        
        lap_times_seconds = [lt.total_seconds() for lt in valid_lap_times]
        lap_numbers = list(range(len(lap_times_seconds)))
        
        # Calculate improvement rate
        slope, _, _, _, _ = stats.linregress(lap_numbers, lap_times_seconds) if len(lap_times_seconds) > 1 else (0, 0, 0, 0, 0)
        
        return {
            'improvement_rate': float(slope),  # Negative = getting faster
            'lap_time_variance': float(np.var(lap_times_seconds))
        }
    
    def _calculate_overall_improvement(self, segments: List[Dict]) -> Dict[str, float]:
        """Calculate overall track improvement throughout session"""
        if len(segments) < 2:
            return {'total_improvement': 0.0, 'improvement_percentage': 0.0}
        
        first_segment_avg = segments[0]['average_lap_time']
        last_segment_avg = segments[-1]['average_lap_time']
        
        if first_segment_avg > 0 and last_segment_avg > 0:
            improvement = first_segment_avg - last_segment_avg
            improvement_percentage = (improvement / first_segment_avg) * 100
            
            return {
                'total_improvement': float(improvement),
                'improvement_percentage': float(improvement_percentage)
            }
        
        return {'total_improvement': 0.0, 'improvement_percentage': 0.0}