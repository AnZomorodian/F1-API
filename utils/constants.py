# F1 Constants and Configuration

# Team Colors (2024 season)
TEAM_COLORS = {
    'Red Bull Racing': '#3671C6',
    'Mercedes': '#6CD3BF',
    'Ferrari': '#F91536',
    'McLaren': '#F58020',
    'Aston Martin': '#358C75',
    'Alpine': '#2293D1',
    'Williams': '#37003C',
    'AlphaTauri': '#5E8FAA',
    'Alfa Romeo': '#C92D4B',
    'Haas': '#B6BABD'
}

# Driver Teams (2024 season)
DRIVER_TEAMS = {
    'VER': 'Red Bull Racing',
    'PER': 'Red Bull Racing',
    'HAM': 'Mercedes',
    'RUS': 'Mercedes',
    'LEC': 'Ferrari',
    'SAI': 'Ferrari',
    'NOR': 'McLaren',
    'PIA': 'McLaren',
    'ALO': 'Aston Martin',
    'STR': 'Aston Martin',
    'GAS': 'Alpine',
    'OCO': 'Alpine',
    'ALB': 'Williams',
    'SAR': 'Williams',
    'TSU': 'AlphaTauri',
    'RIC': 'AlphaTauri',
    'BOT': 'Alfa Romeo',
    'ZHO': 'Alfa Romeo',
    'MAG': 'Haas',
    'HUL': 'Haas'
}

# Grands Prix (2024 season)
GRANDS_PRIX = [
    'Bahrain', 'Saudi Arabia', 'Australia', 'Japan', 'China',
    'Miami', 'Italy', 'Monaco', 'Canada', 'Spain',
    'Austria', 'Great Britain', 'Hungary', 'Belgium', 'Netherlands',
    'Italy', 'Azerbaijan', 'Singapore', 'United States', 'Mexico',
    'Brazil', 'Las Vegas', 'Qatar', 'Abu Dhabi'
]

# Session Types
SESSIONS = [
    'Practice 1',
    'Practice 2', 
    'Practice 3',
    'Sprint Shootout',
    'Sprint',
    'Qualifying',
    'Race'
]

# Tire Colors
TIRE_COLORS = {
    'SOFT': '#FF3333',
    'MEDIUM': '#FFF200',
    'HARD': '#EBEBEB',
    'INTERMEDIATE': '#43B02A',
    'WET': '#0067AD'
}

# Track Information
TRACK_INFO = {
    'Bahrain': {
        'length': 5.412,
        'turns': 15,
        'drs_zones': 3
    },
    'Saudi Arabia': {
        'length': 6.174,
        'turns': 27,
        'drs_zones': 3
    },
    'Australia': {
        'length': 5.278,
        'turns': 14,
        'drs_zones': 2
    },
    # Add more tracks as needed
}

# Performance Metrics
PERFORMANCE_METRICS = [
    'lap_time',
    'sector_1_time',
    'sector_2_time', 
    'sector_3_time',
    'speed_trap',
    'max_speed',
    'avg_speed',
    'tire_degradation',
    'fuel_consumption'
]

# Telemetry Channels
TELEMETRY_CHANNELS = [
    'Speed',
    'Throttle',
    'Brake',
    'RPM',
    'nGear',
    'Distance',
    'Time',
    'SessionTime'
]
