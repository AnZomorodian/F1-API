import pandas as pd
import numpy as np
from utils.data_loader import DataLoader

class BrakeAnalyzer:
    """Analyze braking performance and characteristics"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def analyze_braking_performance(self, year, grand_prix, session, driver):
        """Comprehensive braking performance analysis"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return None
            
            driver_laps = self.data_loader.get_driver_laps(session_data, driver)
            if driver_laps is None or driver_laps.empty:
                return {'error': f'No data found for driver {driver}'}
            
            analysis = {
                'braking_zones_analysis': self.analyze_braking_zones(driver_laps),
                'brake_pressure_analysis': self.analyze_brake_pressure(driver_laps),
                'braking_consistency': self.analyze_braking_consistency(driver_laps),
                'brake_temperature_analysis': self.analyze_brake_temperatures(driver_laps),
                'braking_efficiency': self.calculate_braking_efficiency(driver_laps),
                'brake_balance_analysis': self.analyze_brake_balance(driver_laps),
                'comparative_analysis': self.compare_with_session_average(driver_laps, session_data),
                'braking_recommendations': self.generate_braking_recommendations(driver_laps)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_braking_zones(self, driver_laps):
        """Analyze braking zones throughout the lap"""
        try:
            braking_zones_data = []
            
            for _, lap in driver_laps.iterrows():
                try:
                    telemetry = self.data_loader.get_telemetry_data(lap)
                    if telemetry is None or telemetry.empty:
                        continue
                    
                    brake_data = telemetry['Brake'] if 'Brake' in telemetry.columns else None
                    if brake_data is None or brake_data.empty:
                        continue
                    
                    # Identify braking zones
                    braking_zones = self.identify_braking_zones(telemetry)
                    
                    lap_braking_data = {
                        'lap_number': int(lap['LapNumber']),
                        'total_braking_zones': len(braking_zones),
                        'braking_zones': braking_zones,
                        'total_braking_time': self.calculate_total_braking_time(braking_zones),
                        'average_brake_pressure': float(brake_data.mean()),
                        'max_brake_pressure': float(brake_data.max())
                    }
                    
                    braking_zones_data.append(lap_braking_data)
                    
                except Exception as lap_error:
                    continue
            
            if not braking_zones_data:
                return {'error': 'No braking telemetry data available'}
            
            # Aggregate analysis
            return {
                'lap_by_lap_analysis': braking_zones_data,
                'average_braking_zones_per_lap': float(np.mean([data['total_braking_zones'] for data in braking_zones_data])),
                'consistency_rating': self.rate_braking_zone_consistency(braking_zones_data),
                'total_laps_analyzed': len(braking_zones_data)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_brake_pressure(self, driver_laps):
        """Analyze brake pressure patterns"""
        try:
            pressure_data = []
            
            for _, lap in driver_laps.iterrows():
                try:
                    telemetry = self.data_loader.get_telemetry_data(lap)
                    if telemetry is None or telemetry.empty:
                        continue
                    
                    brake_data = telemetry['Brake'] if 'Brake' in telemetry.columns else None
                    if brake_data is None or brake_data.empty:
                        continue
                    
                    # Analyze pressure characteristics
                    pressure_analysis = {
                        'lap_number': int(lap['LapNumber']),
                        'max_pressure': float(brake_data.max()),
                        'avg_pressure': float(brake_data.mean()),
                        'pressure_variance': float(brake_data.var()),
                        'pressure_range': float(brake_data.max() - brake_data.min()),
                        'heavy_braking_events': len(brake_data[brake_data > 80]),
                        'moderate_braking_events': len(brake_data[(brake_data > 30) & (brake_data <= 80)]),
                        'light_braking_events': len(brake_data[(brake_data > 0) & (brake_data <= 30)])
                    }
                    
                    pressure_data.append(pressure_analysis)
                    
                except Exception as lap_error:
                    continue
            
            if not pressure_data:
                return {'error': 'No brake pressure data available'}
            
            # Statistical analysis
            max_pressures = [data['max_pressure'] for data in pressure_data]
            avg_pressures = [data['avg_pressure'] for data in pressure_data]
            
            return {
                'lap_by_lap_analysis': pressure_data,
                'overall_statistics': {
                    'session_max_pressure': float(max(max_pressures)),
                    'session_avg_pressure': float(np.mean(avg_pressures)),
                    'pressure_consistency': float(np.std(max_pressures)),
                    'total_heavy_braking': sum([data['heavy_braking_events'] for data in pressure_data])
                },
                'pressure_rating': self.rate_brake_pressure_performance(max_pressures, avg_pressures)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_braking_consistency(self, driver_laps):
        """Analyze consistency of braking performance"""
        try:
            consistency_metrics = []
            
            for _, lap in driver_laps.iterrows():
                try:
                    telemetry = self.data_loader.get_telemetry_data(lap)
                    if telemetry is None or telemetry.empty:
                        continue
                    
                    brake_data = telemetry['Brake'] if 'Brake' in telemetry.columns else None
                    speed_data = telemetry['Speed'] if 'Speed' in telemetry.columns else None
                    
                    if brake_data is None or speed_data is None:
                        continue
                    
                    # Calculate braking consistency metrics
                    braking_events = self.identify_braking_events(brake_data)
                    
                    if braking_events:
                        consistency_score = self.calculate_braking_consistency_score(braking_events)
                        
                        consistency_metrics.append({
                            'lap_number': int(lap['LapNumber']),
                            'consistency_score': consistency_score,
                            'braking_events_count': len(braking_events),
                            'avg_braking_intensity': float(np.mean([event['max_pressure'] for event in braking_events]))
                        })
                    
                except Exception as lap_error:
                    continue
            
            if not consistency_metrics:
                return {'error': 'Insufficient data for consistency analysis'}
            
            # Overall consistency analysis
            consistency_scores = [metric['consistency_score'] for metric in consistency_metrics]
            
            return {
                'lap_by_lap_metrics': consistency_metrics,
                'overall_consistency': {
                    'average_consistency_score': float(np.mean(consistency_scores)),
                    'consistency_variance': float(np.var(consistency_scores)),
                    'most_consistent_lap': max(consistency_metrics, key=lambda x: x['consistency_score']),
                    'least_consistent_lap': min(consistency_metrics, key=lambda x: x['consistency_score'])
                },
                'consistency_rating': self.rate_overall_consistency(consistency_scores),
                'consistency_trend': self.analyze_consistency_trend(consistency_scores)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_brake_temperatures(self, driver_laps):
        """Analyze brake temperature patterns (if available in telemetry)"""
        try:
            # Note: Brake temperature data is often not available in public F1 telemetry
            # This is a framework for when such data becomes available
            
            temperature_analysis = {
                'data_availability': 'limited',
                'analysis_method': 'inferred_from_usage',
                'estimated_temperatures': self.estimate_brake_temperatures(driver_laps),
                'thermal_management_rating': self.rate_thermal_management(driver_laps)
            }
            
            return temperature_analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_braking_efficiency(self, driver_laps):
        """Calculate braking efficiency metrics"""
        try:
            efficiency_data = []
            
            for _, lap in driver_laps.iterrows():
                try:
                    telemetry = self.data_loader.get_telemetry_data(lap)
                    if telemetry is None or telemetry.empty:
                        continue
                    
                    brake_data = telemetry['Brake'] if 'Brake' in telemetry.columns else None
                    speed_data = telemetry['Speed'] if 'Speed' in telemetry.columns else None
                    
                    if brake_data is None or speed_data is None:
                        continue
                    
                    # Calculate braking efficiency
                    efficiency_metrics = self.calculate_lap_braking_efficiency(brake_data, speed_data)
                    
                    if efficiency_metrics:
                        efficiency_data.append({
                            'lap_number': int(lap['LapNumber']),
                            'braking_efficiency': efficiency_metrics['efficiency'],
                            'energy_dissipation': efficiency_metrics['energy_dissipation'],
                            'braking_distance_optimization': efficiency_metrics['distance_optimization']
                        })
                    
                except Exception as lap_error:
                    continue
            
            if not efficiency_data:
                return {'error': 'Unable to calculate braking efficiency'}
            
            # Overall efficiency analysis
            efficiencies = [data['braking_efficiency'] for data in efficiency_data]
            
            return {
                'lap_by_lap_efficiency': efficiency_data,
                'overall_efficiency': {
                    'average_efficiency': float(np.mean(efficiencies)),
                    'efficiency_consistency': float(np.std(efficiencies)),
                    'best_efficiency_lap': max(efficiency_data, key=lambda x: x['braking_efficiency']),
                    'efficiency_trend': self.analyze_efficiency_trend(efficiencies)
                },
                'efficiency_rating': self.rate_braking_efficiency(efficiencies)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_brake_balance(self, driver_laps):
        """Analyze brake balance characteristics"""
        try:
            # Brake balance analysis is typically inferred from speed and braking patterns
            # as direct brake balance data is usually not available in public telemetry
            
            balance_data = []
            
            for _, lap in driver_laps.iterrows():
                try:
                    telemetry = self.data_loader.get_telemetry_data(lap)
                    if telemetry is None or telemetry.empty:
                        continue
                    
                    brake_data = telemetry['Brake'] if 'Brake' in telemetry.columns else None
                    speed_data = telemetry['Speed'] if 'Speed' in telemetry.columns else None
                    
                    if brake_data is None or speed_data is None:
                        continue
                    
                    # Infer brake balance from braking patterns
                    balance_metrics = self.infer_brake_balance(brake_data, speed_data)
                    
                    if balance_metrics:
                        balance_data.append({
                            'lap_number': int(lap['LapNumber']),
                            'balance_score': balance_metrics['balance_score'],
                            'front_bias_indicator': balance_metrics['front_bias'],
                            'rear_bias_indicator': balance_metrics['rear_bias'],
                            'stability_rating': balance_metrics['stability']
                        })
                    
                except Exception as lap_error:
                    continue
            
            if not balance_data:
                return {'error': 'Unable to analyze brake balance'}
            
            # Overall balance analysis
            balance_scores = [data['balance_score'] for data in balance_data]
            
            return {
                'lap_by_lap_balance': balance_data,
                'overall_balance': {
                    'average_balance_score': float(np.mean(balance_scores)),
                    'balance_consistency': float(np.std(balance_scores)),
                    'optimal_balance_lap': self.find_optimal_balance_lap(balance_data)
                },
                'balance_rating': self.rate_brake_balance(balance_scores),
                'balance_recommendations': self.generate_balance_recommendations(balance_data)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def compare_with_session_average(self, driver_laps, session_data):
        """Compare driver's braking with session average"""
        try:
            # Calculate session-wide braking statistics
            session_braking_data = []
            
            for driver in session_data.drivers:
                try:
                    other_driver_laps = session_data.laps.pick_driver(driver)
                    if not other_driver_laps.empty:
                        driver_braking_stats = self.calculate_driver_braking_stats(other_driver_laps)
                        if driver_braking_stats:
                            session_braking_data.append(driver_braking_stats)
                except Exception as driver_error:
                    continue
            
            if not session_braking_data:
                return {'error': 'No session data available for comparison'}
            
            # Calculate session averages
            session_avg_max_pressure = np.mean([data['avg_max_pressure'] for data in session_braking_data])
            session_avg_consistency = np.mean([data['consistency_score'] for data in session_braking_data])
            
            # Driver's statistics
            driver_stats = self.calculate_driver_braking_stats(driver_laps)
            
            if not driver_stats:
                return {'error': 'Unable to calculate driver statistics'}
            
            return {
                'driver_stats': driver_stats,
                'session_averages': {
                    'avg_max_pressure': float(session_avg_max_pressure),
                    'avg_consistency': float(session_avg_consistency)
                },
                'relative_performance': {
                    'pressure_vs_average': float(driver_stats['avg_max_pressure'] / session_avg_max_pressure),
                    'consistency_vs_average': float(driver_stats['consistency_score'] / session_avg_consistency),
                    'percentile_rank': self.calculate_braking_percentile(driver_stats, session_braking_data)
                },
                'comparison_rating': self.rate_comparative_performance(driver_stats, session_braking_data)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_braking_recommendations(self, driver_laps):
        """Generate braking performance recommendations"""
        try:
            recommendations = []
            
            # Analyze braking patterns to generate recommendations
            braking_analysis = self.analyze_braking_zones(driver_laps)
            pressure_analysis = self.analyze_brake_pressure(driver_laps)
            consistency_analysis = self.analyze_braking_consistency(driver_laps)
            
            # Generate specific recommendations based on analysis
            if isinstance(braking_analysis, dict) and 'lap_by_lap_analysis' in braking_analysis:
                avg_zones = braking_analysis.get('average_braking_zones_per_lap', 0)
                if avg_zones > 15:
                    recommendations.append({
                        'category': 'braking_zones',
                        'recommendation': 'Consider optimizing braking points - high number of braking zones detected',
                        'priority': 'medium',
                        'technical_detail': f'Average {avg_zones:.1f} braking zones per lap'
                    })
            
            if isinstance(pressure_analysis, dict) and 'overall_statistics' in pressure_analysis:
                consistency = pressure_analysis['overall_statistics'].get('pressure_consistency', 0)
                if consistency > 20:
                    recommendations.append({
                        'category': 'consistency',
                        'recommendation': 'Focus on more consistent brake pressure application',
                        'priority': 'high',
                        'technical_detail': f'Pressure consistency variance: {consistency:.1f}'
                    })
            
            if isinstance(consistency_analysis, dict) and 'overall_consistency' in consistency_analysis:
                avg_consistency = consistency_analysis['overall_consistency'].get('average_consistency_score', 0)
                if avg_consistency < 0.7:
                    recommendations.append({
                        'category': 'technique',
                        'recommendation': 'Work on braking technique consistency across laps',
                        'priority': 'high',
                        'technical_detail': f'Consistency score: {avg_consistency:.2f}'
                    })
            
            # Add general recommendations
            recommendations.append({
                'category': 'general',
                'recommendation': 'Continue monitoring brake temperatures to prevent overheating',
                'priority': 'low',
                'technical_detail': 'Thermal management is crucial for consistent performance'
            })
            
            return {
                'recommendations': recommendations,
                'total_recommendations': len(recommendations),
                'priority_breakdown': {
                    'high': len([r for r in recommendations if r['priority'] == 'high']),
                    'medium': len([r for r in recommendations if r['priority'] == 'medium']),
                    'low': len([r for r in recommendations if r['priority'] == 'low'])
                }
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    # Helper methods
    def identify_braking_zones(self, telemetry):
        """Identify distinct braking zones from telemetry"""
        try:
            brake_data = telemetry['Brake']
            speed_data = telemetry['Speed']
            distance_data = telemetry['Distance']
            
            braking_zones = []
            in_braking_zone = False
            zone_start = None
            zone_data = []
            
            for i, (brake_pressure, speed, distance) in enumerate(zip(brake_data, speed_data, distance_data)):
                if brake_pressure > 10 and not in_braking_zone:  # Start of braking zone
                    in_braking_zone = True
                    zone_start = i
                    zone_data = [(brake_pressure, speed, distance)]
                elif brake_pressure > 10 and in_braking_zone:  # Continue braking zone
                    zone_data.append((brake_pressure, speed, distance))
                elif brake_pressure <= 10 and in_braking_zone:  # End of braking zone
                    in_braking_zone = False
                    
                    if zone_data:
                        zone_analysis = {
                            'start_index': zone_start,
                            'end_index': i,
                            'duration': i - zone_start,
                            'max_pressure': max([bp for bp, _, _ in zone_data]),
                            'avg_pressure': np.mean([bp for bp, _, _ in zone_data]),
                            'speed_reduction': zone_data[0][1] - zone_data[-1][1] if zone_data else 0,
                            'braking_distance': zone_data[-1][2] - zone_data[0][2] if zone_data else 0
                        }
                        braking_zones.append(zone_analysis)
                    
                    zone_data = []
            
            return braking_zones
            
        except Exception as e:
            return []
    
    def calculate_total_braking_time(self, braking_zones):
        """Calculate total braking time from braking zones"""
        try:
            total_duration = sum([zone['duration'] for zone in braking_zones])
            return float(total_duration * 0.02)  # Assuming 50Hz data (0.02s per sample)
        except Exception as e:
            return 0.0
    
    def rate_braking_zone_consistency(self, braking_zones_data):
        """Rate consistency of braking zones across laps"""
        try:
            zone_counts = [data['total_braking_zones'] for data in braking_zones_data]
            if not zone_counts:
                return 'unknown'
            
            consistency = np.std(zone_counts) / np.mean(zone_counts) if np.mean(zone_counts) > 0 else 1
            
            if consistency < 0.1:
                return 'excellent'
            elif consistency < 0.2:
                return 'good'
            elif consistency < 0.3:
                return 'average'
            else:
                return 'poor'
                
        except Exception as e:
            return 'unknown'
    
    def rate_brake_pressure_performance(self, max_pressures, avg_pressures):
        """Rate brake pressure performance"""
        try:
            pressure_consistency = np.std(max_pressures) / np.mean(max_pressures) if np.mean(max_pressures) > 0 else 1
            avg_max_pressure = np.mean(max_pressures)
            
            # Rate based on consistency and appropriate pressure levels
            if pressure_consistency < 0.1 and 70 <= avg_max_pressure <= 100:
                return 'excellent'
            elif pressure_consistency < 0.2 and 60 <= avg_max_pressure <= 100:
                return 'good'
            elif pressure_consistency < 0.3:
                return 'average'
            else:
                return 'needs_improvement'
                
        except Exception as e:
            return 'unknown'
    
    def identify_braking_events(self, brake_data):
        """Identify individual braking events"""
        try:
            events = []
            in_event = False
            event_start = None
            event_pressures = []
            
            for i, pressure in enumerate(brake_data):
                if pressure > 20 and not in_event:  # Start of braking event
                    in_event = True
                    event_start = i
                    event_pressures = [pressure]
                elif pressure > 20 and in_event:  # Continue event
                    event_pressures.append(pressure)
                elif pressure <= 20 and in_event:  # End of event
                    in_event = False
                    
                    if event_pressures:
                        event = {
                            'start_index': event_start,
                            'end_index': i,
                            'duration': i - event_start,
                            'max_pressure': max(event_pressures),
                            'avg_pressure': np.mean(event_pressures),
                            'pressure_buildup_rate': self.calculate_pressure_buildup_rate(event_pressures)
                        }
                        events.append(event)
                    
                    event_pressures = []
            
            return events
            
        except Exception as e:
            return []
    
    def calculate_pressure_buildup_rate(self, pressures):
        """Calculate how quickly brake pressure builds up"""
        try:
            if len(pressures) < 2:
                return 0
            
            max_pressure = max(pressures)
            buildup_index = pressures.index(max_pressure)
            
            if buildup_index == 0:
                return float('inf')  # Instant buildup
            
            return float(max_pressure / buildup_index)  # Pressure per time step
            
        except Exception as e:
            return 0
    
    def calculate_braking_consistency_score(self, braking_events):
        """Calculate consistency score for braking events"""
        try:
            if not braking_events:
                return 0
            
            max_pressures = [event['max_pressure'] for event in braking_events]
            durations = [event['duration'] for event in braking_events]
            
            pressure_consistency = 1 - (np.std(max_pressures) / np.mean(max_pressures)) if np.mean(max_pressures) > 0 else 0
            duration_consistency = 1 - (np.std(durations) / np.mean(durations)) if np.mean(durations) > 0 else 0
            
            return float((pressure_consistency + duration_consistency) / 2)
            
        except Exception as e:
            return 0
    
    def rate_overall_consistency(self, consistency_scores):
        """Rate overall braking consistency"""
        try:
            avg_consistency = np.mean(consistency_scores)
            
            if avg_consistency > 0.8:
                return 'excellent'
            elif avg_consistency > 0.7:
                return 'good'
            elif avg_consistency > 0.6:
                return 'average'
            else:
                return 'needs_improvement'
                
        except Exception as e:
            return 'unknown'
    
    def analyze_consistency_trend(self, consistency_scores):
        """Analyze trend in consistency over the session"""
        try:
            if len(consistency_scores) < 3:
                return 'insufficient_data'
            
            # Simple linear trend analysis
            x = np.arange(len(consistency_scores))
            slope = np.polyfit(x, consistency_scores, 1)[0]
            
            if slope > 0.01:
                return 'improving'
            elif slope < -0.01:
                return 'declining'
            else:
                return 'stable'
                
        except Exception as e:
            return 'unknown'
    
    def estimate_brake_temperatures(self, driver_laps):
        """Estimate brake temperatures based on usage patterns"""
        try:
            # This is a simplified estimation method
            temperature_estimates = []
            
            for _, lap in driver_laps.iterrows():
                try:
                    telemetry = self.data_loader.get_telemetry_data(lap)
                    if telemetry is None or telemetry.empty:
                        continue
                    
                    brake_data = telemetry['Brake'] if 'Brake' in telemetry.columns else None
                    if brake_data is None:
                        continue
                    
                    # Simplified temperature estimation
                    heavy_braking_time = len(brake_data[brake_data > 70])
                    moderate_braking_time = len(brake_data[(brake_data > 30) & (brake_data <= 70)])
                    
                    # Estimate temperature based on braking intensity and duration
                    estimated_temp = 200 + (heavy_braking_time * 2) + (moderate_braking_time * 0.5)
                    
                    temperature_estimates.append({
                        'lap_number': int(lap['LapNumber']),
                        'estimated_temperature': float(min(800, estimated_temp))  # Cap at reasonable maximum
                    })
                    
                except Exception as lap_error:
                    continue
            
            return temperature_estimates
            
        except Exception as e:
            return []
    
    def rate_thermal_management(self, driver_laps):
        """Rate thermal management based on braking patterns"""
        try:
            # Analyze braking patterns for thermal management
            thermal_load_indicators = []
            
            for _, lap in driver_laps.iterrows():
                try:
                    telemetry = self.data_loader.get_telemetry_data(lap)
                    if telemetry is None or telemetry.empty:
                        continue
                    
                    brake_data = telemetry['Brake'] if 'Brake' in telemetry.columns else None
                    if brake_data is None:
                        continue
                    
                    # Calculate thermal load indicator
                    heavy_braking_ratio = len(brake_data[brake_data > 80]) / len(brake_data)
                    continuous_braking = self.detect_continuous_braking(brake_data)
                    
                    thermal_load = heavy_braking_ratio * 0.7 + continuous_braking * 0.3
                    thermal_load_indicators.append(thermal_load)
                    
                except Exception as lap_error:
                    continue
            
            if not thermal_load_indicators:
                return 'unknown'
            
            avg_thermal_load = np.mean(thermal_load_indicators)
            
            if avg_thermal_load < 0.2:
                return 'excellent'
            elif avg_thermal_load < 0.4:
                return 'good'
            elif avg_thermal_load < 0.6:
                return 'average'
            else:
                return 'concerning'
                
        except Exception as e:
            return 'unknown'
    
    def detect_continuous_braking(self, brake_data):
        """Detect periods of continuous braking that could cause overheating"""
        try:
            continuous_periods = 0
            current_period = 0
            
            for pressure in brake_data:
                if pressure > 30:  # Moderate to heavy braking
                    current_period += 1
                else:
                    if current_period > 10:  # Long period of continuous braking
                        continuous_periods += 1
                    current_period = 0
            
            return float(continuous_periods / len(brake_data) * 100)  # Percentage of lap in continuous braking
            
        except Exception as e:
            return 0
    
    def calculate_lap_braking_efficiency(self, brake_data, speed_data):
        """Calculate braking efficiency for a single lap"""
        try:
            braking_events = self.identify_braking_events(brake_data)
            if not braking_events:
                return None
            
            # Calculate efficiency metrics
            total_speed_reduction = 0
            total_brake_energy = 0
            
            for event in braking_events:
                start_idx = event['start_index']
                end_idx = event['end_index']
                
                if start_idx < len(speed_data) and end_idx < len(speed_data):
                    speed_reduction = speed_data.iloc[start_idx] - speed_data.iloc[end_idx]
                    brake_energy = event['avg_pressure'] * event['duration']
                    
                    total_speed_reduction += max(0, speed_reduction)
                    total_brake_energy += brake_energy
            
            efficiency = total_speed_reduction / total_brake_energy if total_brake_energy > 0 else 0
            
            return {
                'efficiency': float(efficiency),
                'energy_dissipation': float(total_brake_energy),
                'distance_optimization': self.calculate_braking_distance_optimization(braking_events)
            }
            
        except Exception as e:
            return None
    
    def calculate_braking_distance_optimization(self, braking_events):
        """Calculate how well braking distances are optimized"""
        try:
            if not braking_events:
                return 0
            
            # Analyze consistency of braking distances
            distances = [event.get('braking_distance', 0) for event in braking_events]
            distances = [d for d in distances if d > 0]  # Filter out invalid distances
            
            if not distances:
                return 0
            
            distance_consistency = 1 - (np.std(distances) / np.mean(distances)) if np.mean(distances) > 0 else 0
            return float(max(0, distance_consistency))
            
        except Exception as e:
            return 0
    
    def analyze_efficiency_trend(self, efficiencies):
        """Analyze trend in braking efficiency"""
        try:
            if len(efficiencies) < 3:
                return 'insufficient_data'
            
            # Linear trend analysis
            x = np.arange(len(efficiencies))
            slope = np.polyfit(x, efficiencies, 1)[0]
            
            if slope > 0.001:
                return 'improving'
            elif slope < -0.001:
                return 'declining'
            else:
                return 'stable'
                
        except Exception as e:
            return 'unknown'
    
    def rate_braking_efficiency(self, efficiencies):
        """Rate overall braking efficiency"""
        try:
            avg_efficiency = np.mean(efficiencies)
            
            if avg_efficiency > 0.8:
                return 'excellent'
            elif avg_efficiency > 0.6:
                return 'good'
            elif avg_efficiency > 0.4:
                return 'average'
            else:
                return 'needs_improvement'
                
        except Exception as e:
            return 'unknown'
    
    def infer_brake_balance(self, brake_data, speed_data):
        """Infer brake balance from braking patterns"""
        try:
            # This is a simplified inference method
            # Real brake balance analysis would require front/rear specific data
            
            braking_events = self.identify_braking_events(brake_data)
            if not braking_events:
                return None
            
            # Analyze braking characteristics to infer balance
            pressure_buildups = [event['pressure_buildup_rate'] for event in braking_events]
            avg_buildup = np.mean(pressure_buildups)
            
            # Simplified balance inference
            if avg_buildup > 10:  # Quick pressure buildup
                balance_score = 0.6  # Slightly rear-biased (simplified assumption)
                front_bias = 0.4
                rear_bias = 0.6
                stability = 'moderate'
            elif avg_buildup < 5:  # Gradual pressure buildup
                balance_score = 0.4  # Slightly front-biased
                front_bias = 0.6
                rear_bias = 0.4
                stability = 'good'
            else:  # Balanced buildup
                balance_score = 0.5  # Balanced
                front_bias = 0.5
                rear_bias = 0.5
                stability = 'excellent'
            
            return {
                'balance_score': float(balance_score),
                'front_bias': float(front_bias),
                'rear_bias': float(rear_bias),
                'stability': stability
            }
            
        except Exception as e:
            return None
    
    def find_optimal_balance_lap(self, balance_data):
        """Find the lap with the most optimal brake balance"""
        try:
            if not balance_data:
                return None
            
            # Find lap closest to ideal balance (0.5)
            optimal_lap = min(balance_data, key=lambda x: abs(x['balance_score'] - 0.5))
            return optimal_lap
            
        except Exception as e:
            return None
    
    def rate_brake_balance(self, balance_scores):
        """Rate overall brake balance"""
        try:
            # Rate based on how close to ideal balance (0.5) the scores are
            deviations = [abs(score - 0.5) for score in balance_scores]
            avg_deviation = np.mean(deviations)
            
            if avg_deviation < 0.05:
                return 'excellent'
            elif avg_deviation < 0.1:
                return 'good'
            elif avg_deviation < 0.2:
                return 'average'
            else:
                return 'needs_adjustment'
                
        except Exception as e:
            return 'unknown'
    
    def generate_balance_recommendations(self, balance_data):
        """Generate brake balance recommendations"""
        try:
            recommendations = []
            
            if not balance_data:
                return recommendations
            
            balance_scores = [data['balance_score'] for data in balance_data]
            avg_balance = np.mean(balance_scores)
            
            if avg_balance < 0.4:
                recommendations.append("Consider reducing front brake bias for better balance")
            elif avg_balance > 0.6:
                recommendations.append("Consider reducing rear brake bias for better balance")
            else:
                recommendations.append("Brake balance appears well-optimized")
            
            # Check consistency
            balance_consistency = np.std(balance_scores)
            if balance_consistency > 0.1:
                recommendations.append("Work on maintaining consistent brake balance across laps")
            
            return recommendations
            
        except Exception as e:
            return []
    
    def calculate_driver_braking_stats(self, driver_laps):
        """Calculate comprehensive braking statistics for a driver"""
        try:
            all_max_pressures = []
            all_consistencies = []
            
            for _, lap in driver_laps.iterrows():
                try:
                    telemetry = self.data_loader.get_telemetry_data(lap)
                    if telemetry is None or telemetry.empty:
                        continue
                    
                    brake_data = telemetry['Brake'] if 'Brake' in telemetry.columns else None
                    if brake_data is None:
                        continue
                    
                    max_pressure = brake_data.max()
                    braking_events = self.identify_braking_events(brake_data)
                    
                    if braking_events:
                        consistency = self.calculate_braking_consistency_score(braking_events)
                        all_max_pressures.append(max_pressure)
                        all_consistencies.append(consistency)
                
                except Exception as lap_error:
                    continue
            
            if not all_max_pressures:
                return None
            
            return {
                'avg_max_pressure': float(np.mean(all_max_pressures)),
                'consistency_score': float(np.mean(all_consistencies)),
                'pressure_variance': float(np.var(all_max_pressures)),
                'laps_analyzed': len(all_max_pressures)
            }
            
        except Exception as e:
            return None
    
    def calculate_braking_percentile(self, driver_stats, session_data):
        """Calculate driver's percentile rank in braking performance"""
        try:
            consistency_scores = [data['consistency_score'] for data in session_data]
            driver_consistency = driver_stats['consistency_score']
            
            better_count = sum(1 for score in consistency_scores if score < driver_consistency)
            percentile = (better_count / len(consistency_scores)) * 100
            
            return float(percentile)
            
        except Exception as e:
            return 50.0
    
    def rate_comparative_performance(self, driver_stats, session_data):
        """Rate driver's comparative braking performance"""
        try:
            percentile = self.calculate_braking_percentile(driver_stats, session_data)
            
            if percentile >= 80:
                return 'excellent'
            elif percentile >= 60:
                return 'good'
            elif percentile >= 40:
                return 'average'
            else:
                return 'below_average'
                
        except Exception as e:
            return 'unknown'
