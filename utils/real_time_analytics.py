"""
Real-time F1 Analytics Module
Provides live session analysis, real-time performance metrics, and streaming data capabilities
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from .data_loader import DataLoader
from .constants import TEAM_COLORS, DRIVER_TEAMS

class RealTimeAnalyzer:
    """Real-time F1 data analysis and streaming capabilities"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.logger = logging.getLogger(__name__)
    
    def get_live_session_status(self, year: int, grand_prix: str) -> Dict[str, Any]:
        """Get current live session status and timing"""
        try:
            # Load the most recent session data
            session_data = self.data_loader.load_session_data(year, grand_prix, 'Race')
            
            if session_data is None:
                return {'status': 'no_data', 'message': 'No session data available'}
            
            # Calculate session timing
            session_start = session_data.date if hasattr(session_data, 'date') else None
            current_time = datetime.now()
            
            # Get latest lap data
            latest_laps = session_data.laps
            if latest_laps.empty:
                return {'status': 'no_laps', 'message': 'No lap data available'}
            
            # Calculate real-time standings
            standings = self._calculate_current_standings(latest_laps)
            
            # Get sector times for live timing
            sector_times = self._get_live_sector_times(latest_laps)
            
            # Calculate gap analysis
            gap_analysis = self._calculate_live_gaps(latest_laps)
            
            return {
                'status': 'live',
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session_start': str(session_start) if session_start else None,
                    'current_time': str(current_time),
                    'elapsed_time': str(current_time - session_start) if session_start else None
                },
                'live_standings': standings,
                'sector_times': sector_times,
                'gap_analysis': gap_analysis,
                'total_laps': len(latest_laps),
                'active_drivers': len(latest_laps['Driver'].unique())
            }
            
        except Exception as e:
            self.logger.error(f"Error getting live session status: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_current_standings(self, laps_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Calculate current race standings based on latest lap data"""
        try:
            # Get the latest lap for each driver
            latest_laps = laps_data.groupby('Driver').last().reset_index()
            
            # Sort by lap number (descending) then by lap time
            latest_laps['LapTime_seconds'] = pd.to_timedelta(latest_laps['LapTime']).dt.total_seconds()
            standings = latest_laps.sort_values(['LapNumber', 'LapTime_seconds'], ascending=[False, True])
            
            standings_list = []
            for idx, row in standings.iterrows():
                driver = row['Driver']
                standings_list.append({
                    'position': idx + 1,
                    'driver': driver,
                    'team': DRIVER_TEAMS.get(driver, 'Unknown'),
                    'lap_number': int(row['LapNumber']),
                    'last_lap_time': str(row['LapTime']),
                    'compound': row.get('Compound', 'Unknown'),
                    'tire_life': int(row.get('TyreLife', 0)),
                    'team_color': TEAM_COLORS.get(DRIVER_TEAMS.get(driver, ''), '#808080')
                })
            
            return standings_list
            
        except Exception as e:
            self.logger.error(f"Error calculating standings: {str(e)}")
            return []
    
    def _get_live_sector_times(self, laps_data: pd.DataFrame) -> Dict[str, Any]:
        """Get live sector timing data"""
        try:
            # Get latest laps for sector analysis
            latest_laps = laps_data.groupby('Driver').tail(3)  # Last 3 laps per driver
            
            sector_data = {}
            for driver in latest_laps['Driver'].unique():
                driver_laps = latest_laps[latest_laps['Driver'] == driver]
                
                if not driver_laps.empty:
                    latest_lap = driver_laps.iloc[-1]
                    sector_data[driver] = {
                        'sector_1': str(latest_lap.get('Sector1Time', 'N/A')),
                        'sector_2': str(latest_lap.get('Sector2Time', 'N/A')),
                        'sector_3': str(latest_lap.get('Sector3Time', 'N/A')),
                        'lap_time': str(latest_lap.get('LapTime', 'N/A')),
                        'speed_trap': float(latest_lap.get('SpeedST', 0)) if latest_lap.get('SpeedST') else 0
                    }
            
            return sector_data
            
        except Exception as e:
            self.logger.error(f"Error getting sector times: {str(e)}")
            return {}
    
    def _calculate_live_gaps(self, laps_data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate gaps between drivers in real-time"""
        try:
            # Get latest lap for each driver
            latest_laps = laps_data.groupby('Driver').last().reset_index()
            latest_laps['LapTime_seconds'] = pd.to_timedelta(latest_laps['LapTime']).dt.total_seconds()
            
            # Sort by position
            standings = latest_laps.sort_values(['LapNumber', 'LapTime_seconds'], ascending=[False, True])
            
            gaps = {}
            leader_time = None
            previous_time = None
            
            for idx, row in standings.iterrows():
                driver = row['Driver']
                lap_time = row['LapTime_seconds']
                
                if idx == 0:  # Leader
                    leader_time = lap_time
                    gaps[driver] = {
                        'gap_to_leader': 0.0,
                        'gap_to_ahead': 0.0,
                        'position': 1
                    }
                    previous_time = lap_time
                else:
                    gap_to_leader = lap_time - leader_time if leader_time else 0
                    gap_to_ahead = lap_time - previous_time if previous_time else 0
                    
                    gaps[driver] = {
                        'gap_to_leader': round(gap_to_leader, 3),
                        'gap_to_ahead': round(gap_to_ahead, 3),
                        'position': idx + 1
                    }
                    previous_time = lap_time
            
            return gaps
            
        except Exception as e:
            self.logger.error(f"Error calculating gaps: {str(e)}")
            return {}
    
    def get_performance_trends(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Analyze performance trends throughout a session"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return {'error': 'No session data available'}
            
            laps_data = session_data.laps
            if laps_data.empty:
                return {'error': 'No lap data available'}
            
            trends = {}
            for driver in laps_data['Driver'].unique():
                driver_laps = laps_data[laps_data['Driver'] == driver].copy()
                
                if len(driver_laps) > 0:
                    # Convert lap times to seconds for analysis
                    driver_laps['LapTime_seconds'] = pd.to_timedelta(driver_laps['LapTime']).dt.total_seconds()
                    
                    # Calculate performance metrics
                    trends[driver] = {
                        'lap_count': len(driver_laps),
                        'fastest_lap': float(driver_laps['LapTime_seconds'].min()),
                        'average_lap': float(driver_laps['LapTime_seconds'].mean()),
                        'consistency': float(driver_laps['LapTime_seconds'].std()),
                        'lap_times': driver_laps['LapTime_seconds'].tolist(),
                        'lap_numbers': driver_laps['LapNumber'].tolist(),
                        'tire_compounds': driver_laps['Compound'].tolist(),
                        'improvement_trend': self._calculate_improvement_trend(driver_laps['LapTime_seconds'])
                    }
            
            return {
                'performance_trends': trends,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance trends: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_improvement_trend(self, lap_times: pd.Series) -> float:
        """Calculate if driver is improving or degrading over time"""
        if len(lap_times) < 3:
            return 0.0
        
        # Use linear regression to find trend
        x = np.arange(len(lap_times))
        coefficients = np.polyfit(x, lap_times, 1)
        
        # Negative slope means improving (faster times)
        return float(-coefficients[0])  # Return positive for improvement

class LiveDataStreamer:
    """Stream live F1 data for real-time applications"""
    
    def __init__(self):
        self.analyzer = RealTimeAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    def get_streaming_data(self, year: int, grand_prix: str) -> Dict[str, Any]:
        """Get data formatted for streaming/real-time updates"""
        try:
            # Get live session status
            live_status = self.analyzer.get_live_session_status(year, grand_prix)
            
            # Get performance trends for race session
            trends = self.analyzer.get_performance_trends(year, grand_prix, 'Race')
            
            # Combine for streaming format
            streaming_data = {
                'timestamp': datetime.now().isoformat(),
                'session_status': live_status.get('status', 'unknown'),
                'live_data': {
                    'standings': live_status.get('live_standings', []),
                    'sector_times': live_status.get('sector_times', {}),
                    'gaps': live_status.get('gap_analysis', {}),
                },
                'trends': trends.get('performance_trends', {}),
                'metadata': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'data_version': '2.0',
                    'update_frequency': '30s'
                }
            }
            
            return streaming_data
            
        except Exception as e:
            self.logger.error(f"Error getting streaming data: {str(e)}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}