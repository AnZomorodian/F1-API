"""
Telemetry Data Visualization Module
Advanced telemetry visualization and analysis for F1 data
"""

import fastf1
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

class TelemetryVisualizer:
    """Advanced telemetry visualization and analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def create_telemetry_comparison_chart(self, year: int, grand_prix: str, session: str, 
                                        drivers: List[str], lap_type: str = 'fastest') -> Dict[str, Any]:
        """Create comprehensive telemetry comparison charts"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            # Prepare data for visualization
            telemetry_data = {}
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98FB98', '#F4A460']
            
            for idx, driver in enumerate(drivers[:len(colors)]):
                try:
                    driver_laps = session_obj.laps.pick_driver(driver)
                    if not driver_laps.empty:
                        if lap_type == 'fastest':
                            lap = driver_laps.pick_fastest()
                        else:
                            lap = driver_laps.iloc[0]  # First lap
                        
                        if lap is not None:
                            telemetry = lap.get_telemetry()
                            
                            telemetry_data[driver] = {
                                'lap_time': str(lap['LapTime']),
                                'color': colors[idx],
                                'data': {
                                    'distance': telemetry['Distance'].tolist(),
                                    'speed': telemetry['Speed'].tolist(),
                                    'throttle': telemetry['Throttle'].tolist(),
                                    'brake': telemetry['Brake'].tolist(),
                                    'rpm': telemetry['RPM'].tolist(),
                                    'gear': telemetry['nGear'].tolist(),
                                    'drs': telemetry['DRS'].tolist() if 'DRS' in telemetry.columns else []
                                }
                            }
                
                except Exception as driver_error:
                    self.logger.warning(f"Error processing driver {driver}: {str(driver_error)}")
                    continue
            
            # Create multi-subplot visualization
            charts = self._create_telemetry_subplots(telemetry_data)
            
            return {
                'telemetry_charts': charts,
                'drivers': list(telemetry_data.keys()),
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session,
                    'lap_type': lap_type
                },
                'chart_config': {
                    'responsive': True,
                    'displayModeBar': True,
                    'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error creating telemetry comparison chart: {str(e)}")
            return {'error': str(e)}
    
    def _create_telemetry_subplots(self, telemetry_data: Dict) -> Dict[str, Any]:
        """Create telemetry subplots for different metrics"""
        charts = {}
        
        # Speed comparison chart
        charts['speed_chart'] = self._create_speed_chart(telemetry_data)
        
        # Throttle and Brake chart
        charts['throttle_brake_chart'] = self._create_throttle_brake_chart(telemetry_data)
        
        # RPM and Gear chart
        charts['rpm_gear_chart'] = self._create_rpm_gear_chart(telemetry_data)
        
        # DRS usage chart
        charts['drs_chart'] = self._create_drs_chart(telemetry_data)
        
        return charts
    
    def _create_speed_chart(self, telemetry_data: Dict) -> Dict[str, Any]:
        """Create speed comparison chart"""
        fig = go.Figure()
        
        for driver, data in telemetry_data.items():
            fig.add_trace(go.Scatter(
                x=data['data']['distance'],
                y=data['data']['speed'],
                mode='lines',
                name=f"{driver} ({data['lap_time']})",
                line=dict(color=data['color'], width=2),
                hovertemplate=f"<b>{driver}</b><br>" +
                             "Distance: %{x:.0f}m<br>" +
                             "Speed: %{y:.0f} km/h<br>" +
                             "<extra></extra>"
            ))
        
        fig.update_layout(
            title="Speed Comparison by Distance",
            xaxis_title="Distance (m)",
            yaxis_title="Speed (km/h)",
            hovermode='x unified',
            template='plotly_dark',
            height=400
        )
        
        return fig.to_dict()
    
    def _create_throttle_brake_chart(self, telemetry_data: Dict) -> Dict[str, Any]:
        """Create throttle and brake comparison chart"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Throttle Position (%)', 'Brake Pressure'),
            shared_xaxes=True,
            vertical_spacing=0.1
        )
        
        for driver, data in telemetry_data.items():
            # Throttle
            fig.add_trace(
                go.Scatter(
                    x=data['data']['distance'],
                    y=data['data']['throttle'],
                    mode='lines',
                    name=f"{driver} Throttle",
                    line=dict(color=data['color'], width=2),
                    showlegend=True
                ),
                row=1, col=1
            )
            
            # Brake
            fig.add_trace(
                go.Scatter(
                    x=data['data']['distance'],
                    y=data['data']['brake'],
                    mode='lines',
                    name=f"{driver} Brake",
                    line=dict(color=data['color'], width=2, dash='dot'),
                    showlegend=False
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title="Throttle and Brake Analysis",
            height=600,
            template='plotly_dark'
        )
        
        fig.update_xaxes(title_text="Distance (m)", row=2, col=1)
        fig.update_yaxes(title_text="Throttle (%)", row=1, col=1)
        fig.update_yaxes(title_text="Brake", row=2, col=1)
        
        return fig.to_dict()
    
    def _create_rpm_gear_chart(self, telemetry_data: Dict) -> Dict[str, Any]:
        """Create RPM and gear comparison chart"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Engine RPM', 'Gear Selection'),
            shared_xaxes=True,
            vertical_spacing=0.1
        )
        
        for driver, data in telemetry_data.items():
            # RPM
            fig.add_trace(
                go.Scatter(
                    x=data['data']['distance'],
                    y=data['data']['rpm'],
                    mode='lines',
                    name=f"{driver} RPM",
                    line=dict(color=data['color'], width=2),
                    showlegend=True
                ),
                row=1, col=1
            )
            
            # Gear
            fig.add_trace(
                go.Scatter(
                    x=data['data']['distance'],
                    y=data['data']['gear'],
                    mode='lines',
                    name=f"{driver} Gear",
                    line=dict(color=data['color'], width=2),
                    showlegend=False
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title="RPM and Gear Analysis",
            height=600,
            template='plotly_dark'
        )
        
        fig.update_xaxes(title_text="Distance (m)", row=2, col=1)
        fig.update_yaxes(title_text="RPM", row=1, col=1)
        fig.update_yaxes(title_text="Gear", row=2, col=1)
        
        return fig.to_dict()
    
    def _create_drs_chart(self, telemetry_data: Dict) -> Dict[str, Any]:
        """Create DRS usage chart"""
        fig = go.Figure()
        
        for driver, data in telemetry_data.items():
            if data['data']['drs']:  # Only if DRS data is available
                # Convert DRS data to zones (0 or 1)
                drs_zones = [1 if x > 0 else 0 for x in data['data']['drs']]
                
                fig.add_trace(go.Scatter(
                    x=data['data']['distance'],
                    y=drs_zones,
                    mode='lines',
                    name=f"{driver} DRS",
                    line=dict(color=data['color'], width=3),
                    fill='tonexty' if driver != list(telemetry_data.keys())[0] else None
                ))
        
        fig.update_layout(
            title="DRS Usage by Distance",
            xaxis_title="Distance (m)",
            yaxis_title="DRS Active",
            yaxis=dict(tickmode='array', tickvals=[0, 1], ticktext=['Closed', 'Open']),
            template='plotly_dark',
            height=300
        )
        
        return fig.to_dict()
    
    def create_sector_time_analysis(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Create sector time analysis visualization"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            sector_data = []
            drivers = session_obj.drivers
            
            for driver in drivers:
                try:
                    driver_laps = session_obj.laps.pick_driver(driver)
                    if not driver_laps.empty:
                        # Get best sectors
                        best_s1 = driver_laps['Sector1Time'].min()
                        best_s2 = driver_laps['Sector2Time'].min()
                        best_s3 = driver_laps['Sector3Time'].min()
                        
                        # Convert to seconds for easier handling
                        sector_data.append({
                            'driver': driver,
                            'sector_1': best_s1.total_seconds() if pd.notna(best_s1) else None,
                            'sector_2': best_s2.total_seconds() if pd.notna(best_s2) else None,
                            'sector_3': best_s3.total_seconds() if pd.notna(best_s3) else None,
                            'theoretical_best': (best_s1 + best_s2 + best_s3).total_seconds() if all(pd.notna(x) for x in [best_s1, best_s2, best_s3]) else None
                        })
                
                except Exception as driver_error:
                    self.logger.warning(f"Error processing driver {driver} sectors: {str(driver_error)}")
                    continue
            
            # Create sector comparison chart
            sector_chart = self._create_sector_comparison_chart(sector_data)
            
            return {
                'sector_analysis': sector_data,
                'sector_chart': sector_chart,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error creating sector analysis: {str(e)}")
            return {'error': str(e)}
    
    def _create_sector_comparison_chart(self, sector_data: List[Dict]) -> Dict[str, Any]:
        """Create sector time comparison chart"""
        drivers = [d['driver'] for d in sector_data if d['sector_1'] is not None]
        sector_1_times = [d['sector_1'] for d in sector_data if d['sector_1'] is not None]
        sector_2_times = [d['sector_2'] for d in sector_data if d['sector_2'] is not None]
        sector_3_times = [d['sector_3'] for d in sector_data if d['sector_3'] is not None]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=drivers,
            y=sector_1_times,
            name='Sector 1',
            marker_color='#FF6B6B'
        ))
        
        fig.add_trace(go.Bar(
            x=drivers,
            y=sector_2_times,
            name='Sector 2',
            marker_color='#4ECDC4'
        ))
        
        fig.add_trace(go.Bar(
            x=drivers,
            y=sector_3_times,
            name='Sector 3',
            marker_color='#45B7D1'
        ))
        
        fig.update_layout(
            title="Best Sector Times Comparison",
            xaxis_title="Drivers",
            yaxis_title="Time (seconds)",
            barmode='group',
            template='plotly_dark',
            height=500
        )
        
        return fig.to_dict()
    
    def create_lap_time_evolution(self, year: int, grand_prix: str, session: str, 
                                 drivers: List[str]) -> Dict[str, Any]:
        """Create lap time evolution chart throughout the session"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            fig = go.Figure()
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            
            for idx, driver in enumerate(drivers[:len(colors)]):
                try:
                    driver_laps = session_obj.laps.pick_driver(driver)
                    if not driver_laps.empty:
                        lap_numbers = driver_laps['LapNumber'].tolist()
                        lap_times = [lap_time.total_seconds() for lap_time in driver_laps['LapTime'] if pd.notna(lap_time)]
                        
                        if lap_times:
                            fig.add_trace(go.Scatter(
                                x=lap_numbers[:len(lap_times)],
                                y=lap_times,
                                mode='lines+markers',
                                name=driver,
                                line=dict(color=colors[idx], width=2),
                                marker=dict(size=4)
                            ))
                
                except Exception as driver_error:
                    self.logger.warning(f"Error processing driver {driver} lap evolution: {str(driver_error)}")
                    continue
            
            fig.update_layout(
                title="Lap Time Evolution",
                xaxis_title="Lap Number",
                yaxis_title="Lap Time (seconds)",
                template='plotly_dark',
                height=500,
                hovermode='x unified'
            )
            
            return {
                'lap_evolution_chart': fig.to_dict(),
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error creating lap time evolution: {str(e)}")
            return {'error': str(e)}