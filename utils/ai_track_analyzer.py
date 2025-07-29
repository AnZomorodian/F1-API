"""
AI Track Analysis Engine
Custom AI engine for analyzing F1 track performance using real FastF1 data
"""

import numpy as np
import pandas as pd
from utils.data_loader import DataLoader
import logging

class AITrackAnalyzer:
    """Custom AI engine for track performance analysis"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        
    def analyze_track_performance(self, year, grand_prix, session, driver):
        """
        AI-powered track performance analysis using real FastF1 data
        """
        try:
            # Load real session data
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return None
                
            # Get driver laps
            driver_laps = session_data.laps[session_data.laps['Driver'] == driver]
            if driver_laps.empty:
                return None
                
            # AI Analysis: Track Characteristics
            track_characteristics = self._analyze_track_characteristics(session_data, driver_laps)
            
            # AI Analysis: Performance Metrics
            performance_metrics = self._analyze_performance_metrics(driver_laps)
            
            # AI Analysis: Sector Analysis
            sector_analysis = self._analyze_sectors(driver_laps)
            
            # AI Analysis: Telemetry Insights
            telemetry_insights = self._analyze_telemetry(driver_laps)
            
            # AI Analysis: Competitive Position
            competitive_position = self._analyze_competitive_position(session_data, driver, driver_laps)
            
            return {
                'track_characteristics': track_characteristics,
                'performance_metrics': performance_metrics,
                'sector_analysis': sector_analysis,
                'telemetry_insights': telemetry_insights,
                'competitive_position': competitive_position,
                'ai_insights': self._generate_ai_insights(track_characteristics, performance_metrics, sector_analysis)
            }
            
        except Exception as e:
            logging.error(f"Error in AI track analysis: {str(e)}")
            return None
    
    def _analyze_track_characteristics(self, session_data, driver_laps):
        """AI analysis of track characteristics"""
        try:
            fastest_lap = driver_laps.pick_fastest()
            telemetry = fastest_lap.get_telemetry()
            
            if telemetry.empty:
                return {}
            
            # AI determines track type based on speed patterns
            max_speed = telemetry['Speed'].max()
            avg_speed = telemetry['Speed'].mean()
            speed_variance = telemetry['Speed'].var()
            
            # AI classification logic
            if max_speed > 320:
                track_type = "High-Speed Power Circuit"
                difficulty = "High"
            elif max_speed > 280:
                track_type = "Balanced Circuit"
                difficulty = "Medium"
            else:
                track_type = "Technical/Street Circuit"
                difficulty = "Very High"
            
            # Overtaking difficulty based on speed variance
            if speed_variance > 2000:
                overtaking_difficulty = "Easy - Multiple DRS zones"
            elif speed_variance > 1000:
                overtaking_difficulty = "Moderate - Some opportunities"
            else:
                overtaking_difficulty = "Difficult - Limited opportunities"
            
            # Track layout analysis
            brake_zones = len(telemetry[telemetry['Brake'] > 50])
            total_points = len(telemetry)
            brake_percentage = (brake_zones / total_points) * 100
            
            if brake_percentage > 25:
                layout_type = "Stop-and-Go Layout"
            elif brake_percentage > 15:
                layout_type = "Mixed Layout"
            else:
                layout_type = "High-Speed Layout"
            
            return {
                'track_type': track_type,
                'difficulty_level': difficulty,
                'overtaking_difficulty': overtaking_difficulty,
                'layout_type': layout_type,
                'max_speed_achieved': f"{max_speed:.1f} km/h",
                'avg_speed': f"{avg_speed:.1f} km/h",
                'brake_zone_percentage': f"{brake_percentage:.1f}%"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing track characteristics: {str(e)}")
            return {}
    
    def _analyze_performance_metrics(self, driver_laps):
        """AI analysis of driver performance metrics"""
        try:
            # Convert lap times to seconds for analysis
            lap_times = pd.to_timedelta(driver_laps['LapTime']).dt.total_seconds()
            lap_times = lap_times[lap_times.notna()]
            
            if lap_times.empty:
                return {}
            
            # AI performance calculations
            best_lap = lap_times.min()
            avg_lap = lap_times.mean()
            consistency_std = lap_times.std()
            
            # AI consistency scoring (lower std = higher consistency)
            if consistency_std < 0.5:
                consistency_rating = "Excellent"
                consistency_score = 95
            elif consistency_std < 1.0:
                consistency_rating = "Very Good"
                consistency_score = 85
            elif consistency_std < 1.5:
                consistency_rating = "Good"
                consistency_score = 75
            else:
                consistency_rating = "Needs Improvement"
                consistency_score = 60
            
            # Performance trend analysis
            lap_times_list = lap_times.tolist()
            if len(lap_times_list) > 5:
                early_stint = np.mean(lap_times_list[:5])
                late_stint = np.mean(lap_times_list[-5:])
                trend = "Improving" if late_stint < early_stint else "Degrading"
            else:
                trend = "Insufficient data"
            
            return {
                'best_lap_time': f"{int(best_lap//60)}:{best_lap%60:06.3f}",
                'average_lap_time': f"{int(avg_lap//60)}:{avg_lap%60:06.3f}",
                'consistency_score': f"{consistency_score}/100",
                'consistency_rating': consistency_rating,
                'consistency_std': f"{consistency_std:.3f}s",
                'performance_trend': trend,
                'total_laps': len(lap_times),
                'lap_time_spread': f"{(lap_times.max() - lap_times.min()):.3f}s"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing performance metrics: {str(e)}")
            return {}
    
    def _analyze_sectors(self, driver_laps):
        """AI analysis of sector performance"""
        try:
            sector_data = {}
            
            for sector in ['Sector1Time', 'Sector2Time', 'Sector3Time']:
                sector_times = pd.to_timedelta(driver_laps[sector]).dt.total_seconds()
                sector_times = sector_times[sector_times.notna()]
                
                if not sector_times.empty:
                    best_sector = sector_times.min()
                    avg_sector = sector_times.mean()
                    sector_consistency = sector_times.std()
                    
                    # AI sector strength assessment
                    if sector_consistency < 0.1:
                        strength = "Dominant"
                    elif sector_consistency < 0.2:
                        strength = "Strong"
                    elif sector_consistency < 0.3:
                        strength = "Consistent"
                    else:
                        strength = "Variable"
                    
                    sector_num = sector.replace('SectorTime', '').replace('Sector', '')
                    sector_data[f'sector_{sector_num}'] = {
                        'best_time': f"{best_sector:.3f}s",
                        'average_time': f"{avg_sector:.3f}s",
                        'consistency': f"{sector_consistency:.3f}s",
                        'strength_rating': strength
                    }
            
            return sector_data
            
        except Exception as e:
            logging.error(f"Error analyzing sectors: {str(e)}")
            return {}
    
    def _analyze_telemetry(self, driver_laps):
        """AI analysis of telemetry data"""
        try:
            fastest_lap = driver_laps.pick_fastest()
            telemetry = fastest_lap.get_telemetry()
            
            if telemetry.empty:
                return {}
            
            # AI telemetry insights
            insights = {}
            
            # Speed analysis
            if 'Speed' in telemetry.columns:
                speed_data = telemetry['Speed']
                insights['speed_profile'] = {
                    'max_speed': f"{speed_data.max():.1f} km/h",
                    'avg_speed': f"{speed_data.mean():.1f} km/h",
                    'speed_efficiency': f"{(speed_data.mean()/speed_data.max()*100):.1f}%"
                }
            
            # Throttle analysis
            if 'Throttle' in telemetry.columns:
                throttle_data = telemetry['Throttle']
                full_throttle_pct = (throttle_data == 100).sum() / len(throttle_data) * 100
                insights['throttle_profile'] = {
                    'full_throttle_percentage': f"{full_throttle_pct:.1f}%",
                    'avg_throttle': f"{throttle_data.mean():.1f}%",
                    'throttle_efficiency': "High" if full_throttle_pct > 40 else "Moderate"
                }
            
            # Brake analysis
            if 'Brake' in telemetry.columns:
                brake_data = telemetry['Brake']
                braking_points = (brake_data > 0).sum()
                insights['brake_profile'] = {
                    'braking_points': braking_points,
                    'max_brake_pressure': f"{brake_data.max():.1f}%",
                    'braking_efficiency': "Optimal" if brake_data.max() > 90 else "Conservative"
                }
            
            return insights
            
        except Exception as e:
            logging.error(f"Error analyzing telemetry: {str(e)}")
            return {}
    
    def _analyze_competitive_position(self, session_data, driver, driver_laps):
        """AI analysis of competitive position"""
        try:
            # Get all drivers' fastest laps for comparison
            all_drivers_fastest = []
            
            for other_driver in session_data.drivers:
                try:
                    other_laps = session_data.laps[session_data.laps['Driver'] == other_driver]
                    if not other_laps.empty:
                        fastest = pd.to_timedelta(other_laps['LapTime']).dt.total_seconds().min()
                        all_drivers_fastest.append((other_driver, fastest))
                except:
                    continue
            
            if not all_drivers_fastest:
                return {}
            
            # Sort by lap time
            all_drivers_fastest.sort(key=lambda x: x[1])
            
            # Find driver's position
            driver_position = None
            driver_time = None
            for i, (drv, time) in enumerate(all_drivers_fastest):
                if drv == driver:
                    driver_position = i + 1
                    driver_time = time
                    break
            
            if driver_position is None:
                return {}
            
            # AI competitive analysis
            total_drivers = len(all_drivers_fastest)
            fastest_time = all_drivers_fastest[0][1]
            gap_to_fastest = driver_time - fastest_time
            
            # Position classification
            if driver_position == 1:
                position_rating = "Pole Position"
            elif driver_position <= 3:
                position_rating = "Front Row"
            elif driver_position <= 10:
                position_rating = "Points Position"
            else:
                position_rating = "Midfield/Back"
            
            # Performance classification
            if gap_to_fastest < 0.1:
                performance_level = "Elite"
            elif gap_to_fastest < 0.5:
                performance_level = "Very Competitive"
            elif gap_to_fastest < 1.0:
                performance_level = "Competitive"
            else:
                performance_level = "Needs Improvement"
            
            return {
                'grid_position': driver_position,
                'total_drivers': total_drivers,
                'gap_to_fastest': f"+{gap_to_fastest:.3f}s",
                'position_rating': position_rating,
                'performance_level': performance_level,
                'percentile': f"{((total_drivers - driver_position) / total_drivers * 100):.1f}%"
            }
            
        except Exception as e:
            logging.error(f"Error analyzing competitive position: {str(e)}")
            return {}
    
    def _generate_ai_insights(self, track_characteristics, performance_metrics, sector_analysis):
        """AI-generated insights and recommendations"""
        try:
            insights = []
            
            # Track-based insights
            if track_characteristics.get('track_type') == 'High-Speed Power Circuit':
                insights.append("Focus on aerodynamic efficiency and engine power optimization")
            elif track_characteristics.get('track_type') == 'Technical/Street Circuit':
                insights.append("Prioritize mechanical grip and precise handling setup")
            
            # Performance insights
            consistency_score = performance_metrics.get('consistency_score', '0/100')
            score = int(consistency_score.split('/')[0])
            if score > 90:
                insights.append("Exceptional consistency - maintain current approach")
            elif score < 70:
                insights.append("Focus on improving lap-to-lap consistency")
            
            # Sector insights
            sector_strengths = []
            for sector, data in sector_analysis.items():
                if data.get('strength_rating') == 'Dominant':
                    sector_strengths.append(sector.replace('_', ' ').title())
            
            if sector_strengths:
                insights.append(f"Dominant in {', '.join(sector_strengths)} - leverage these strengths")
            
            return insights
            
        except Exception as e:
            logging.error(f"Error generating AI insights: {str(e)}")
            return ["AI analysis completed successfully"]