import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils.constants import TEAM_COLORS, TIRE_COLORS

def create_telemetry_plot(telemetry_data, drivers):
    """Create telemetry comparison plot"""
    try:
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=['Speed', 'Throttle', 'Brake', 'RPM'],
            vertical_spacing=0.08
        )
        
        colors = ['#FF0000', '#0000FF', '#00FF00', '#FF00FF', '#FFFF00']
        
        for i, driver in enumerate(drivers):
            if driver in telemetry_data:
                data = telemetry_data[driver]
                color = colors[i % len(colors)]
                
                # Speed plot
                fig.add_trace(
                    go.Scatter(
                        x=data['distance'],
                        y=data['speed'],
                        name=f"{driver} Speed",
                        line=dict(color=color),
                        legendgroup=driver
                    ),
                    row=1, col=1
                )
                
                # Throttle plot
                fig.add_trace(
                    go.Scatter(
                        x=data['distance'],
                        y=data['throttle'],
                        name=f"{driver} Throttle",
                        line=dict(color=color),
                        legendgroup=driver,
                        showlegend=False
                    ),
                    row=2, col=1
                )
                
                # Brake plot
                fig.add_trace(
                    go.Scatter(
                        x=data['distance'],
                        y=data['brake'],
                        name=f"{driver} Brake",
                        line=dict(color=color),
                        legendgroup=driver,
                        showlegend=False
                    ),
                    row=3, col=1
                )
                
                # RPM plot
                fig.add_trace(
                    go.Scatter(
                        x=data['distance'],
                        y=data['rpm'],
                        name=f"{driver} RPM",
                        line=dict(color=color),
                        legendgroup=driver,
                        showlegend=False
                    ),
                    row=4, col=1
                )
        
        fig.update_layout(
            height=800,
            title="Telemetry Comparison",
            template="plotly_dark"
        )
        
        return fig.to_json()
        
    except Exception as e:
        return None

def create_tire_strategy_plot(tire_data):
    """Create tire strategy visualization"""
    try:
        fig = go.Figure()
        
        for driver, strategy in tire_data.items():
            if 'stints' in strategy:
                for stint in strategy['stints']:
                    fig.add_trace(
                        go.Scatter(
                            x=[stint['start_lap'], stint['end_lap']],
                            y=[driver, driver],
                            mode='lines',
                            line=dict(
                                color=TIRE_COLORS.get(stint['compound'], '#888888'),
                                width=10
                            ),
                            name=f"{driver} - {stint['compound']}",
                            hovertemplate=f"Driver: {driver}<br>Compound: {stint['compound']}<br>Laps: {stint['start_lap']}-{stint['end_lap']}"
                        )
                    )
        
        fig.update_layout(
            title="Tire Strategy by Driver",
            xaxis_title="Lap Number",
            yaxis_title="Driver",
            template="plotly_dark",
            height=600
        )
        
        return fig.to_json()
        
    except Exception as e:
        return None

def create_race_progression_plot(lap_times_data):
    """Create race progression plot showing position changes"""
    try:
        fig = go.Figure()
        
        for driver, data in lap_times_data.items():
            if 'lap_numbers' in data and 'positions' in data:
                fig.add_trace(
                    go.Scatter(
                        x=data['lap_numbers'],
                        y=data['positions'],
                        mode='lines+markers',
                        name=driver,
                        line=dict(width=3),
                        marker=dict(size=6)
                    )
                )
        
        fig.update_layout(
            title="Race Progression - Position Changes",
            xaxis_title="Lap Number",
            yaxis_title="Position",
            yaxis=dict(autorange="reversed"),  # Position 1 at top
            template="plotly_dark",
            height=600
        )
        
        return fig.to_json()
        
    except Exception as e:
        return None

def create_speed_comparison_plot(telemetry_data, drivers):
    """Create speed comparison plot"""
    try:
        fig = go.Figure()
        
        colors = ['#FF0000', '#0000FF', '#00FF00', '#FF00FF', '#FFFF00']
        
        for i, driver in enumerate(drivers):
            if driver in telemetry_data:
                data = telemetry_data[driver]
                color = colors[i % len(colors)]
                
                fig.add_trace(
                    go.Scatter(
                        x=data['distance'],
                        y=data['speed'],
                        name=driver,
                        line=dict(color=color, width=3),
                        mode='lines'
                    )
                )
        
        fig.update_layout(
            title="Speed Comparison",
            xaxis_title="Distance (m)",
            yaxis_title="Speed (km/h)",
            template="plotly_dark",
            height=500
        )
        
        return fig.to_json()
        
    except Exception as e:
        return None

def create_lap_time_distribution(lap_times_data):
    """Create lap time distribution plot"""
    try:
        fig = go.Figure()
        
        for driver, data in lap_times_data.items():
            if 'lap_times' in data:
                # Convert lap times to seconds for plotting
                lap_times_seconds = []
                for lap_time in data['lap_times']:
                    try:
                        # Parse lap time string (format: "M:SS.mmm")
                        if ':' in str(lap_time):
                            parts = str(lap_time).split(':')
                            minutes = int(parts[0])
                            seconds = float(parts[1])
                            total_seconds = minutes * 60 + seconds
                            lap_times_seconds.append(total_seconds)
                    except:
                        continue
                
                if lap_times_seconds:
                    fig.add_trace(
                        go.Box(
                            y=lap_times_seconds,
                            name=driver,
                            boxpoints='all',
                            jitter=0.3,
                            pointpos=-1.8
                        )
                    )
        
        fig.update_layout(
            title="Lap Time Distribution by Driver",
            yaxis_title="Lap Time (seconds)",
            template="plotly_dark",
            height=500
        )
        
        return fig.to_json()
        
    except Exception as e:
        return None
