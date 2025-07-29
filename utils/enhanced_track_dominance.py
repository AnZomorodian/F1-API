"""
Enhanced Track Dominance Analysis
Real FastF1 data-based track dominance analysis with proper JSON serialization
"""

import numpy as np
import pandas as pd
from utils.data_loader import DataLoader
from utils.json_utils import make_json_serializable
import logging

class EnhancedTrackDominanceAnalyzer:
    """Enhanced track dominance analysis using real FastF1 data"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        
    def analyze_track_dominance(self, year, grand_prix, session, driver):
        """
        Analyze track dominance using real FastF1 data
        """
        try:
            # Load real session data
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return None
                
            # Get driver laps using new FastF1 v3.6+ API
            driver_laps = session_data.laps.pick_drivers(driver)
            if driver_laps.empty:
                return None
                
            # Real sector dominance analysis
            sector_dominance = self._analyze_real_sector_dominance(session_data, driver, driver_laps)
            
            # Real dominance metrics
            dominance_metrics = self._calculate_real_dominance_metrics(session_data, driver, driver_laps)
            
            # Real speed dominance
            speed_dominance = self._analyze_real_speed_dominance(driver_laps)
            
            result = {
                'sector_dominance': sector_dominance,
                'dominance_metrics': dominance_metrics,
                'speed_dominance': speed_dominance,
                'track_mastery': self._calculate_track_mastery(sector_dominance, dominance_metrics, speed_dominance)
            }
            
            # Ensure JSON serializable
            return make_json_serializable(result)
            
        except Exception as e:
            logging.error(f"Error in enhanced track dominance analysis: {str(e)}")
            return None
    
    def _analyze_real_sector_dominance(self, session_data, driver, driver_laps):
        """Real sector dominance analysis using FastF1 data"""
        try:
            # Get driver's fastest lap real sector times
            fastest_lap = driver_laps.pick_fastest()
            
            driver_sectors = {}
            for i, sector in enumerate(['Sector1Time', 'Sector2Time', 'Sector3Time'], 1):
                sector_time = fastest_lap[sector]
                if pd.notna(sector_time):
                    driver_sectors[f'sector_{i}_time'] = float(pd.to_timedelta(sector_time).total_seconds())
            
            # Compare with all other drivers for real dominance analysis
            all_drivers_sectors = {}
            for other_driver in session_data.drivers:
                if other_driver == driver:
                    continue
                    
                try:
                    other_laps = session_data.laps.pick_drivers(other_driver)
                    if not other_laps.empty:
                        other_fastest = other_laps.pick_fastest()
                        other_sectors = {}
                        
                        for i, sector in enumerate(['Sector1Time', 'Sector2Time', 'Sector3Time'], 1):
                            sector_time = other_fastest[sector]
                            if pd.notna(sector_time):
                                other_sectors[f'sector_{i}_time'] = float(pd.to_timedelta(sector_time).total_seconds())
                        
                        if other_sectors:
                            all_drivers_sectors[other_driver] = other_sectors
                except:
                    continue
            
            # Calculate real dominance percentages
            dominance_analysis = {}
            
            for sector_key in ['sector_1_time', 'sector_2_time', 'sector_3_time']:
                if sector_key in driver_sectors:
                    driver_time = driver_sectors[sector_key]
                    faster_count = 0
                    total_comparisons = 0
                    
                    for other_driver, other_sectors in all_drivers_sectors.items():
                        if sector_key in other_sectors:
                            total_comparisons += 1
                            if driver_time < other_sectors[sector_key]:
                                faster_count += 1
                    
                    if total_comparisons > 0:
                        dominance_pct = (faster_count / total_comparisons) * 100
                        sector_num = sector_key.split('_')[1]
                        dominance_analysis[f'sector_{sector_num}_performance'] = f"{driver_time:.3f}s ({dominance_pct:.1f}% dominance)"
                    else:
                        sector_num = sector_key.split('_')[1]
                        dominance_analysis[f'sector_{sector_num}_performance'] = f"{driver_time:.3f}s"
            
            return dominance_analysis
            
        except Exception as e:
            logging.error(f"Error in real sector dominance analysis: {str(e)}")
            return {}
    
    def _calculate_real_dominance_metrics(self, session_data, driver, driver_laps):
        """Calculate real dominance metrics from FastF1 data"""
        try:
            # Get all drivers' fastest laps for real comparison
            all_fastest_times = []
            driver_fastest_time = None
            
            for other_driver in session_data.drivers:
                try:
                    other_laps = session_data.laps.pick_drivers(other_driver)
                    if not other_laps.empty:
                        fastest_time = float(pd.to_timedelta(other_laps['LapTime']).dt.total_seconds().min())
                        all_fastest_times.append(fastest_time)
                        
                        if other_driver == driver:
                            driver_fastest_time = fastest_time
                except:
                    continue
            
            if not all_fastest_times or driver_fastest_time is None:
                return {}
            
            # Real dominance calculations
            all_fastest_times.sort()
            driver_position = all_fastest_times.index(driver_fastest_time) + 1
            total_drivers = len(all_fastest_times)
            
            # Real dominance score based on position
            dominance_score = ((total_drivers - driver_position + 1) / total_drivers) * 100
            
            # Real competitive position
            if driver_position == 1:
                competitive_position = "Dominant Leader"
            elif driver_position <= 3:
                competitive_position = "Highly Competitive"
            elif driver_position <= total_drivers // 2:
                competitive_position = "Competitive"
            else:
                competitive_position = "Challenging Position"
            
            # Real performance rating
            if dominance_score >= 90:
                performance_rating = "Outstanding"
            elif dominance_score >= 75:
                performance_rating = "Excellent"
            elif dominance_score >= 60:
                performance_rating = "Good"
            elif dominance_score >= 40:
                performance_rating = "Average"
            else:
                performance_rating = "Below Average"
            
            # Real gap analysis
            fastest_overall = all_fastest_times[0]
            gap_to_fastest = driver_fastest_time - fastest_overall
            
            return {
                'dominance_score': f"{dominance_score:.1f}%",
                'competitive_position': competitive_position,
                'performance_rating': performance_rating,
                'grid_position': f"P{driver_position} of {total_drivers}",
                'gap_to_fastest': f"+{gap_to_fastest:.3f}s" if gap_to_fastest > 0 else "Fastest"
            }
            
        except Exception as e:
            logging.error(f"Error calculating real dominance metrics: {str(e)}")
            return {}
    
    def _analyze_real_speed_dominance(self, driver_laps):
        """Analyze real speed dominance from telemetry"""
        try:
            fastest_lap = driver_laps.pick_fastest()
            telemetry = fastest_lap.get_telemetry()
            
            if telemetry.empty or 'Speed' not in telemetry.columns:
                return {}
            
            # Real speed analysis
            speed_data = telemetry['Speed']
            max_speed = float(speed_data.max())
            avg_speed = float(speed_data.mean())
            speed_consistency = float(speed_data.std())
            
            # Speed zones analysis
            high_speed_zones = len(speed_data[speed_data > (max_speed * 0.9)])
            total_points = len(speed_data)
            high_speed_percentage = (high_speed_zones / total_points) * 100
            
            # Speed dominance classification
            if max_speed > 340:
                speed_category = "Exceptional Top Speed"
            elif max_speed > 320:
                speed_category = "High Top Speed" 
            elif max_speed > 300:
                speed_category = "Good Top Speed"
            else:
                speed_category = "Moderate Top Speed"
            
            return {
                'max_speed_achieved': f"{max_speed:.1f} km/h",
                'average_speed': f"{avg_speed:.1f} km/h",
                'speed_consistency': f"{speed_consistency:.1f} km/h std",
                'speed_category': speed_category,
                'high_speed_percentage': f"{high_speed_percentage:.1f}%"
            }
            
        except Exception as e:
            logging.error(f"Error in real speed dominance analysis: {str(e)}")
            return {}
    
    def _calculate_track_mastery(self, sector_dominance, dominance_metrics, speed_dominance):
        """Calculate overall track mastery from real data"""
        try:
            mastery_factors = []
            
            # Extract dominance score
            if 'dominance_score' in dominance_metrics:
                score_str = dominance_metrics['dominance_score'].replace('%', '')
                try:
                    score = float(score_str)
                    mastery_factors.append(score)
                except:
                    pass
            
            # Sector performance analysis
            sector_scores = []
            for key, value in sector_dominance.items():
                if 'dominance' in value:
                    try:
                        # Extract dominance percentage
                        dominance_part = value.split('(')[1].split('%')[0]
                        sector_scores.append(float(dominance_part))
                    except:
                        pass
            
            if sector_scores:
                avg_sector_dominance = sum(sector_scores) / len(sector_scores)
                mastery_factors.append(avg_sector_dominance)
            
            # Speed mastery
            if speed_dominance.get('speed_category') == 'Exceptional Top Speed':
                mastery_factors.append(95)
            elif speed_dominance.get('speed_category') == 'High Top Speed':
                mastery_factors.append(85)
            elif speed_dominance.get('speed_category') == 'Good Top Speed':
                mastery_factors.append(75)
            else:
                mastery_factors.append(60)
            
            # Calculate overall mastery
            if mastery_factors:
                overall_mastery = sum(mastery_factors) / len(mastery_factors)
                
                if overall_mastery >= 90:
                    mastery_level = "Track Master"
                elif overall_mastery >= 80:
                    mastery_level = "Highly Skilled"
                elif overall_mastery >= 70:
                    mastery_level = "Competent"
                elif overall_mastery >= 60:
                    mastery_level = "Developing"
                else:
                    mastery_level = "Learning"
                
                return {
                    'overall_mastery_score': f"{overall_mastery:.1f}%",
                    'mastery_level': mastery_level,
                    'mastery_factors_analyzed': len(mastery_factors)
                }
            
            return {
                'overall_mastery_score': "Insufficient data",
                'mastery_level': "Cannot determine",
                'mastery_factors_analyzed': 0
            }
            
        except Exception as e:
            logging.error(f"Error calculating track mastery: {str(e)}")
            return {}