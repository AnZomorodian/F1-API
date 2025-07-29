
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
    """Advanced telemetry visualization with interactive charts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.driver_colors = {
            'VER': '#0600EF', 'HAM': '#00D2BE', 'LEC': '#DC143C', 'RUS': '#00D2BE',
            'SAI': '#DC143C', 'NOR': '#FF8700', 'PIA': '#FF8700', 'ALO': '#006F62',
            'STR': '#006F62', 'GAS': '#0090FF', 'OCO': '#0090FF', 'ALB': '#005AFF',
            'TSU': '#005AFF', 'RIC': '#005AFF', 'HUL': '#FFFFFF', 'MAG': '#FFFFFF',
            'ZHO': '#900000', 'BOT': '#900000', 'SAR': '#E80020', 'COL': '#E80020'
        }
    
    def create_telemetry_comparison_chart(self, year: int, grand_prix: str, session: str, 
                                        drivers: List[str], lap_type: str = 'fastest') -> Dict[str, Any]:
        """Create comprehensive telemetry comparison charts"""
        try:
            # Load session data
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            telemetry_data = {}
            
            # Get telemetry for each driver
            for driver in drivers:
                try:
                    driver_laps = session_obj.laps.pick_drivers(driver)
                    if not driver_laps.empty:
                        if lap_type == 'fastest':
                            selected_lap = driver_laps.pick_fastest()
                        elif lap_type == 'first':
                            selected_lap = driver_laps.iloc[0]
                        else:  # last
                            selected_lap = driver_laps.iloc[-1]
                        
                        if selected_lap is not None and hasattr(selected_lap, 'get_telemetry'):
                            telemetry = selected_lap.get_telemetry()
                            
                            telemetry_data[driver] = {
                                'data': {
                                    'distance': telemetry['Distance'].tolist(),
                                    'speed': telemetry['Speed'].tolist(),
                                    'throttle': telemetry['Throttle'].tolist(),
                                    'brake': telemetry['Brake'].tolist(),
                                    'rpm': telemetry['RPM'].tolist(),
                                    'gear': telemetry['nGear'].tolist(),
                                    'drs': telemetry['DRS'].tolist() if 'DRS' in telemetry.columns else [0] * len(telemetry)
                                },
                                'lap_time': str(selected_lap['LapTime']),
                                'color': self.driver_colors.get(driver, '#FF6B6B')
                            }
                except Exception as driver_error:
                    self.logger.warning(f"Error processing driver {driver}: {str(driver_error)}")
                    continue
            
            if not telemetry_data:
                return {'error': 'No telemetry data available for selected drivers'}
            
            # Create charts
            charts = self._create_telemetry_subplots(telemetry_data)
            
            return {
                'telemetry_charts': charts,
                'drivers_processed': list(telemetry_data.keys()),
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session,
                    'lap_type': lap_type
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
                line=dict(color=data['color'], width=3),
                hovertemplate=f"<b>{driver}</b><br>" +
                             "Distance: %{x:.0f}m<br>" +
                             "Speed: %{y:.0f} km/h<br>" +
                             "<extra></extra>"
            ))
        
        fig.update_layout(
            title="Speed Comparison",
            xaxis_title="Distance (m)",
            yaxis_title="Speed (km/h)",
            hovermode='x unified'
        )
        
        return {
            'data': fig.data,
            'layout': fig.layout
        }
    
    def _create_throttle_brake_chart(self, telemetry_data: Dict) -> Dict[str, Any]:
        """Create throttle and brake comparison chart"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Throttle Position (%)', 'Brake Pressure'),
            shared_xaxes=True,
            vertical_spacing=0.1
        )
        
        for driver, data in telemetry_data.items():
            # Throttle trace
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
            
            # Brake trace
            fig.add_trace(
                go.Scatter(
                    x=data['data']['distance'],
                    y=data['data']['brake'],
                    mode='lines',
                    name=f"{driver} Brake",
                    line=dict(color=data['color'], width=2, dash='dash'),
                    showlegend=True
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title="Throttle & Brake Analysis",
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Distance (m)", row=2, col=1)
        fig.update_yaxes(title_text="Throttle (%)", row=1, col=1)
        fig.update_yaxes(title_text="Brake", row=2, col=1)
        
        return {
            'data': fig.data,
            'layout': fig.layout
        }
    
    def _create_rpm_gear_chart(self, telemetry_data: Dict) -> Dict[str, Any]:
        """Create RPM and gear comparison chart"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Engine RPM', 'Gear Selection'),
            shared_xaxes=True,
            vertical_spacing=0.1
        )
        
        for driver, data in telemetry_data.items():
            # RPM trace
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
            
            # Gear trace
            fig.add_trace(
                go.Scatter(
                    x=data['data']['distance'],
                    y=data['data']['gear'],
                    mode='lines+markers',
                    name=f"{driver} Gear",
                    line=dict(color=data['color'], width=2),
                    marker=dict(size=4),
                    showlegend=True
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            title="Engine Performance Analysis",
            hovermode='x unified'
        )
        
        fig.update_xaxes(title_text="Distance (m)", row=2, col=1)
        fig.update_yaxes(title_text="RPM", row=1, col=1)
        fig.update_yaxes(title_text="Gear", row=2, col=1)
        
        return {
            'data': fig.data,
            'layout': fig.layout
        }
    
    def _create_drs_chart(self, telemetry_data: Dict) -> Dict[str, Any]:
        """Create DRS usage chart"""
        fig = go.Figure()
        
        for driver, data in telemetry_data.items():
            fig.add_trace(go.Scatter(
                x=data['data']['distance'],
                y=data['data']['drs'],
                mode='lines',
                name=f"{driver} DRS",
                line=dict(color=data['color'], width=2),
                fill='tonexty' if len(fig.data) > 0 else None
            ))
        
        fig.update_layout(
            title="DRS Usage",
            xaxis_title="Distance (m)",
            yaxis_title="DRS Open",
            hovermode='x unified'
        )
        
        return {
            'data': fig.data,
            'layout': fig.layout
        }
    
    def create_sector_time_analysis(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Create sector time analysis chart"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            sector_data = []
            
            for driver in session_obj.drivers:
                try:
                    driver_laps = session_obj.laps.pick_drivers(driver)
                    if not driver_laps.empty:
                        fastest_lap = driver_laps.pick_fastest()
                        if fastest_lap is not None:
                            sector_data.append({
                                'Driver': driver,
                                'Sector1': fastest_lap['Sector1Time'].total_seconds() if pd.notna(fastest_lap['Sector1Time']) else 0,
                                'Sector2': fastest_lap['Sector2Time'].total_seconds() if pd.notna(fastest_lap['Sector2Time']) else 0,
                                'Sector3': fastest_lap['Sector3Time'].total_seconds() if pd.notna(fastest_lap['Sector3Time']) else 0
                            })
                except Exception:
                    continue
            
            if not sector_data:
                return {'error': 'No sector data available'}
            
            df = pd.DataFrame(sector_data)
            
            fig = go.Figure()
            
            sectors = ['Sector1', 'Sector2', 'Sector3']
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
            
            for i, sector in enumerate(sectors):
                fig.add_trace(go.Bar(
                    name=f'Sector {i+1}',
                    x=df['Driver'],
                    y=df[sector],
                    marker_color=colors[i]
                ))
            
            fig.update_layout(
                title='Sector Time Comparison (Best Lap)',
                barmode='group',
                xaxis_title='Driver',
                yaxis_title='Time (seconds)',
                hovermode='x unified'
            )
            
            return {
                'sector_analysis': {
                    'data': fig.data,
                    'layout': fig.layout
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error creating sector analysis: {str(e)}")
            return {'error': str(e)}
    
    def create_lap_time_evolution(self, year: int, grand_prix: str, session: str, drivers: List[str]) -> Dict[str, Any]:
        """Create lap time evolution chart"""
        try:
            session_obj = fastf1.get_session(year, grand_prix, session)
            session_obj.load()
            
            fig = go.Figure()
            
            for driver in drivers:
                try:
                    driver_laps = session_obj.laps.pick_drivers(driver)
                    if not driver_laps.empty:
                        lap_numbers = driver_laps['LapNumber'].tolist()
                        lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'] if pd.notna(lt)]
                        
                        if lap_times and len(lap_times) == len(lap_numbers):
                            fig.add_trace(go.Scatter(
                                x=lap_numbers,
                                y=lap_times,
                                mode='lines+markers',
                                name=driver,
                                line=dict(color=self.driver_colors.get(driver, '#FF6B6B'), width=2),
                                marker=dict(size=4)
                            ))
                except Exception:
                    continue
            
            fig.update_layout(
                title='Lap Time Evolution',
                xaxis_title='Lap Number',
                yaxis_title='Lap Time (seconds)',
                hovermode='x unified'
            )
            
            return {
                'lap_evolution': {
                    'data': fig.data,
                    'layout': fig.layout
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error creating lap evolution: {str(e)}")
            return {'error': str(e)}
