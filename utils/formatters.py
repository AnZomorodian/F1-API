import pandas as pd
import numpy as np
from datetime import timedelta

def format_lap_time(lap_time):
    """Format lap time to string"""
    if pd.isna(lap_time):
        return "N/A"
    
    if isinstance(lap_time, timedelta):
        total_seconds = lap_time.total_seconds()
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"
    
    return str(lap_time)

def format_sector_time(sector_time):
    """Format sector time to string"""
    if pd.isna(sector_time):
        return "N/A"
    
    if isinstance(sector_time, (int, float)):
        return f"{sector_time:.3f}s"
    
    return str(sector_time)

def get_lap_time_color_class(lap_time, fastest_time):
    """Get color class for lap time based on performance"""
    if pd.isna(lap_time) or pd.isna(fastest_time):
        return "normal"
    
    try:
        if isinstance(lap_time, timedelta):
            lap_seconds = lap_time.total_seconds()
        else:
            lap_seconds = float(lap_time)
            
        if isinstance(fastest_time, timedelta):
            fastest_seconds = fastest_time.total_seconds()
        else:
            fastest_seconds = float(fastest_time)
        
        diff_percent = ((lap_seconds - fastest_seconds) / fastest_seconds) * 100
        
        if diff_percent <= 0.5:
            return "fastest"
        elif diff_percent <= 1.0:
            return "fast"
        elif diff_percent <= 2.0:
            return "medium"
        else:
            return "slow"
            
    except (ValueError, TypeError):
        return "normal"

def get_position_change_text(start_pos, end_pos):
    """Get position change text with direction"""
    if pd.isna(start_pos) or pd.isna(end_pos):
        return "N/A"
    
    change = start_pos - end_pos
    
    if change > 0:
        return f"+{change}"
    elif change < 0:
        return str(change)
    else:
        return "0"

def format_average_lap_time(lap_times):
    """Calculate and format average lap time"""
    if not lap_times or len(lap_times) == 0:
        return "N/A"
    
    try:
        # Convert to seconds if timedelta
        seconds_list = []
        for lap_time in lap_times:
            if pd.isna(lap_time):
                continue
            
            if isinstance(lap_time, timedelta):
                seconds_list.append(lap_time.total_seconds())
            else:
                seconds_list.append(float(lap_time))
        
        if not seconds_list:
            return "N/A"
        
        avg_seconds = np.mean(seconds_list)
        minutes = int(avg_seconds // 60)
        seconds = avg_seconds % 60
        
        return f"{minutes}:{seconds:06.3f}"
        
    except (ValueError, TypeError):
        return "N/A"

def format_speed(speed):
    """Format speed value"""
    if pd.isna(speed):
        return "N/A"
    
    try:
        return f"{float(speed):.1f} km/h"
    except (ValueError, TypeError):
        return "N/A"

def format_percentage(value):
    """Format percentage value"""
    if pd.isna(value):
        return "N/A"
    
    try:
        return f"{float(value):.1f}%"
    except (ValueError, TypeError):
        return "N/A"

def format_distance(distance):
    """Format distance value"""
    if pd.isna(distance):
        return "N/A"
    
    try:
        return f"{float(distance):.0f}m"
    except (ValueError, TypeError):
        return "N/A"

def format_time_delta(time1, time2):
    """Format time difference between two times"""
    if pd.isna(time1) or pd.isna(time2):
        return "N/A"
    
    try:
        if isinstance(time1, timedelta) and isinstance(time2, timedelta):
            diff = time1 - time2
            total_seconds = abs(diff.total_seconds())
            sign = "+" if diff.total_seconds() > 0 else "-"
            
            if total_seconds < 60:
                return f"{sign}{total_seconds:.3f}s"
            else:
                minutes = int(total_seconds // 60)
                seconds = total_seconds % 60
                return f"{sign}{minutes}:{seconds:06.3f}"
        
        return "N/A"
        
    except (ValueError, TypeError):
        return "N/A"
