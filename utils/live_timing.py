"""
Live Timing and Real-time Data Analysis Module
Enhanced F1 data analysis with live timing features
"""

import fastf1
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class LiveTimingAnalyzer:
    """Enhanced live timing and real-time data analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_live_session_status(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Get current session status and live timing information"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            # Get session information
            session_info = {
                'session_type': session,
                'date': str(session_obj.date) if hasattr(session_obj, 'date') else None,
                'total_laps': len(session_obj.laps) if hasattr(session_obj, 'laps') else 0,
                'active_drivers': len(session_obj.drivers) if hasattr(session_obj, 'drivers') else 0,
                'circuit_info': {
                    'name': session_obj.event.Location if hasattr(session_obj, 'event') else None,
                    'country': session_obj.event.Country if hasattr(session_obj, 'event') else None,
                    'circuit_name': session_obj.event.EventName if hasattr(session_obj, 'event') else None
                }
            }
            
            # Add track status information if available
            if hasattr(session_obj, 'track_status'):
                track_status = session_obj.track_status
                session_info['track_status'] = {
                    'current_status': track_status.iloc[-1]['Status'] if not track_status.empty else 'Unknown',
                    'status_changes': len(track_status),
                    'safety_car_periods': len(track_status[track_status['Status'].isin(['2', '4', '6'])]) if not track_status.empty else 0
                }
            
            return session_info
            
        except Exception as e:
            self.logger.error(f"Error getting live session status: {str(e)}")
            return {'error': str(e)}
    
    def get_current_standings(self, year: int, grand_prix: str) -> Dict[str, Any]:
        """Get current championship standings and race results"""
        try:
            # Get race session
            race_session = fastf1.get_session(year, grand_prix, 'Race')
            race_session.load()
            
            standings = {}
            
            if hasattr(race_session, 'results') and race_session.results is not None:
                results = race_session.results
                standings['race_results'] = []
                
                for idx, row in results.iterrows():
                    driver_result = {
                        'position': row.get('Position', 'N/A'),
                        'driver': row.get('Abbreviation', 'N/A'),
                        'driver_name': f"{row.get('FirstName', '')} {row.get('LastName', '')}".strip(),
                        'team': row.get('TeamName', 'N/A'),
                        'time': str(row.get('Time', 'N/A')),
                        'status': row.get('Status', 'N/A'),
                        'points': row.get('Points', 0)
                    }
                    standings['race_results'].append(driver_result)
            
            return standings
            
        except Exception as e:
            self.logger.error(f"Error getting current standings: {str(e)}")
            return {'error': str(e)}
    
    def get_sector_analysis(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Enhanced sector time analysis with detailed breakdowns"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            sector_data = {}
            
            for driver in session_obj.drivers:
                try:
                    driver_laps = session_obj.laps.pick_driver(driver)
                    if not driver_laps.empty:
                        # Get best sectors
                        sector_1_best = driver_laps['Sector1Time'].min()
                        sector_2_best = driver_laps['Sector2Time'].min()
                        sector_3_best = driver_laps['Sector3Time'].min()
                        
                        # Calculate theoretical best lap
                        theoretical_best = sector_1_best + sector_2_best + sector_3_best
                        
                        # Get actual fastest lap
                        fastest_lap = driver_laps.pick_fastest()
                        
                        sector_data[driver] = {
                            'sector_1_best': str(sector_1_best),
                            'sector_2_best': str(sector_2_best),
                            'sector_3_best': str(sector_3_best),
                            'theoretical_best': str(theoretical_best),
                            'fastest_lap_actual': str(fastest_lap['LapTime']),
                            'time_loss': str(fastest_lap['LapTime'] - theoretical_best),
                            'sector_consistency': {
                                'sector_1_std': float(driver_laps['Sector1Time'].std()),
                                'sector_2_std': float(driver_laps['Sector2Time'].std()),
                                'sector_3_std': float(driver_laps['Sector3Time'].std())
                            }
                        }
                
                except Exception as driver_error:
                    self.logger.warning(f"Error processing driver {driver} sectors: {str(driver_error)}")
                    continue
            
            return {
                'sector_analysis': sector_data,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting sector analysis: {str(e)}")
            return {'error': str(e)}
    
    def get_pit_stop_analysis(self, year: int, grand_prix: str) -> Dict[str, Any]:
        """Enhanced pit stop analysis with strategic insights"""
        try:
            race_session = fastf1.get_session(year, grand_prix, 'Race')
            race_session.load()
            
            pit_stops = {}
            
            # Get pit stop data
            if hasattr(race_session, 'laps'):
                laps = race_session.laps
                
                for driver in race_session.drivers:
                    try:
                        driver_laps = laps.pick_driver(driver)
                        if not driver_laps.empty:
                            # Find pit stops (where PitInTime or PitOutTime is not null)
                            pit_laps = driver_laps[
                                (driver_laps['PitInTime'].notna()) | 
                                (driver_laps['PitOutTime'].notna())
                            ]
                            
                            if not pit_laps.empty:
                                pit_stop_data = []
                                for idx, lap in pit_laps.iterrows():
                                    pit_stop = {
                                        'lap_number': lap['LapNumber'],
                                        'pit_in_time': str(lap.get('PitInTime', 'N/A')),
                                        'pit_out_time': str(lap.get('PitOutTime', 'N/A')),
                                        'pit_duration': str(lap.get('PitOutTime', pd.NaT) - lap.get('PitInTime', pd.NaT)) if pd.notna(lap.get('PitInTime')) and pd.notna(lap.get('PitOutTime')) else 'N/A',
                                        'tire_compound_before': lap.get('Compound', 'Unknown'),
                                        'tire_life_before': lap.get('TyreLife', 0)
                                    }
                                    pit_stop_data.append(pit_stop)
                                
                                pit_stops[driver] = {
                                    'total_pit_stops': len(pit_stop_data),
                                    'pit_stops': pit_stop_data,
                                    'average_pit_duration': 'N/A'  # Would need more detailed timing data
                                }
                    
                    except Exception as driver_error:
                        self.logger.warning(f"Error processing driver {driver} pit stops: {str(driver_error)}")
                        continue
            
            return {
                'pit_stop_analysis': pit_stops,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting pit stop analysis: {str(e)}")
            return {'error': str(e)}
    
    def get_drs_usage_analysis(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Analyze DRS (Drag Reduction System) usage patterns"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            drs_analysis = {}
            
            for driver in session_obj.drivers:
                try:
                    driver_laps = session_obj.laps.pick_driver(driver)
                    if not driver_laps.empty:
                        fastest_lap = driver_laps.pick_fastest()
                        telemetry = fastest_lap.get_telemetry()
                        
                        if 'DRS' in telemetry.columns:
                            drs_data = telemetry['DRS']
                            total_distance = telemetry['Distance'].max() - telemetry['Distance'].min()
                            drs_distance = len(drs_data[drs_data > 0]) * (total_distance / len(telemetry))
                            
                            drs_analysis[driver] = {
                                'drs_activation_count': len(drs_data[drs_data.diff() > 0]),
                                'total_drs_distance': float(drs_distance),
                                'drs_percentage': float((drs_distance / total_distance) * 100) if total_distance > 0 else 0,
                                'lap_time': str(fastest_lap['LapTime'])
                            }
                
                except Exception as driver_error:
                    self.logger.warning(f"Error processing driver {driver} DRS: {str(driver_error)}")
                    continue
            
            return {
                'drs_analysis': drs_analysis,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting DRS analysis: {str(e)}")
            return {'error': str(e)}