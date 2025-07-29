"""
Driver Comparison Module
Advanced driver-to-driver comparison and analysis
"""

import fastf1
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import scipy.stats as stats

class DriverComparisonAnalyzer:
    """Advanced driver comparison and performance analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_comprehensive_comparison(self, year: int, grand_prix: str, session: str, 
                                      drivers: List[str]) -> Dict[str, Any]:
        """Create comprehensive comparison between multiple drivers"""
        return self.get_comprehensive_driver_comparison(year, grand_prix, session, drivers)
    
    def get_comprehensive_driver_comparison(self, year: int, grand_prix: str, session: str, 
                                          drivers: List[str]) -> Dict[str, Any]:
        """Comprehensive comparison between multiple drivers"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            comparison_data = {
                'driver_statistics': {},
                'performance_metrics': {},
                'telemetry_comparison': {},
                'sector_analysis': {},
                'consistency_metrics': {}
            }
            
            for driver in drivers:
                try:
                    driver_laps = session_obj.laps.pick_drivers(driver)
                    if not driver_laps.empty:
                        # Basic statistics
                        comparison_data['driver_statistics'][driver] = self._get_driver_statistics(driver_laps)
                        
                        # Performance metrics
                        comparison_data['performance_metrics'][driver] = self._calculate_performance_metrics(driver_laps)
                        
                        # Sector analysis
                        comparison_data['sector_analysis'][driver] = self._analyze_driver_sectors(driver_laps)
                        
                        # Consistency metrics
                        comparison_data['consistency_metrics'][driver] = self._calculate_consistency_metrics(driver_laps)
                        
                        # Telemetry comparison (fastest lap)
                        fastest_lap = driver_laps.pick_fastest()
                        if fastest_lap is not None:
                            telemetry = fastest_lap.get_telemetry()
                            comparison_data['telemetry_comparison'][driver] = self._extract_telemetry_metrics(telemetry)
                
                except Exception as driver_error:
                    self.logger.warning(f"Error analyzing driver {driver}: {str(driver_error)}")
                    continue
            
            # Add comparative analysis
            comparison_data['comparative_analysis'] = self._generate_comparative_insights(comparison_data, drivers)
            
            return {
                'driver_comparison': comparison_data,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session,
                    'drivers_compared': drivers
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive driver comparison: {str(e)}")
            return {'error': str(e)}
    
    def _get_driver_statistics(self, driver_laps: pd.DataFrame) -> Dict[str, Any]:
        """Extract basic driver statistics"""
        valid_laps = driver_laps['LapTime'].dropna()
        
        if valid_laps.empty:
            return {'total_laps': 0, 'valid_laps': 0}
        
        lap_times_seconds = [lt.total_seconds() for lt in valid_laps]
        
        return {
            'total_laps': len(driver_laps),
            'valid_laps': len(valid_laps),
            'fastest_lap_time': float(min(lap_times_seconds)),
            'average_lap_time': float(np.mean(lap_times_seconds)),
            'slowest_lap_time': float(max(lap_times_seconds)),
            'lap_time_range': float(max(lap_times_seconds) - min(lap_times_seconds)),
            'median_lap_time': float(np.median(lap_times_seconds))
        }
    
    def _calculate_performance_metrics(self, driver_laps: pd.DataFrame) -> Dict[str, float]:
        """Calculate advanced performance metrics"""
        valid_laps = driver_laps['LapTime'].dropna()
        
        if len(valid_laps) < 2:
            return {'performance_score': 0.0, 'improvement_rate': 0.0}
        
        lap_times_seconds = [lt.total_seconds() for lt in valid_laps]
        lap_numbers = list(range(len(lap_times_seconds)))
        
        # Calculate improvement rate
        slope, _, r_value, _, _ = stats.linregress(lap_numbers, lap_times_seconds) if len(lap_times_seconds) > 1 else (0, 0, 0, 0, 0)
        
        # Performance score (based on consistency and speed)
        avg_time = np.mean(lap_times_seconds)
        std_time = np.std(lap_times_seconds)
        cv = std_time / avg_time if avg_time > 0 else 0
        performance_score = max(0, 100 * (1 - cv))  # Higher is better
        
        return {
            'performance_score': float(performance_score),
            'improvement_rate': float(slope),  # Negative = improving
            'correlation_coefficient': float(r_value),
            'coefficient_of_variation': float(cv)
        }
    
    def _analyze_driver_sectors(self, driver_laps: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Analyze sector performance for a driver"""
        sector_analysis = {}
        
        sectors = ['Sector1Time', 'Sector2Time', 'Sector3Time']
        sector_names = ['sector_1', 'sector_2', 'sector_3']
        
        for sector, name in zip(sectors, sector_names):
            sector_times = driver_laps[sector].dropna()
            
            if not sector_times.empty:
                sector_times_seconds = [st.total_seconds() for st in sector_times]
                
                sector_analysis[name] = {
                    'best_time': float(min(sector_times_seconds)),
                    'average_time': float(np.mean(sector_times_seconds)),
                    'worst_time': float(max(sector_times_seconds)),
                    'consistency': float(100 - (np.std(sector_times_seconds) / np.mean(sector_times_seconds) * 100)) if np.mean(sector_times_seconds) > 0 else 0,
                    'improvement_potential': float(max(sector_times_seconds) - min(sector_times_seconds))
                }
            else:
                sector_analysis[name] = {
                    'best_time': 0.0, 'average_time': 0.0, 'worst_time': 0.0,
                    'consistency': 0.0, 'improvement_potential': 0.0
                }
        
        return sector_analysis
    
    def _calculate_consistency_metrics(self, driver_laps: pd.DataFrame) -> Dict[str, float]:
        """Calculate consistency metrics for a driver"""
        valid_laps = driver_laps['LapTime'].dropna()
        
        if len(valid_laps) < 3:
            return {'consistency_score': 0.0, 'consistency_rank': 0.0}
        
        lap_times_seconds = [lt.total_seconds() for lt in valid_laps]
        
        # Various consistency measures
        cv = np.std(lap_times_seconds) / np.mean(lap_times_seconds) if np.mean(lap_times_seconds) > 0 else 0
        consistency_score = max(0, 100 * (1 - cv * 10))  # Scale factor
        
        # Quartile-based consistency
        q1, q3 = np.percentile(lap_times_seconds, [25, 75])
        iqr_consistency = 100 - ((q3 - q1) / np.median(lap_times_seconds) * 100) if np.median(lap_times_seconds) > 0 else 0
        
        return {
            'consistency_score': float(min(100.0, consistency_score)),
            'iqr_consistency': float(max(0.0, iqr_consistency)),
            'lap_time_std': float(np.std(lap_times_seconds)),
            'outlier_count': int(len([lt for lt in lap_times_seconds if abs(lt - np.mean(lap_times_seconds)) > 2 * np.std(lap_times_seconds)]))
        }
    
    def _extract_telemetry_metrics(self, telemetry: pd.DataFrame) -> Dict[str, float]:
        """Extract key telemetry metrics from fastest lap"""
        if telemetry.empty:
            return {}
        
        metrics = {
            'max_speed': float(telemetry['Speed'].max()),
            'avg_speed': float(telemetry['Speed'].mean()),
            'min_speed': float(telemetry['Speed'].min()),
            'max_throttle': float(telemetry['Throttle'].max()),
            'avg_throttle': float(telemetry['Throttle'].mean()),
            'max_brake': float(telemetry['Brake'].max()),
            'avg_brake': float(telemetry['Brake'].mean()),
            'max_rpm': float(telemetry['RPM'].max()),
            'avg_rpm': float(telemetry['RPM'].mean()),
            'max_gear': float(telemetry['nGear'].max()),
            'gear_changes': len(telemetry['nGear'].diff().dropna()[telemetry['nGear'].diff().dropna() != 0])
        }
        
        # Calculate time spent in different zones
        total_points = len(telemetry)
        metrics['full_throttle_percentage'] = float((telemetry['Throttle'] == 100).sum() / total_points * 100)
        metrics['braking_percentage'] = float((telemetry['Brake'] > 0).sum() / total_points * 100)
        metrics['coasting_percentage'] = float(((telemetry['Throttle'] == 0) & (telemetry['Brake'] == 0)).sum() / total_points * 100)
        
        # DRS usage if available
        if 'DRS' in telemetry.columns:
            metrics['drs_usage_percentage'] = float((telemetry['DRS'] > 0).sum() / total_points * 100)
        
        return metrics
    
    def _generate_comparative_insights(self, comparison_data: Dict, drivers: List[str]) -> Dict[str, Any]:
        """Generate comparative insights between drivers"""
        insights = {
            'fastest_driver': None,
            'most_consistent_driver': None,
            'best_sector_performers': {},
            'telemetry_leaders': {},
            'overall_rankings': {}
        }
        
        try:
            # Find fastest driver
            fastest_times = {}
            for driver in drivers:
                if driver in comparison_data['driver_statistics']:
                    fastest_times[driver] = comparison_data['driver_statistics'][driver].get('fastest_lap_time', float('inf'))
            
            if fastest_times:
                insights['fastest_driver'] = min(fastest_times, key=fastest_times.get)
            
            # Find most consistent driver
            consistency_scores = {}
            for driver in drivers:
                if driver in comparison_data['consistency_metrics']:
                    consistency_scores[driver] = comparison_data['consistency_metrics'][driver].get('consistency_score', 0)
            
            if consistency_scores:
                insights['most_consistent_driver'] = max(consistency_scores, key=consistency_scores.get)
            
            # Best sector performers
            for sector in ['sector_1', 'sector_2', 'sector_3']:
                sector_times = {}
                for driver in drivers:
                    if driver in comparison_data['sector_analysis']:
                        sector_data = comparison_data['sector_analysis'][driver].get(sector, {})
                        best_time = sector_data.get('best_time', float('inf'))
                        if best_time > 0:
                            sector_times[driver] = best_time
                
                if sector_times:
                    insights['best_sector_performers'][sector] = min(sector_times, key=sector_times.get)
            
            # Telemetry leaders
            telemetry_categories = ['max_speed', 'avg_speed', 'full_throttle_percentage']
            for category in telemetry_categories:
                category_values = {}
                for driver in drivers:
                    if driver in comparison_data['telemetry_comparison']:
                        value = comparison_data['telemetry_comparison'][driver].get(category, 0)
                        category_values[driver] = value
                
                if category_values:
                    insights['telemetry_leaders'][category] = max(category_values, key=category_values.get)
            
            # Overall rankings
            insights['overall_rankings'] = self._calculate_overall_rankings(comparison_data, drivers)
        
        except Exception as e:
            self.logger.warning(f"Error generating comparative insights: {str(e)}")
        
        return insights
    
    def _calculate_overall_rankings(self, comparison_data: Dict, drivers: List[str]) -> Dict[str, List[str]]:
        """Calculate overall rankings for different categories"""
        rankings = {}
        
        # Speed ranking
        speed_scores = {}
        for driver in drivers:
            if driver in comparison_data['driver_statistics']:
                fastest_time = comparison_data['driver_statistics'][driver].get('fastest_lap_time', float('inf'))
                if fastest_time < float('inf'):
                    speed_scores[driver] = 1 / fastest_time  # Higher is better
        
        if speed_scores:
            rankings['speed_ranking'] = sorted(speed_scores.keys(), key=lambda x: speed_scores[x], reverse=True)
        
        # Consistency ranking
        consistency_scores = {}
        for driver in drivers:
            if driver in comparison_data['consistency_metrics']:
                score = comparison_data['consistency_metrics'][driver].get('consistency_score', 0)
                consistency_scores[driver] = score
        
        if consistency_scores:
            rankings['consistency_ranking'] = sorted(consistency_scores.keys(), key=lambda x: consistency_scores[x], reverse=True)
        
        # Performance ranking (combined speed and consistency)
        performance_scores = {}
        for driver in drivers:
            speed_score = speed_scores.get(driver, 0)
            consistency_score = consistency_scores.get(driver, 0)
            # Weighted combination: 60% speed, 40% consistency
            combined_score = speed_score * 0.6 + (consistency_score / 100) * 0.4
            performance_scores[driver] = combined_score
        
        if performance_scores:
            rankings['performance_ranking'] = sorted(performance_scores.keys(), key=lambda x: performance_scores[x], reverse=True)
        
        return rankings
    
    def get_head_to_head_detailed_analysis(self, year: int, grand_prix: str, session: str, 
                                         driver1: str, driver2: str) -> Dict[str, Any]:
        """Detailed head-to-head analysis between two drivers"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            # Get data for both drivers
            driver1_laps = session_obj.laps.pick_drivers(driver1)
            driver2_laps = session_obj.laps.pick_drivers(driver2)
            
            if driver1_laps.empty or driver2_laps.empty:
                return {'error': f'Insufficient data for comparison between {driver1} and {driver2}'}
            
            head_to_head = {
                'lap_time_comparison': self._compare_lap_times(driver1_laps, driver2_laps, driver1, driver2),
                'sector_comparison': self._compare_sectors(driver1_laps, driver2_laps, driver1, driver2),
                'telemetry_comparison': self._compare_telemetry(driver1_laps, driver2_laps, driver1, driver2),
                'consistency_comparison': self._compare_consistency(driver1_laps, driver2_laps, driver1, driver2),
                'race_pace_comparison': self._compare_race_pace(driver1_laps, driver2_laps, driver1, driver2)
            }
            
            # Overall verdict
            head_to_head['overall_verdict'] = self._generate_head_to_head_verdict(head_to_head, driver1, driver2)
            
            return {
                'head_to_head_analysis': head_to_head,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session,
                    'driver1': driver1,
                    'driver2': driver2
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in head-to-head analysis: {str(e)}")
            return {'error': str(e)}
    
    def _compare_lap_times(self, laps1: pd.DataFrame, laps2: pd.DataFrame, 
                          driver1: str, driver2: str) -> Dict[str, Any]:
        """Compare lap times between two drivers"""
        valid_laps1 = laps1['LapTime'].dropna()
        valid_laps2 = laps2['LapTime'].dropna()
        
        if valid_laps1.empty or valid_laps2.empty:
            return {'comparison_possible': False}
        
        times1 = [lt.total_seconds() for lt in valid_laps1]
        times2 = [lt.total_seconds() for lt in valid_laps2]
        
        return {
            'comparison_possible': True,
            f'{driver1}_fastest': float(min(times1)),
            f'{driver2}_fastest': float(min(times2)),
            f'{driver1}_average': float(np.mean(times1)),
            f'{driver2}_average': float(np.mean(times2)),
            'fastest_gap': float(min(times1) - min(times2)),  # Negative means driver1 is faster
            'average_gap': float(np.mean(times1) - np.mean(times2)),
            'winner': driver1 if min(times1) < min(times2) else driver2,
            'gap_to_winner': float(abs(min(times1) - min(times2)))
        }
    
    def _compare_sectors(self, laps1: pd.DataFrame, laps2: pd.DataFrame, 
                        driver1: str, driver2: str) -> Dict[str, Dict[str, Any]]:
        """Compare sector times between two drivers"""
        sector_comparison = {}
        
        sectors = ['Sector1Time', 'Sector2Time', 'Sector3Time']
        sector_names = ['sector_1', 'sector_2', 'sector_3']
        
        for sector, name in zip(sectors, sector_names):
            sector1 = laps1[sector].dropna()
            sector2 = laps2[sector].dropna()
            
            if not sector1.empty and not sector2.empty:
                times1 = [st.total_seconds() for st in sector1]
                times2 = [st.total_seconds() for st in sector2]
                
                sector_comparison[name] = {
                    f'{driver1}_best': float(min(times1)),
                    f'{driver2}_best': float(min(times2)),
                    'gap': float(min(times1) - min(times2)),
                    'winner': driver1 if min(times1) < min(times2) else driver2,
                    f'{driver1}_consistency': float(100 - (np.std(times1) / np.mean(times1) * 100)) if np.mean(times1) > 0 else 0,
                    f'{driver2}_consistency': float(100 - (np.std(times2) / np.mean(times2) * 100)) if np.mean(times2) > 0 else 0
                }
        
        return sector_comparison
    
    def _compare_telemetry(self, laps1: pd.DataFrame, laps2: pd.DataFrame, 
                          driver1: str, driver2: str) -> Dict[str, Any]:
        """Compare telemetry from fastest laps"""
        try:
            fastest1 = laps1.pick_fastest()
            fastest2 = laps2.pick_fastest()
            
            if fastest1 is None or fastest2 is None:
                return {'comparison_possible': False}
            
            tel1 = fastest1.get_telemetry()
            tel2 = fastest2.get_telemetry()
            
            if tel1.empty or tel2.empty:
                return {'comparison_possible': False}
            
            return {
                'comparison_possible': True,
                'max_speed': {
                    driver1: float(tel1['Speed'].max()),
                    driver2: float(tel2['Speed'].max()),
                    'winner': driver1 if tel1['Speed'].max() > tel2['Speed'].max() else driver2
                },
                'avg_speed': {
                    driver1: float(tel1['Speed'].mean()),
                    driver2: float(tel2['Speed'].mean()),
                    'winner': driver1 if tel1['Speed'].mean() > tel2['Speed'].mean() else driver2
                },
                'throttle_usage': {
                    driver1: float(tel1['Throttle'].mean()),
                    driver2: float(tel2['Throttle'].mean()),
                    'winner': driver1 if tel1['Throttle'].mean() > tel2['Throttle'].mean() else driver2
                },
                'braking_intensity': {
                    driver1: float(tel1['Brake'].mean()),
                    driver2: float(tel2['Brake'].mean()),
                    'comparison': 'Higher indicates more braking'
                }
            }
            
        except Exception as e:
            self.logger.warning(f"Error comparing telemetry: {str(e)}")
            return {'comparison_possible': False, 'error': str(e)}
    
    def _compare_consistency(self, laps1: pd.DataFrame, laps2: pd.DataFrame, 
                           driver1: str, driver2: str) -> Dict[str, Any]:
        """Compare consistency between two drivers"""
        valid_laps1 = laps1['LapTime'].dropna()
        valid_laps2 = laps2['LapTime'].dropna()
        
        if len(valid_laps1) < 2 or len(valid_laps2) < 2:
            return {'comparison_possible': False}
        
        times1 = [lt.total_seconds() for lt in valid_laps1]
        times2 = [lt.total_seconds() for lt in valid_laps2]
        
        cv1 = np.std(times1) / np.mean(times1) if np.mean(times1) > 0 else 0
        cv2 = np.std(times2) / np.mean(times2) if np.mean(times2) > 0 else 0
        
        consistency1 = max(0, 100 * (1 - cv1 * 10))
        consistency2 = max(0, 100 * (1 - cv2 * 10))
        
        return {
            'comparison_possible': True,
            f'{driver1}_consistency_score': float(min(100.0, consistency1)),
            f'{driver2}_consistency_score': float(min(100.0, consistency2)),
            f'{driver1}_coefficient_variation': float(cv1),
            f'{driver2}_coefficient_variation': float(cv2),
            'more_consistent': driver1 if consistency1 > consistency2 else driver2,
            'consistency_gap': float(abs(consistency1 - consistency2))
        }
    
    def _compare_race_pace(self, laps1: pd.DataFrame, laps2: pd.DataFrame, 
                          driver1: str, driver2: str) -> Dict[str, Any]:
        """Compare race pace over stint lengths"""
        # This would typically analyze pace over tire stints
        # For now, provide basic race pace comparison
        
        valid_laps1 = laps1['LapTime'].dropna()
        valid_laps2 = laps2['LapTime'].dropna()
        
        if valid_laps1.empty or valid_laps2.empty:
            return {'comparison_possible': False}
        
        # Exclude outliers (very slow laps)
        times1 = [lt.total_seconds() for lt in valid_laps1]
        times2 = [lt.total_seconds() for lt in valid_laps2]
        
        # Remove outliers (laps more than 2 standard deviations from mean)
        mean1, std1 = np.mean(times1), np.std(times1)
        mean2, std2 = np.mean(times2), np.std(times2)
        
        clean_times1 = [t for t in times1 if abs(t - mean1) <= 2 * std1]
        clean_times2 = [t for t in times2 if abs(t - mean2) <= 2 * std2]
        
        if not clean_times1 or not clean_times2:
            return {'comparison_possible': False}
        
        return {
            'comparison_possible': True,
            f'{driver1}_race_pace': float(np.mean(clean_times1)),
            f'{driver2}_race_pace': float(np.mean(clean_times2)),
            'pace_gap': float(np.mean(clean_times1) - np.mean(clean_times2)),
            'faster_race_pace': driver1 if np.mean(clean_times1) < np.mean(clean_times2) else driver2,
            f'{driver1}_pace_laps': len(clean_times1),
            f'{driver2}_pace_laps': len(clean_times2)
        }
    
    def _generate_head_to_head_verdict(self, head_to_head: Dict, driver1: str, driver2: str) -> Dict[str, Any]:
        """Generate overall verdict for head-to-head comparison"""
        categories = ['lap_time', 'consistency', 'race_pace']
        scores = {driver1: 0, driver2: 0}
        
        # Lap time comparison
        if head_to_head['lap_time_comparison'].get('comparison_possible', False):
            winner = head_to_head['lap_time_comparison'].get('winner')
            if winner:
                scores[winner] += 1
        
        # Consistency comparison
        if head_to_head['consistency_comparison'].get('comparison_possible', False):
            winner = head_to_head['consistency_comparison'].get('more_consistent')
            if winner:
                scores[winner] += 1
        
        # Race pace comparison
        if head_to_head['race_pace_comparison'].get('comparison_possible', False):
            winner = head_to_head['race_pace_comparison'].get('faster_race_pace')
            if winner:
                scores[winner] += 1
        
        overall_winner = max(scores, key=scores.get) if max(scores.values()) > 0 else None
        
        return {
            'category_scores': scores,
            'overall_winner': overall_winner,
            'margin_of_victory': abs(scores[driver1] - scores[driver2]) if overall_winner else 0,
            'categories_analyzed': len([cat for cat in categories if head_to_head.get(f'{cat}_comparison', {}).get('comparison_possible', False)])
        }