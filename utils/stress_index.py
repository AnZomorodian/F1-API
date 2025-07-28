import pandas as pd
import numpy as np
from utils.data_loader import DataLoader

class DriverStressAnalyzer:
    """Analyze driver stress levels based on telemetry data"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def analyze_driver_stress(self, year, grand_prix, session, driver):
        """Comprehensive driver stress analysis"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return None
            
            driver_laps = self.data_loader.get_driver_laps(session_data, driver)
            if driver_laps is None or driver_laps.empty:
                return {'error': f'No data found for driver {driver}'}
            
            analysis = {
                'overall_stress_index': self.calculate_overall_stress_index(driver_laps),
                'sector_stress_analysis': self.analyze_sector_stress(driver_laps),
                'consistency_stress': self.analyze_consistency_stress(driver_laps),
                'braking_stress': self.analyze_braking_stress(driver_laps),
                'cornering_stress': self.analyze_cornering_stress(driver_laps),
                'pressure_moments': self.identify_pressure_moments(driver_laps),
                'stress_trends': self.analyze_stress_trends(driver_laps),
                'comparative_stress': self.compare_with_session_average(driver_laps, session_data)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_overall_stress_index(self, driver_laps):
        """Calculate overall stress index (0-100 scale)"""
        try:
            stress_factors = []
            
            # Lap time consistency stress
            lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
            if len(lap_times) > 1:
                consistency_stress = (np.std(lap_times) / np.mean(lap_times)) * 100
                stress_factors.append(min(100, consistency_stress * 50))
            
            # Sector time variability stress
            for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
                sector_times = driver_laps[sector].dropna()
                if len(sector_times) > 1:
                    sector_times_seconds = [st.total_seconds() for st in sector_times]
                    sector_stress = (np.std(sector_times_seconds) / np.mean(sector_times_seconds)) * 100
                    stress_factors.append(min(100, sector_stress * 60))
            
            # Position changes stress
            positions = driver_laps['Position'].dropna()
            if len(positions) > 1:
                position_changes = np.diff(positions.values)
                position_stress = np.sum(np.abs(position_changes)) * 2
                stress_factors.append(min(100, position_stress))
            
            # Calculate weighted average
            if stress_factors:
                overall_stress = float(np.mean(stress_factors))
                return {
                    'index': overall_stress,
                    'rating': self.rate_stress_level(overall_stress),
                    'factors_analyzed': len(stress_factors)
                }
            
            return {'index': 0, 'rating': 'insufficient_data', 'factors_analyzed': 0}
            
        except Exception as e:
            return {'index': 0, 'rating': 'error', 'factors_analyzed': 0}
    
    def analyze_sector_stress(self, driver_laps):
        """Analyze stress levels in different track sectors"""
        try:
            sector_stress = {}
            
            for i, sector in enumerate(['Sector1Time', 'Sector2Time', 'Sector3Time'], 1):
                sector_times = driver_laps[sector].dropna()
                if len(sector_times) <= 1:
                    continue
                
                sector_times_seconds = [st.total_seconds() for st in sector_times]
                
                # Calculate sector-specific stress metrics
                mean_time = np.mean(sector_times_seconds)
                std_time = np.std(sector_times_seconds)
                cv = std_time / mean_time if mean_time > 0 else 0
                
                # Identify outliers
                outliers = self.identify_outlier_sectors(sector_times_seconds)
                
                sector_stress[f'sector_{i}'] = {
                    'mean_time': float(mean_time),
                    'standard_deviation': float(std_time),
                    'coefficient_of_variation': float(cv),
                    'stress_index': float(min(100, cv * 200)),
                    'outlier_count': len(outliers),
                    'consistency_rating': self.rate_sector_consistency(cv),
                    'best_time': float(min(sector_times_seconds)),
                    'worst_time': float(max(sector_times_seconds))
                }
            
            return sector_stress
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_consistency_stress(self, driver_laps):
        """Analyze stress related to lap time consistency"""
        try:
            lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
            if len(lap_times) < 3:
                return {'error': 'Insufficient data for consistency analysis'}
            
            # Moving average analysis
            window_size = min(5, len(lap_times) // 2)
            moving_avg = pd.Series(lap_times).rolling(window=window_size).mean()
            moving_std = pd.Series(lap_times).rolling(window=window_size).std()
            
            # Identify consistency breakdowns
            consistency_breakdowns = []
            for i in range(window_size, len(lap_times)):
                if moving_std.iloc[i] > moving_std.mean() + 2 * moving_std.std():
                    consistency_breakdowns.append({
                        'lap_number': i + 1,
                        'deviation': float(moving_std.iloc[i]),
                        'severity': 'high' if moving_std.iloc[i] > moving_std.mean() + 3 * moving_std.std() else 'moderate'
                    })
            
            return {
                'overall_consistency': float(np.std(lap_times) / np.mean(lap_times)),
                'consistency_rating': self.rate_consistency(np.std(lap_times) / np.mean(lap_times)),
                'breakdown_incidents': consistency_breakdowns,
                'most_consistent_period': self.find_most_consistent_period(lap_times),
                'least_consistent_period': self.find_least_consistent_period(lap_times)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_braking_stress(self, driver_laps):
        """Analyze stress related to braking performance"""
        try:
            braking_stress_data = []
            
            for _, lap in driver_laps.iterrows():
                try:
                    telemetry = self.data_loader.get_telemetry_data(lap)
                    if telemetry is None or telemetry.empty:
                        continue
                    
                    # Analyze braking events
                    brake_data = telemetry['Brake']
                    if brake_data.empty:
                        continue
                    
                    # Find heavy braking zones (brake pressure > 80%)
                    heavy_braking = brake_data[brake_data > 80]
                    
                    # Calculate braking variability
                    braking_events = self.identify_braking_events(brake_data)
                    
                    lap_braking_stress = {
                        'lap_number': int(lap['LapNumber']),
                        'heavy_braking_zones': len(heavy_braking),
                        'braking_events': len(braking_events),
                        'max_brake_pressure': float(brake_data.max()),
                        'avg_brake_pressure': float(brake_data.mean()),
                        'braking_variability': float(brake_data.std())
                    }
                    
                    braking_stress_data.append(lap_braking_stress)
                    
                except Exception as lap_error:
                    continue
            
            if not braking_stress_data:
                return {'error': 'No braking telemetry data available'}
            
            # Aggregate braking stress analysis
            avg_variability = np.mean([data['braking_variability'] for data in braking_stress_data])
            max_pressure_std = np.std([data['max_brake_pressure'] for data in braking_stress_data])
            
            return {
                'lap_by_lap_analysis': braking_stress_data,
                'overall_braking_stress': float(min(100, (avg_variability + max_pressure_std) * 2)),
                'braking_consistency_rating': self.rate_braking_consistency(avg_variability),
                'high_stress_laps': [data for data in braking_stress_data if data['braking_variability'] > avg_variability + max_pressure_std]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_cornering_stress(self, driver_laps):
        """Analyze stress related to cornering performance"""
        try:
            cornering_data = []
            
            for _, lap in driver_laps.iterrows():
                try:
                    telemetry = self.data_loader.get_telemetry_data(lap)
                    if telemetry is None or telemetry.empty:
                        continue
                    
                    # Analyze speed variance in corners (low speed sections)
                    speed_data = telemetry['Speed']
                    if speed_data.empty:
                        continue
                    
                    # Identify cornering zones (speed < 200 km/h)
                    cornering_zones = speed_data[speed_data < 200]
                    
                    if len(cornering_zones) > 0:
                        cornering_variability = float(cornering_zones.std())
                        min_corner_speed = float(cornering_zones.min())
                        avg_corner_speed = float(cornering_zones.mean())
                        
                        lap_cornering_data = {
                            'lap_number': int(lap['LapNumber']),
                            'cornering_variability': cornering_variability,
                            'min_corner_speed': min_corner_speed,
                            'avg_corner_speed': avg_corner_speed,
                            'cornering_consistency': float(cornering_variability / avg_corner_speed if avg_corner_speed > 0 else 0)
                        }
                        
                        cornering_data.append(lap_cornering_data)
                
                except Exception as lap_error:
                    continue
            
            if not cornering_data:
                return {'error': 'No cornering telemetry data available'}
            
            # Aggregate analysis
            avg_consistency = np.mean([data['cornering_consistency'] for data in cornering_data])
            
            return {
                'lap_by_lap_analysis': cornering_data,
                'overall_cornering_stress': float(min(100, avg_consistency * 100)),
                'cornering_rating': self.rate_cornering_consistency(avg_consistency),
                'most_challenging_laps': sorted(cornering_data, key=lambda x: x['cornering_variability'], reverse=True)[:3]
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def identify_pressure_moments(self, driver_laps):
        """Identify high-pressure moments during the session"""
        try:
            pressure_moments = []
            
            # Analyze position changes
            positions = driver_laps['Position'].dropna()
            if len(positions) > 1:
                for i in range(1, len(positions)):
                    position_change = positions.iloc[i] - positions.iloc[i-1]
                    if abs(position_change) >= 2:  # Significant position change
                        pressure_moments.append({
                            'lap_number': int(driver_laps.iloc[i]['LapNumber']),
                            'type': 'position_change',
                            'severity': 'high' if abs(position_change) >= 3 else 'moderate',
                            'description': f"Position change: {position_change:+d}",
                            'position_before': int(positions.iloc[i-1]),
                            'position_after': int(positions.iloc[i])
                        })
            
            # Analyze lap time spikes
            lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
            if len(lap_times) > 2:
                mean_time = np.mean(lap_times)
                std_time = np.std(lap_times)
                
                for i, lap_time in enumerate(lap_times):
                    if lap_time > mean_time + 2 * std_time:
                        pressure_moments.append({
                            'lap_number': i + 1,
                            'type': 'lap_time_spike',
                            'severity': 'high' if lap_time > mean_time + 3 * std_time else 'moderate',
                            'description': f"Slow lap: +{lap_time - mean_time:.3f}s",
                            'lap_time': lap_time,
                            'deviation': lap_time - mean_time
                        })
            
            # Sort by lap number
            pressure_moments.sort(key=lambda x: x['lap_number'])
            
            return {
                'total_pressure_moments': len(pressure_moments),
                'high_severity_count': len([pm for pm in pressure_moments if pm['severity'] == 'high']),
                'pressure_moments': pressure_moments,
                'pressure_density': len(pressure_moments) / len(driver_laps) if len(driver_laps) > 0 else 0
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_stress_trends(self, driver_laps):
        """Analyze how stress levels change throughout the session"""
        try:
            if len(driver_laps) < 5:
                return {'error': 'Insufficient data for trend analysis'}
            
            # Divide session into segments
            num_segments = min(5, len(driver_laps) // 3)
            segment_size = len(driver_laps) // num_segments
            
            segment_stress = []
            
            for i in range(num_segments):
                start_idx = i * segment_size
                end_idx = (i + 1) * segment_size if i < num_segments - 1 else len(driver_laps)
                
                segment_laps = driver_laps.iloc[start_idx:end_idx]
                segment_lap_times = [lt.total_seconds() for lt in segment_laps['LapTime'].dropna()]
                
                if len(segment_lap_times) > 1:
                    segment_consistency = np.std(segment_lap_times) / np.mean(segment_lap_times)
                    segment_stress.append({
                        'segment': i + 1,
                        'laps': f"{start_idx + 1}-{end_idx}",
                        'consistency': float(segment_consistency),
                        'stress_level': float(min(100, segment_consistency * 200)),
                        'avg_lap_time': float(np.mean(segment_lap_times))
                    })
            
            if not segment_stress:
                return {'error': 'Unable to calculate stress trends'}
            
            # Calculate trend direction
            stress_levels = [seg['stress_level'] for seg in segment_stress]
            trend_slope = np.polyfit(range(len(stress_levels)), stress_levels, 1)[0]
            
            return {
                'segment_analysis': segment_stress,
                'trend_direction': 'increasing' if trend_slope > 1 else 'decreasing' if trend_slope < -1 else 'stable',
                'trend_slope': float(trend_slope),
                'highest_stress_segment': max(segment_stress, key=lambda x: x['stress_level']),
                'lowest_stress_segment': min(segment_stress, key=lambda x: x['stress_level'])
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def compare_with_session_average(self, driver_laps, session_data):
        """Compare driver's stress levels with session average"""
        try:
            # Calculate session-wide statistics
            all_lap_times = []
            for driver in session_data.drivers:
                other_driver_laps = session_data.laps.pick_driver(driver)
                if not other_driver_laps.empty:
                    driver_times = [lt.total_seconds() for lt in other_driver_laps['LapTime'].dropna()]
                    all_lap_times.extend(driver_times)
            
            if not all_lap_times:
                return {'error': 'No session data available for comparison'}
            
            session_consistency = np.std(all_lap_times) / np.mean(all_lap_times)
            
            # Driver consistency
            driver_lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
            if not driver_lap_times:
                return {'error': 'No driver lap times available'}
            
            driver_consistency = np.std(driver_lap_times) / np.mean(driver_lap_times)
            
            return {
                'driver_consistency': float(driver_consistency),
                'session_avg_consistency': float(session_consistency),
                'relative_stress': float(driver_consistency / session_consistency if session_consistency > 0 else 1),
                'comparison': 'above_average' if driver_consistency > session_consistency else 'below_average',
                'percentile_rank': self.calculate_consistency_percentile(driver_consistency, session_data)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def rate_stress_level(self, stress_index):
        """Rate stress level based on index"""
        if stress_index < 20:
            return 'very_low'
        elif stress_index < 40:
            return 'low'
        elif stress_index < 60:
            return 'moderate'
        elif stress_index < 80:
            return 'high'
        else:
            return 'very_high'
    
    def rate_sector_consistency(self, cv):
        """Rate sector consistency based on coefficient of variation"""
        if cv < 0.02:
            return 'excellent'
        elif cv < 0.04:
            return 'good'
        elif cv < 0.06:
            return 'average'
        else:
            return 'poor'
    
    def rate_consistency(self, cv):
        """Rate overall consistency"""
        if cv < 0.01:
            return 'excellent'
        elif cv < 0.02:
            return 'good'
        elif cv < 0.04:
            return 'average'
        else:
            return 'poor'
    
    def rate_braking_consistency(self, variability):
        """Rate braking consistency"""
        if variability < 5:
            return 'excellent'
        elif variability < 10:
            return 'good'
        elif variability < 20:
            return 'average'
        else:
            return 'poor'
    
    def rate_cornering_consistency(self, consistency_ratio):
        """Rate cornering consistency"""
        if consistency_ratio < 0.1:
            return 'excellent'
        elif consistency_ratio < 0.2:
            return 'good'
        elif consistency_ratio < 0.3:
            return 'average'
        else:
            return 'poor'
    
    def identify_outlier_sectors(self, sector_times):
        """Identify outlier sector times"""
        try:
            if len(sector_times) < 3:
                return []
            
            q1 = np.percentile(sector_times, 25)
            q3 = np.percentile(sector_times, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = []
            for i, time in enumerate(sector_times):
                if time < lower_bound or time > upper_bound:
                    outliers.append({'index': i, 'time': time, 'type': 'fast' if time < lower_bound else 'slow'})
            
            return outliers
            
        except Exception as e:
            return []
    
    def identify_braking_events(self, brake_data):
        """Identify distinct braking events"""
        try:
            events = []
            in_braking = False
            current_event = None
            
            for i, brake_pressure in enumerate(brake_data):
                if brake_pressure > 10 and not in_braking:  # Start of braking event
                    in_braking = True
                    current_event = {'start': i, 'max_pressure': brake_pressure}
                elif brake_pressure <= 10 and in_braking:  # End of braking event
                    in_braking = False
                    if current_event:
                        current_event['end'] = i
                        current_event['duration'] = i - current_event['start']
                        events.append(current_event)
                elif in_braking and brake_pressure > current_event['max_pressure']:
                    current_event['max_pressure'] = brake_pressure
            
            return events
            
        except Exception as e:
            return []
    
    def find_most_consistent_period(self, lap_times):
        """Find the most consistent period of laps"""
        try:
            if len(lap_times) < 5:
                return None
            
            min_std = float('inf')
            best_period = None
            window_size = min(5, len(lap_times) // 2)
            
            for i in range(len(lap_times) - window_size + 1):
                window = lap_times[i:i + window_size]
                std = np.std(window)
                
                if std < min_std:
                    min_std = std
                    best_period = {
                        'start_lap': i + 1,
                        'end_lap': i + window_size,
                        'consistency': float(std / np.mean(window)),
                        'avg_lap_time': float(np.mean(window))
                    }
            
            return best_period
            
        except Exception as e:
            return None
    
    def find_least_consistent_period(self, lap_times):
        """Find the least consistent period of laps"""
        try:
            if len(lap_times) < 5:
                return None
            
            max_std = 0
            worst_period = None
            window_size = min(5, len(lap_times) // 2)
            
            for i in range(len(lap_times) - window_size + 1):
                window = lap_times[i:i + window_size]
                std = np.std(window)
                
                if std > max_std:
                    max_std = std
                    worst_period = {
                        'start_lap': i + 1,
                        'end_lap': i + window_size,
                        'consistency': float(std / np.mean(window)),
                        'avg_lap_time': float(np.mean(window))
                    }
            
            return worst_period
            
        except Exception as e:
            return None
    
    def calculate_consistency_percentile(self, driver_consistency, session_data):
        """Calculate driver's consistency percentile compared to all drivers"""
        try:
            all_consistencies = []
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if not driver_laps.empty:
                    lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
                    if len(lap_times) > 1:
                        consistency = np.std(lap_times) / np.mean(lap_times)
                        all_consistencies.append(consistency)
            
            if not all_consistencies:
                return 50  # Default to 50th percentile
            
            # Lower consistency is better, so we need to reverse the percentile
            percentile = (1 - (sorted(all_consistencies).index(driver_consistency) / len(all_consistencies))) * 100
            return float(percentile)
            
        except Exception as e:
            return 50
