import pandas as pd
import numpy as np
from utils.data_loader import DataLoader
from utils.advanced_analytics import AdvancedF1Analytics
from utils.weather_analytics import WeatherAnalytics
from utils.tire_performance import TirePerformanceAnalyzer

class EnhancedF1Analytics:
    """Enhanced F1 analytics combining multiple analysis types"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.advanced_analytics = AdvancedF1Analytics()
        self.weather_analytics = WeatherAnalytics()
        self.tire_analyzer = TirePerformanceAnalyzer()
    
    def enhanced_session_analysis(self, year, grand_prix, session):
        """Comprehensive enhanced session analysis"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return None
            
            analysis = {
                'session_overview': self.generate_session_overview(session_data, year, grand_prix, session),
                'performance_insights': self.generate_performance_insights(session_data),
                'competitive_analysis': self.analyze_competitive_dynamics(session_data),
                'technical_analysis': self.perform_technical_analysis(session_data),
                'strategic_insights': self.generate_strategic_insights(session_data, session),
                'predictive_analytics': self.generate_predictive_insights(session_data),
                'session_highlights': self.identify_session_highlights(session_data),
                'comparative_metrics': self.generate_comparative_metrics(session_data)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_session_overview(self, session_data, year, grand_prix, session):
        """Generate comprehensive session overview"""
        try:
            overview = {
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session_type': session,
                    'total_drivers': len(session_data.drivers),
                    'total_laps': len(session_data.laps) if hasattr(session_data, 'laps') else 0,
                    'session_duration': self.calculate_session_duration(session_data)
                },
                'weather_conditions': self.get_weather_overview(session_data),
                'track_conditions': self.assess_track_conditions(session_data),
                'session_classification': self.classify_session_type(session_data, session)
            }
            
            return overview
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_performance_insights(self, session_data):
        """Generate detailed performance insights"""
        try:
            insights = {}
            
            # Analyze top performers
            top_performers = self.identify_top_performers(session_data)
            
            # Analyze performance gaps
            performance_gaps = self.analyze_performance_gaps(session_data)
            
            # Analyze improvement patterns
            improvement_patterns = self.analyze_improvement_patterns(session_data)
            
            # Driver-specific insights
            driver_insights = {}
            for driver in session_data.drivers[:10]:  # Top 10 for performance
                try:
                    driver_analysis = self.analyze_driver_performance(session_data, driver)
                    if driver_analysis:
                        driver_insights[driver] = driver_analysis
                except Exception as driver_error:
                    continue
            
            insights = {
                'top_performers': top_performers,
                'performance_gaps': performance_gaps,
                'improvement_patterns': improvement_patterns,
                'driver_specific_insights': driver_insights,
                'performance_summary': self.summarize_performance_insights(top_performers, performance_gaps)
            }
            
            return insights
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_competitive_dynamics(self, session_data):
        """Analyze competitive dynamics within the session"""
        try:
            dynamics = {
                'championship_battles': self.identify_championship_battles(session_data),
                'team_battles': self.analyze_team_battles(session_data),
                'performance_clusters': self.identify_performance_clusters(session_data),
                'competitive_intensity': self.measure_competitive_intensity(session_data),
                'position_volatility': self.analyze_position_volatility(session_data)
            }
            
            return dynamics
            
        except Exception as e:
            return {'error': str(e)}
    
    def perform_technical_analysis(self, session_data):
        """Perform detailed technical analysis"""
        try:
            technical_data = {
                'aerodynamic_analysis': self.analyze_aerodynamic_performance(session_data),
                'power_unit_analysis': self.analyze_power_unit_performance(session_data),
                'tire_analysis': self.analyze_tire_performance_detailed(session_data),
                'setup_analysis': self.analyze_setup_effectiveness(session_data),
                'reliability_analysis': self.analyze_reliability_issues(session_data)
            }
            
            return technical_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_strategic_insights(self, session_data, session_type):
        """Generate strategic insights based on session type"""
        try:
            if session_type == 'Race':
                return self.generate_race_strategic_insights(session_data)
            elif session_type == 'Qualifying':
                return self.generate_qualifying_strategic_insights(session_data)
            else:
                return self.generate_practice_strategic_insights(session_data)
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_predictive_insights(self, session_data):
        """Generate predictive insights for future performance"""
        try:
            predictions = {
                'race_pace_predictions': self.predict_race_pace(session_data),
                'tire_strategy_predictions': self.predict_optimal_tire_strategies(session_data),
                'weather_impact_predictions': self.predict_weather_impact(session_data),
                'championship_implications': self.analyze_championship_implications(session_data),
                'next_session_outlook': self.generate_next_session_outlook(session_data)
            }
            
            return predictions
            
        except Exception as e:
            return {'error': str(e)}
    
    def identify_session_highlights(self, session_data):
        """Identify key highlights from the session"""
        try:
            highlights = {
                'fastest_times': self.extract_fastest_times(session_data),
                'notable_performances': self.identify_notable_performances(session_data),
                'incidents_and_flags': self.identify_incidents(session_data),
                'record_breakers': self.identify_record_breaking_performances(session_data),
                'surprise_performances': self.identify_surprise_performances(session_data)
            }
            
            return highlights
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_comparative_metrics(self, session_data):
        """Generate comparative metrics across drivers"""
        try:
            metrics = {
                'speed_trap_comparison': self.compare_speed_traps(session_data),
                'sector_time_comparison': self.compare_sector_times(session_data),
                'consistency_comparison': self.compare_consistency_metrics(session_data),
                'tire_usage_comparison': self.compare_tire_usage(session_data),
                'fuel_efficiency_comparison': self.compare_fuel_efficiency(session_data)
            }
            
            return metrics
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_session_duration(self, session_data):
        """Calculate total session duration"""
        try:
            if hasattr(session_data, 'laps') and not session_data.laps.empty:
                start_time = session_data.laps['Time'].min()
                end_time = session_data.laps['Time'].max()
                duration = end_time - start_time
                return str(duration)
            return 'Unknown'
        except Exception as e:
            return 'Unknown'
    
    def get_weather_overview(self, session_data):
        """Get weather overview for the session"""
        try:
            weather_data = self.data_loader.get_weather_data(session_data)
            if weather_data is None or weather_data.empty:
                return {'status': 'No weather data available'}
            
            return {
                'air_temperature': {
                    'avg': float(weather_data['AirTemp'].mean()),
                    'range': [float(weather_data['AirTemp'].min()), float(weather_data['AirTemp'].max())]
                },
                'track_temperature': {
                    'avg': float(weather_data['TrackTemp'].mean()),
                    'range': [float(weather_data['TrackTemp'].min()), float(weather_data['TrackTemp'].max())]
                },
                'humidity': float(weather_data['Humidity'].mean()),
                'conditions': self.classify_weather_conditions(weather_data)
            }
        except Exception as e:
            return {'status': 'Error retrieving weather data'}
    
    def assess_track_conditions(self, session_data):
        """Assess overall track conditions"""
        try:
            # This would analyze multiple factors to assess track conditions
            # For now, providing a simplified assessment
            
            all_lap_times = []
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if not driver_laps.empty:
                    lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
                    all_lap_times.extend(lap_times)
            
            if not all_lap_times:
                return {'status': 'Unknown'}
            
            avg_lap_time = np.mean(all_lap_times)
            lap_time_variance = np.var(all_lap_times)
            
            return {
                'average_lap_time': float(avg_lap_time),
                'lap_time_variance': float(lap_time_variance),
                'conditions_rating': self.rate_track_conditions(lap_time_variance),
                'grip_level': self.estimate_grip_level(lap_time_variance)
            }
            
        except Exception as e:
            return {'status': 'Error assessing track conditions'}
    
    def classify_session_type(self, session_data, session):
        """Classify the session type and characteristics"""
        try:
            classification = {
                'session_type': session,
                'competitiveness': self.measure_session_competitiveness(session_data),
                'difficulty_level': self.assess_session_difficulty(session_data),
                'strategic_importance': self.assess_strategic_importance(session)
            }
            
            return classification
            
        except Exception as e:
            return {'session_type': session, 'status': 'Classification error'}
    
    def identify_top_performers(self, session_data):
        """Identify top performing drivers"""
        try:
            driver_performance = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                fastest_lap = driver_laps.pick_fastest()
                performance_score = self.calculate_performance_score(driver_laps, fastest_lap)
                
                driver_performance[driver] = {
                    'fastest_lap_time': str(fastest_lap['LapTime']),
                    'performance_score': performance_score,
                    'total_laps': len(driver_laps),
                    'consistency_rating': self.rate_driver_consistency(driver_laps)
                }
            
            # Sort by performance score
            sorted_performers = sorted(
                driver_performance.items(),
                key=lambda x: x[1]['performance_score'],
                reverse=True
            )
            
            return {
                'top_3': sorted_performers[:3],
                'all_drivers': sorted_performers,
                'performance_spread': self.calculate_performance_spread(driver_performance)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_performance_gaps(self, session_data):
        """Analyze performance gaps between drivers"""
        try:
            fastest_times = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()
                    fastest_times[driver] = fastest_lap['LapTime'].total_seconds()
            
            if not fastest_times:
                return {'error': 'No lap times available'}
            
            fastest_overall = min(fastest_times.values())
            gaps = {driver: time - fastest_overall for driver, time in fastest_times.items()}
            
            return {
                'fastest_time': fastest_overall,
                'gaps_to_fastest': gaps,
                'average_gap': float(np.mean(list(gaps.values()))),
                'largest_gap': float(max(gaps.values())),
                'competitiveness_rating': self.rate_competitiveness(gaps)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_improvement_patterns(self, session_data):
        """Analyze how drivers improved throughout the session"""
        try:
            improvement_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if len(driver_laps) < 5:  # Need sufficient laps
                    continue
                
                lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
                if len(lap_times) < 5:
                    continue
                
                # Analyze improvement trend
                lap_numbers = list(range(len(lap_times)))
                trend_slope = np.polyfit(lap_numbers, lap_times, 1)[0]
                
                improvement_data[driver] = {
                    'trend_slope': float(trend_slope),
                    'improvement_direction': 'improving' if trend_slope < -0.01 else 'stable' if abs(trend_slope) <= 0.01 else 'declining',
                    'first_lap_time': lap_times[0],
                    'last_lap_time': lap_times[-1],
                    'best_lap_time': min(lap_times),
                    'improvement_magnitude': float(abs(trend_slope))
                }
            
            return improvement_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_driver_performance(self, session_data, driver):
        """Detailed analysis of individual driver performance"""
        try:
            driver_laps = session_data.laps.pick_driver(driver)
            if driver_laps.empty:
                return None
            
            analysis = {
                'basic_stats': self.get_driver_basic_stats(driver_laps),
                'sector_analysis': self.analyze_driver_sectors(driver_laps),
                'consistency_analysis': self.analyze_driver_consistency(driver_laps),
                'tire_management': self.analyze_driver_tire_management(driver_laps),
                'performance_rating': self.rate_overall_driver_performance(driver_laps)
            }
            
            return analysis
            
        except Exception as e:
            return None
        
    def summarize_performance_insights(self, top_performers, performance_gaps):
        """Summarize key performance insights"""
        try:
            if not top_performers.get('top_3') or not performance_gaps.get('gaps_to_fastest'):
                return {'error': 'Insufficient data for summary'}
            
            summary = {
                'session_winner': top_performers['top_3'][0][0] if top_performers['top_3'] else 'Unknown',
                'competitiveness_level': performance_gaps.get('competitiveness_rating', 'Unknown'),
                'performance_spread': f"{performance_gaps.get('largest_gap', 0):.3f}s",
                'key_insights': self.generate_key_insights(top_performers, performance_gaps)
            }
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_key_insights(self, top_performers, performance_gaps):
        """Generate key insights from the analysis"""
        insights = []
        
        try:
            if performance_gaps.get('largest_gap', 0) < 1.0:
                insights.append("Very competitive session with tight performance gaps")
            elif performance_gaps.get('largest_gap', 0) > 3.0:
                insights.append("Large performance spread indicates varying conditions or setup issues")
            
            avg_gap = performance_gaps.get('average_gap', 0)
            if avg_gap < 0.5:
                insights.append("Field closely matched with minimal average gap")
            
            if len(top_performers.get('top_3', [])) >= 3:
                top_3_gap = (
                    top_performers['top_3'][2][1]['performance_score'] - 
                    top_performers['top_3'][0][1]['performance_score']
                )
                if abs(top_3_gap) < 10:
                    insights.append("Top 3 drivers very evenly matched")
        
        except Exception as e:
            insights.append("Analysis completed with limited insights")
        
        return insights
    
    # Additional helper methods for detailed analysis
    def calculate_performance_score(self, driver_laps, fastest_lap):
        """Calculate overall performance score for a driver"""
        try:
            # Base score from lap time
            lap_time_score = 100 - (fastest_lap['LapTime'].total_seconds() - 60)  # Normalized
            
            # Consistency bonus
            lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
            if len(lap_times) > 1:
                consistency_bonus = max(0, 20 - (np.std(lap_times) * 10))
            else:
                consistency_bonus = 0
            
            # Volume bonus (more laps = more data)
            volume_bonus = min(10, len(driver_laps) / 2)
            
            total_score = lap_time_score + consistency_bonus + volume_bonus
            return float(max(0, min(200, total_score)))  # Clamp between 0-200
            
        except Exception as e:
            return 50.0
    
    def rate_driver_consistency(self, driver_laps):
        """Rate driver consistency"""
        try:
            lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
            if len(lap_times) < 2:
                return 'insufficient_data'
            
            cv = np.std(lap_times) / np.mean(lap_times)
            
            if cv < 0.01:
                return 'excellent'
            elif cv < 0.02:
                return 'good'
            elif cv < 0.04:
                return 'average'
            else:
                return 'poor'
                
        except Exception as e:
            return 'unknown'
    
    def calculate_performance_spread(self, driver_performance):
        """Calculate the spread of performance across all drivers"""
        try:
            scores = [data['performance_score'] for data in driver_performance.values()]
            return {
                'range': float(max(scores) - min(scores)),
                'standard_deviation': float(np.std(scores)),
                'coefficient_of_variation': float(np.std(scores) / np.mean(scores))
            }
        except Exception as e:
            return {'error': str(e)}
    
    def rate_competitiveness(self, gaps):
        """Rate the competitiveness of the session"""
        try:
            avg_gap = np.mean(list(gaps.values()))
            max_gap = max(gaps.values())
            
            if avg_gap < 0.5 and max_gap < 2.0:
                return 'very_high'
            elif avg_gap < 1.0 and max_gap < 3.0:
                return 'high'
            elif avg_gap < 2.0 and max_gap < 5.0:
                return 'moderate'
            else:
                return 'low'
                
        except Exception as e:
            return 'unknown'
    
    def classify_weather_conditions(self, weather_data):
        """Classify weather conditions"""
        try:
            avg_temp = weather_data['AirTemp'].mean()
            avg_humidity = weather_data['Humidity'].mean()
            
            if avg_temp > 30 and avg_humidity < 60:
                return 'hot_dry'
            elif avg_temp > 25 and avg_humidity > 80:
                return 'hot_humid'
            elif avg_temp < 20:
                return 'cool'
            else:
                return 'moderate'
                
        except Exception as e:
            return 'unknown'
    
    def rate_track_conditions(self, variance):
        """Rate track conditions based on lap time variance"""
        if variance < 1.0:
            return 'excellent'
        elif variance < 4.0:
            return 'good'
        elif variance < 9.0:
            return 'challenging'
        else:
            return 'difficult'
    
    def estimate_grip_level(self, variance):
        """Estimate grip level from lap time variance"""
        if variance < 2.0:
            return 'high'
        elif variance < 6.0:
            return 'medium'
        else:
            return 'low'
    
    # Placeholder methods for comprehensive analysis (would be fully implemented)
    def identify_championship_battles(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def analyze_team_battles(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def identify_performance_clusters(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def measure_competitive_intensity(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def analyze_position_volatility(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def analyze_aerodynamic_performance(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def analyze_power_unit_performance(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def analyze_tire_performance_detailed(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def analyze_setup_effectiveness(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def analyze_reliability_issues(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def generate_race_strategic_insights(self, session_data):
        return {'type': 'race_strategy', 'status': 'Framework ready'}
    
    def generate_qualifying_strategic_insights(self, session_data):
        return {'type': 'qualifying_strategy', 'status': 'Framework ready'}
    
    def generate_practice_strategic_insights(self, session_data):
        return {'type': 'practice_strategy', 'status': 'Framework ready'}
    
    def predict_race_pace(self, session_data):
        return {'status': 'Prediction framework ready'}
    
    def predict_optimal_tire_strategies(self, session_data):
        return {'status': 'Prediction framework ready'}
    
    def predict_weather_impact(self, session_data):
        return {'status': 'Prediction framework ready'}
    
    def analyze_championship_implications(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def generate_next_session_outlook(self, session_data):
        return {'status': 'Outlook framework ready'}
    
    def extract_fastest_times(self, session_data):
        return {'status': 'Extraction framework ready'}
    
    def identify_notable_performances(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def identify_incidents(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def identify_record_breaking_performances(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def identify_surprise_performances(self, session_data):
        return {'status': 'Analysis framework ready'}
    
    def compare_speed_traps(self, session_data):
        return {'status': 'Comparison framework ready'}
    
    def compare_sector_times(self, session_data):
        return {'status': 'Comparison framework ready'}
    
    def compare_consistency_metrics(self, session_data):
        return {'status': 'Comparison framework ready'}
    
    def compare_tire_usage(self, session_data):
        return {'status': 'Comparison framework ready'}
    
    def compare_fuel_efficiency(self, session_data):
        return {'status': 'Comparison framework ready'}
    
    def measure_session_competitiveness(self, session_data):
        return 'high'  # Simplified
    
    def assess_session_difficulty(self, session_data):
        return 'moderate'  # Simplified
    
    def assess_strategic_importance(self, session):
        importance_map = {
            'Race': 'very_high',
            'Qualifying': 'high',
            'Practice 3': 'medium',
            'Practice 2': 'medium',
            'Practice 1': 'low'
        }
        return importance_map.get(session, 'medium')
    
    def get_driver_basic_stats(self, driver_laps):
        return {'status': 'Stats framework ready'}
    
    def analyze_driver_sectors(self, driver_laps):
        return {'status': 'Sector analysis framework ready'}
    
    def analyze_driver_consistency(self, driver_laps):
        return {'status': 'Consistency analysis framework ready'}
    
    def analyze_driver_tire_management(self, driver_laps):
        return {'status': 'Tire management analysis framework ready'}
    
    def rate_overall_driver_performance(self, driver_laps):
        return 'good'  # Simplified
