import pandas as pd
import numpy as np
from utils.data_loader import DataLoader

class WeatherAnalytics:
    """Weather analysis for F1 sessions"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def analyze_session_weather(self, year, grand_prix, session):
        """Analyze weather conditions and their impact"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return None
            
            weather_data = self.data_loader.get_weather_data(session_data)
            if weather_data is None or weather_data.empty:
                return {
                    'error': 'No weather data available for this session'
                }
            
            analysis = {
                'weather_summary': self.summarize_weather_conditions(weather_data),
                'temperature_analysis': self.analyze_temperature_trends(weather_data),
                'track_conditions': self.analyze_track_conditions(weather_data),
                'weather_impact': self.analyze_weather_impact(session_data, weather_data)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def summarize_weather_conditions(self, weather_data):
        """Summarize overall weather conditions"""
        try:
            summary = {
                'air_temperature': {
                    'min': float(weather_data['AirTemp'].min()),
                    'max': float(weather_data['AirTemp'].max()),
                    'avg': float(weather_data['AirTemp'].mean()),
                    'unit': '°C'
                },
                'track_temperature': {
                    'min': float(weather_data['TrackTemp'].min()),
                    'max': float(weather_data['TrackTemp'].max()),
                    'avg': float(weather_data['TrackTemp'].mean()),
                    'unit': '°C'
                },
                'humidity': {
                    'min': float(weather_data['Humidity'].min()),
                    'max': float(weather_data['Humidity'].max()),
                    'avg': float(weather_data['Humidity'].mean()),
                    'unit': '%'
                },
                'pressure': {
                    'min': float(weather_data['Pressure'].min()),
                    'max': float(weather_data['Pressure'].max()),
                    'avg': float(weather_data['Pressure'].mean()),
                    'unit': 'mbar'
                }
            }
            
            # Add wind analysis if available
            if 'WindSpeed' in weather_data.columns:
                summary['wind'] = {
                    'min_speed': float(weather_data['WindSpeed'].min()),
                    'max_speed': float(weather_data['WindSpeed'].max()),
                    'avg_speed': float(weather_data['WindSpeed'].mean()),
                    'speed_unit': 'm/s'
                }
                
                if 'WindDirection' in weather_data.columns:
                    summary['wind']['avg_direction'] = float(weather_data['WindDirection'].mean())
                    summary['wind']['direction_unit'] = 'degrees'
            
            # Add rainfall information if available
            if 'Rainfall' in weather_data.columns:
                summary['rainfall'] = {
                    'total': float(weather_data['Rainfall'].sum()),
                    'max_intensity': float(weather_data['Rainfall'].max()),
                    'periods_with_rain': int((weather_data['Rainfall'] > 0).sum()),
                    'unit': 'mm'
                }
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_temperature_trends(self, weather_data):
        """Analyze temperature trends throughout the session"""
        try:
            trends = {
                'air_temp_trend': self.calculate_trend(weather_data['AirTemp']),
                'track_temp_trend': self.calculate_trend(weather_data['TrackTemp']),
                'temperature_correlation': float(weather_data['AirTemp'].corr(weather_data['TrackTemp'])),
                'temp_difference': {
                    'min': float((weather_data['TrackTemp'] - weather_data['AirTemp']).min()),
                    'max': float((weather_data['TrackTemp'] - weather_data['AirTemp']).max()),
                    'avg': float((weather_data['TrackTemp'] - weather_data['AirTemp']).mean())
                }
            }
            
            return trends
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_track_conditions(self, weather_data):
        """Analyze track conditions based on weather"""
        try:
            conditions = {
                'grip_level': self.estimate_grip_level(weather_data),
                'tire_performance_impact': self.estimate_tire_impact(weather_data),
                'strategy_implications': self.analyze_strategy_implications(weather_data)
            }
            
            return conditions
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_weather_impact(self, session_data, weather_data):
        """Analyze weather impact on lap times and performance"""
        try:
            impact_analysis = {
                'lap_time_correlation': {},
                'performance_windows': [],
                'weather_sensitive_drivers': []
            }
            
            # Analyze lap time correlation with weather
            for driver in session_data.drivers[:5]:  # Limit to top 5 for performance
                try:
                    driver_laps = session_data.laps.pick_driver(driver)
                    if len(driver_laps) < 5:
                        continue
                    
                    # Get lap times as seconds
                    lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
                    
                    if len(lap_times) < 5:
                        continue
                    
                    # Correlate with weather conditions (simplified)
                    avg_air_temp = weather_data['AirTemp'].mean()
                    avg_track_temp = weather_data['TrackTemp'].mean()
                    
                    impact_analysis['lap_time_correlation'][driver] = {
                        'avg_lap_time': float(np.mean(lap_times)),
                        'temp_conditions': {
                            'air_temp': float(avg_air_temp),
                            'track_temp': float(avg_track_temp)
                        },
                        'performance_rating': self.rate_weather_performance(lap_times, avg_track_temp)
                    }
                    
                except Exception as driver_error:
                    continue
            
            return impact_analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_trend(self, data_series):
        """Calculate trend direction for a data series"""
        try:
            if len(data_series) < 2:
                return 'insufficient_data'
            
            # Simple linear regression slope
            x = np.arange(len(data_series))
            slope = np.polyfit(x, data_series, 1)[0]
            
            if slope > 0.1:
                return 'increasing'
            elif slope < -0.1:
                return 'decreasing'
            else:
                return 'stable'
                
        except Exception as e:
            return 'unknown'
    
    def estimate_grip_level(self, weather_data):
        """Estimate track grip level based on weather conditions"""
        try:
            avg_track_temp = weather_data['TrackTemp'].mean()
            avg_humidity = weather_data['Humidity'].mean()
            
            # Simplified grip estimation
            if avg_track_temp > 45:
                grip_base = 'low'  # Very hot track
            elif avg_track_temp > 35:
                grip_base = 'medium-high'
            elif avg_track_temp > 25:
                grip_base = 'high'
            else:
                grip_base = 'medium'  # Cold track
            
            # Adjust for humidity
            if avg_humidity > 80:
                grip_modifier = 'reduced'
            elif avg_humidity < 40:
                grip_modifier = 'enhanced'
            else:
                grip_modifier = 'normal'
            
            # Check for rain
            has_rain = False
            if 'Rainfall' in weather_data.columns:
                has_rain = weather_data['Rainfall'].sum() > 0
            
            return {
                'base_grip': grip_base,
                'humidity_impact': grip_modifier,
                'wet_conditions': has_rain,
                'overall_assessment': self.overall_grip_assessment(grip_base, grip_modifier, has_rain)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def estimate_tire_impact(self, weather_data):
        """Estimate tire performance impact"""
        try:
            avg_track_temp = weather_data['TrackTemp'].mean()
            
            impact = {
                'degradation_rate': 'normal',
                'optimal_compounds': [],
                'strategy_recommendation': 'standard'
            }
            
            if avg_track_temp > 50:
                impact['degradation_rate'] = 'very_high'
                impact['optimal_compounds'] = ['HARD']
                impact['strategy_recommendation'] = 'aggressive_cooling'
            elif avg_track_temp > 40:
                impact['degradation_rate'] = 'high'
                impact['optimal_compounds'] = ['HARD', 'MEDIUM']
                impact['strategy_recommendation'] = 'conservative'
            elif avg_track_temp > 25:
                impact['degradation_rate'] = 'normal'
                impact['optimal_compounds'] = ['MEDIUM', 'SOFT']
                impact['strategy_recommendation'] = 'standard'
            else:
                impact['degradation_rate'] = 'low'
                impact['optimal_compounds'] = ['SOFT', 'MEDIUM']
                impact['strategy_recommendation'] = 'aggressive'
            
            return impact
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_strategy_implications(self, weather_data):
        """Analyze strategic implications of weather"""
        try:
            implications = []
            
            avg_track_temp = weather_data['TrackTemp'].mean()
            temp_range = weather_data['TrackTemp'].max() - weather_data['TrackTemp'].min()
            
            if temp_range > 10:
                implications.append("High temperature variation - tire performance will change significantly")
            
            if avg_track_temp > 45:
                implications.append("Very hot track - expect high tire degradation")
                implications.append("Consider hard compound strategies")
            
            if avg_track_temp < 25:
                implications.append("Cool track - tire warm-up will be critical")
                implications.append("Soft compounds may struggle for temperature")
            
            # Check for rain potential
            if 'Rainfall' in weather_data.columns:
                if weather_data['Rainfall'].sum() > 0:
                    implications.append("Wet conditions - intermediate/wet tire strategies needed")
                
                humidity = weather_data['Humidity'].mean()
                if humidity > 85:
                    implications.append("High humidity - increased rain risk")
            
            return implications
            
        except Exception as e:
            return []
    
    def overall_grip_assessment(self, base_grip, humidity_impact, has_rain):
        """Provide overall grip assessment"""
        if has_rain:
            return 'very_low_wet'
        
        grip_map = {
            ('low', 'reduced'): 'very_low',
            ('low', 'normal'): 'low',
            ('low', 'enhanced'): 'medium_low',
            ('medium', 'reduced'): 'low',
            ('medium', 'normal'): 'medium',
            ('medium', 'enhanced'): 'medium_high',
            ('medium-high', 'reduced'): 'medium',
            ('medium-high', 'normal'): 'medium_high',
            ('medium-high', 'enhanced'): 'high',
            ('high', 'reduced'): 'medium_high',
            ('high', 'normal'): 'high',
            ('high', 'enhanced'): 'very_high'
        }
        
        return grip_map.get((base_grip, humidity_impact), 'medium')
    
    def rate_weather_performance(self, lap_times, track_temp):
        """Rate driver performance relative to weather conditions"""
        try:
            if not lap_times:
                return 'unknown'
            
            avg_lap_time = np.mean(lap_times)
            consistency = np.std(lap_times)
            
            # Simplified performance rating
            if track_temp > 45:  # Hot conditions
                if consistency < 1.0:  # Very consistent in difficult conditions
                    return 'excellent'
                elif consistency < 2.0:
                    return 'good'
                else:
                    return 'struggling'
            else:  # Normal conditions
                if consistency < 0.5:
                    return 'excellent'
                elif consistency < 1.5:
                    return 'good'
                else:
                    return 'average'
                    
        except Exception as e:
            return 'unknown'
