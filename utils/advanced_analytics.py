import pandas as pd
import numpy as np
from utils.data_loader import DataLoader

class AdvancedF1Analytics:
    """Advanced F1 analytics and insights"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def comprehensive_session_analysis(self, year, grand_prix, session):
        """Comprehensive analysis of a session"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return None
            
            analysis = {
                'performance_analysis': self.analyze_performance_metrics(session_data),
                'consistency_analysis': self.analyze_consistency(session_data),
                'tire_degradation': self.analyze_tire_degradation(session_data),
                'sector_analysis': self.analyze_sector_performance(session_data),
                'race_pace': self.analyze_race_pace(session_data) if session == 'Race' else None
            }
            
            return analysis
            
        except Exception as e:
            return None
    
    def analyze_performance_metrics(self, session_data):
        """Analyze driver performance metrics"""
        try:
            performance_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                fastest_lap = driver_laps.pick_fastest()
                
                performance_data[driver] = {
                    'fastest_lap_time': str(fastest_lap['LapTime']),
                    'average_lap_time': str(driver_laps['LapTime'].mean()),
                    'total_laps': len(driver_laps),
                    'valid_laps': len(driver_laps[driver_laps['IsPersonalBest'] == True]),
                    'position': int(fastest_lap['Position']) if pd.notna(fastest_lap['Position']) else None
                }
                
                # Add telemetry insights
                try:
                    telemetry = fastest_lap.get_telemetry()
                    if not telemetry.empty:
                        performance_data[driver].update({
                            'max_speed': float(telemetry['Speed'].max()),
                            'avg_speed': float(telemetry['Speed'].mean()),
                            'max_rpm': float(telemetry['RPM'].max()),
                            'avg_throttle': float(telemetry['Throttle'].mean())
                        })
                except:
                    pass
            
            return performance_data
            
        except Exception as e:
            return {}
    
    def analyze_consistency(self, session_data):
        """Analyze driver consistency"""
        try:
            consistency_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if len(driver_laps) < 3:  # Need minimum laps for consistency analysis
                    continue
                
                lap_times = driver_laps['LapTime'].dropna()
                if len(lap_times) < 3:
                    continue
                
                # Convert to seconds for calculation
                lap_times_seconds = [lt.total_seconds() for lt in lap_times]
                
                consistency_data[driver] = {
                    'standard_deviation': float(np.std(lap_times_seconds)),
                    'coefficient_of_variation': float(np.std(lap_times_seconds) / np.mean(lap_times_seconds)),
                    'consistency_score': self.calculate_consistency_score(lap_times_seconds),
                    'outlier_laps': self.identify_outlier_laps(lap_times_seconds)
                }
            
            return consistency_data
            
        except Exception as e:
            return {}
    
    def analyze_tire_degradation(self, session_data):
        """Analyze tire degradation patterns"""
        try:
            degradation_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                # Group by stint (tire compound changes)
                stints = []
                current_compound = None
                current_stint = []
                
                for _, lap in driver_laps.iterrows():
                    if lap['Compound'] != current_compound:
                        if current_stint:
                            stints.append(current_stint)
                        current_stint = [lap]
                        current_compound = lap['Compound']
                    else:
                        current_stint.append(lap)
                
                if current_stint:
                    stints.append(current_stint)
                
                # Analyze each stint
                stint_analysis = []
                for i, stint in enumerate(stints):
                    if len(stint) > 2:  # Need minimum laps for degradation analysis
                        stint_df = pd.DataFrame(stint)
                        degradation = self.calculate_tire_degradation(stint_df)
                        
                        stint_analysis.append({
                            'stint_number': i + 1,
                            'compound': stint[0]['Compound'],
                            'laps': len(stint),
                            'degradation_rate': degradation,
                            'start_performance': str(stint[0]['LapTime']),
                            'end_performance': str(stint[-1]['LapTime'])
                        })
                
                degradation_data[driver] = stint_analysis
            
            return degradation_data
            
        except Exception as e:
            return {}
    
    def analyze_sector_performance(self, session_data):
        """Analyze sector-by-sector performance"""
        try:
            sector_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                valid_laps = driver_laps.dropna(subset=['Sector1Time', 'Sector2Time', 'Sector3Time'])
                if valid_laps.empty:
                    continue
                
                sector_data[driver] = {
                    'best_sector_1': str(valid_laps['Sector1Time'].min()),
                    'best_sector_2': str(valid_laps['Sector2Time'].min()),
                    'best_sector_3': str(valid_laps['Sector3Time'].min()),
                    'avg_sector_1': str(valid_laps['Sector1Time'].mean()),
                    'avg_sector_2': str(valid_laps['Sector2Time'].mean()),
                    'avg_sector_3': str(valid_laps['Sector3Time'].mean()),
                    'sector_consistency': {
                        'sector_1_std': float(valid_laps['Sector1Time'].std().total_seconds()),
                        'sector_2_std': float(valid_laps['Sector2Time'].std().total_seconds()),
                        'sector_3_std': float(valid_laps['Sector3Time'].std().total_seconds())
                    }
                }
            
            return sector_data
            
        except Exception as e:
            return {}
    
    def analyze_race_pace(self, session_data):
        """Analyze race pace and strategy"""
        try:
            if not hasattr(session_data, 'laps'):
                return None
            
            race_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                # Filter out outlier laps (pit stops, safety cars, etc.)
                clean_laps = self.filter_clean_laps(driver_laps)
                
                if len(clean_laps) < 5:
                    continue
                
                race_data[driver] = {
                    'average_pace': str(clean_laps['LapTime'].mean()),
                    'median_pace': str(clean_laps['LapTime'].median()),
                    'pace_consistency': float(clean_laps['LapTime'].std().total_seconds()),
                    'fastest_race_lap': str(clean_laps['LapTime'].min()),
                    'stint_analysis': self.analyze_race_stints(driver_laps),
                    'position_changes': self.analyze_position_changes(driver_laps)
                }
            
            return race_data
            
        except Exception as e:
            return {}
    
    def calculate_consistency_score(self, lap_times):
        """Calculate a consistency score (0-100, higher is more consistent)"""
        try:
            if len(lap_times) < 2:
                return 0
            
            cv = np.std(lap_times) / np.mean(lap_times)
            # Convert to 0-100 scale (lower CV = higher consistency)
            consistency_score = max(0, 100 - (cv * 1000))
            return float(consistency_score)
            
        except Exception as e:
            return 0
    
    def identify_outlier_laps(self, lap_times):
        """Identify outlier laps using statistical methods"""
        try:
            if len(lap_times) < 4:
                return []
            
            q1 = np.percentile(lap_times, 25)
            q3 = np.percentile(lap_times, 75)
            iqr = q3 - q1
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = []
            for i, lap_time in enumerate(lap_times):
                if lap_time < lower_bound or lap_time > upper_bound:
                    outliers.append(i + 1)  # 1-indexed lap numbers
            
            return outliers
            
        except Exception as e:
            return []
    
    def calculate_tire_degradation(self, stint_data):
        """Calculate tire degradation rate for a stint"""
        try:
            if len(stint_data) < 3:
                return 0
            
            lap_times = [row['LapTime'].total_seconds() for _, row in stint_data.iterrows()]
            lap_numbers = list(range(1, len(lap_times) + 1))
            
            # Linear regression to find degradation trend
            slope = np.polyfit(lap_numbers, lap_times, 1)[0]
            return float(slope)  # seconds per lap degradation
            
        except Exception as e:
            return 0
    
    def filter_clean_laps(self, driver_laps):
        """Filter out non-representative laps (pit stops, etc.)"""
        try:
            # Remove laps with pit stops
            clean_laps = driver_laps[driver_laps['PitOutTime'].isna() & driver_laps['PitInTime'].isna()]
            
            # Remove statistical outliers
            if len(clean_laps) > 5:
                lap_times = [lt.total_seconds() for lt in clean_laps['LapTime']]
                q1 = np.percentile(lap_times, 25)
                q3 = np.percentile(lap_times, 75)
                iqr = q3 - q1
                
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                clean_laps = clean_laps[
                    clean_laps['LapTime'].apply(lambda x: lower_bound <= x.total_seconds() <= upper_bound)
                ]
            
            return clean_laps
            
        except Exception as e:
            return driver_laps
    
    def analyze_race_stints(self, driver_laps):
        """Analyze individual race stints"""
        try:
            stints = []
            current_compound = None
            current_stint_laps = []
            
            for _, lap in driver_laps.iterrows():
                if lap['Compound'] != current_compound:
                    if current_stint_laps:
                        stint_analysis = self.analyze_single_stint(current_stint_laps, current_compound)
                        stints.append(stint_analysis)
                    
                    current_stint_laps = [lap]
                    current_compound = lap['Compound']
                else:
                    current_stint_laps.append(lap)
            
            # Analyze final stint
            if current_stint_laps:
                stint_analysis = self.analyze_single_stint(current_stint_laps, current_compound)
                stints.append(stint_analysis)
            
            return stints
            
        except Exception as e:
            return []
    
    def analyze_single_stint(self, stint_laps, compound):
        """Analyze a single stint"""
        try:
            stint_df = pd.DataFrame(stint_laps)
            
            return {
                'compound': compound,
                'laps': len(stint_laps),
                'avg_lap_time': str(stint_df['LapTime'].mean()),
                'best_lap_time': str(stint_df['LapTime'].min()),
                'degradation': self.calculate_tire_degradation(stint_df),
                'start_lap': int(stint_df['LapNumber'].min()),
                'end_lap': int(stint_df['LapNumber'].max())
            }
            
        except Exception as e:
            return {}
    
    def analyze_position_changes(self, driver_laps):
        """Analyze position changes throughout the race"""
        try:
            positions = driver_laps['Position'].dropna()
            if positions.empty:
                return {}
            
            start_position = int(positions.iloc[0])
            end_position = int(positions.iloc[-1])
            
            return {
                'start_position': start_position,
                'end_position': end_position,
                'position_change': start_position - end_position,
                'highest_position': int(positions.min()),
                'lowest_position': int(positions.max()),
                'position_variance': float(positions.var())
            }
            
        except Exception as e:
            return {}
