import pandas as pd
import numpy as np
from utils.data_loader import DataLoader

class TirePerformanceAnalyzer:
    """Analyze tire performance and degradation patterns"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def analyze_race_tire_performance(self, year, grand_prix):
        """Comprehensive tire performance analysis for a race"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, 'Race')
            if session_data is None:
                return None
            
            analysis = {
                'compound_performance': self.analyze_compound_performance(session_data),
                'degradation_analysis': self.analyze_tire_degradation(session_data),
                'temperature_impact': self.analyze_temperature_impact(session_data),
                'stint_optimization': self.analyze_stint_optimization(session_data),
                'tire_strategy_effectiveness': self.evaluate_tire_strategies(session_data)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_compound_performance(self, session_data):
        """Analyze performance of different tire compounds"""
        try:
            compound_data = {}
            
            # Get all available compounds used in the race
            all_laps = session_data.laps
            compounds = all_laps['Compound'].dropna().unique()
            
            for compound in compounds:
                compound_laps = all_laps[all_laps['Compound'] == compound]
                
                if compound_laps.empty:
                    continue
                
                # Calculate performance metrics
                lap_times = compound_laps['LapTime'].dropna()
                lap_times_seconds = [lt.total_seconds() for lt in lap_times]
                
                compound_data[compound] = {
                    'total_laps': len(compound_laps),
                    'average_lap_time': float(np.mean(lap_times_seconds)),
                    'best_lap_time': float(np.min(lap_times_seconds)),
                    'lap_time_std': float(np.std(lap_times_seconds)),
                    'drivers_used': len(compound_laps['Driver'].unique()),
                    'performance_window': self.calculate_performance_window(compound_laps),
                    'degradation_characteristics': self.analyze_compound_degradation(compound_laps)
                }
            
            # Rank compounds by performance
            compound_ranking = self.rank_compounds_by_performance(compound_data)
            
            return {
                'compound_data': compound_data,
                'compound_ranking': compound_ranking,
                'optimal_compound': compound_ranking[0] if compound_ranking else None
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_tire_degradation(self, session_data):
        """Analyze tire degradation patterns"""
        try:
            degradation_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                driver_stints = self.extract_driver_stints(driver_laps)
                stint_analysis = []
                
                for stint in driver_stints:
                    if len(stint) >= 3:  # Need minimum laps for degradation analysis
                        degradation = self.calculate_stint_degradation(stint)
                        stint_analysis.append(degradation)
                
                if stint_analysis:
                    degradation_data[driver] = {
                        'stints': stint_analysis,
                        'average_degradation': float(np.mean([s['degradation_rate'] for s in stint_analysis])),
                        'degradation_consistency': float(np.std([s['degradation_rate'] for s in stint_analysis])),
                        'tire_management_rating': self.rate_tire_management(stint_analysis)
                    }
            
            return degradation_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_temperature_impact(self, session_data):
        """Analyze impact of temperature on tire performance"""
        try:
            # Get weather data if available
            weather_data = self.data_loader.get_weather_data(session_data)
            if weather_data is None or weather_data.empty:
                return {'error': 'No weather data available'}
            
            avg_air_temp = weather_data['AirTemp'].mean()
            avg_track_temp = weather_data['TrackTemp'].mean()
            
            temperature_impact = {
                'air_temperature': float(avg_air_temp),
                'track_temperature': float(avg_track_temp),
                'temperature_impact_rating': self.rate_temperature_impact(avg_track_temp),
                'compound_recommendations': self.recommend_compounds_for_temperature(avg_track_temp),
                'degradation_factor': self.calculate_temperature_degradation_factor(avg_track_temp)
            }
            
            return temperature_impact
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_stint_optimization(self, session_data):
        """Analyze optimal stint lengths for different compounds"""
        try:
            optimization_data = {}
            
            all_laps = session_data.laps
            compounds = all_laps['Compound'].dropna().unique()
            
            for compound in compounds:
                compound_stints = self.get_compound_stints(all_laps, compound)
                
                if not compound_stints:
                    continue
                
                stint_lengths = [len(stint) for stint in compound_stints]
                stint_performances = [self.calculate_stint_performance(stint) for stint in compound_stints]
                
                optimization_data[compound] = {
                    'average_stint_length': float(np.mean(stint_lengths)),
                    'optimal_stint_length': self.calculate_optimal_stint_length(compound_stints),
                    'stint_length_range': {
                        'min': int(np.min(stint_lengths)),
                        'max': int(np.max(stint_lengths))
                    },
                    'performance_correlation': self.correlate_length_with_performance(stint_lengths, stint_performances)
                }
            
            return optimization_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def evaluate_tire_strategies(self, session_data):
        """Evaluate effectiveness of different tire strategies"""
        try:
            strategy_evaluation = {}
            
            # Get race results for strategy effectiveness
            results = session_data.results if hasattr(session_data, 'results') else None
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                strategy = self.extract_tire_strategy(driver_laps)
                
                # Get final position if available
                final_position = None
                if results is not None:
                    driver_result = results[results['Abbreviation'] == driver]
                    if not driver_result.empty:
                        final_position = int(driver_result['Position'].iloc[0])
                
                strategy_evaluation[driver] = {
                    'strategy': strategy,
                    'final_position': final_position,
                    'strategy_effectiveness': self.rate_strategy_effectiveness(strategy, final_position),
                    'alternative_strategies': self.suggest_alternative_strategies(strategy),
                    'tire_usage_efficiency': self.calculate_tire_usage_efficiency(driver_laps)
                }
            
            return strategy_evaluation
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_performance_window(self, compound_laps):
        """Calculate the performance window for a tire compound"""
        try:
            # Group laps by tire age
            tire_ages = compound_laps['TyreLife'].dropna()
            if tire_ages.empty:
                return {'peak_performance_age': None, 'cliff_age': None}
            
            # Find peak performance age (lowest average lap time)
            age_performance = {}
            for age in tire_ages.unique():
                age_laps = compound_laps[compound_laps['TyreLife'] == age]
                lap_times = age_laps['LapTime'].dropna()
                if not lap_times.empty:
                    avg_time = np.mean([lt.total_seconds() for lt in lap_times])
                    age_performance[age] = avg_time
            
            if not age_performance:
                return {'peak_performance_age': None, 'cliff_age': None}
            
            peak_age = min(age_performance, key=age_performance.get)
            
            # Find cliff point (where performance degrades significantly)
            cliff_age = self.find_performance_cliff(age_performance)
            
            return {
                'peak_performance_age': int(peak_age),
                'cliff_age': cliff_age,
                'performance_curve': age_performance
            }
            
        except Exception as e:
            return {'peak_performance_age': None, 'cliff_age': None}
    
    def analyze_compound_degradation(self, compound_laps):
        """Analyze degradation characteristics of a compound"""
        try:
            # Group by stint and calculate degradation for each
            stints = self.group_laps_by_stint(compound_laps)
            degradation_rates = []
            
            for stint in stints:
                if len(stint) >= 3:
                    rate = self.calculate_stint_degradation_rate(stint)
                    if rate is not None:
                        degradation_rates.append(rate)
            
            if not degradation_rates:
                return {'average_degradation_rate': None, 'degradation_consistency': None}
            
            return {
                'average_degradation_rate': float(np.mean(degradation_rates)),
                'degradation_consistency': float(np.std(degradation_rates)),
                'degradation_range': {
                    'min': float(np.min(degradation_rates)),
                    'max': float(np.max(degradation_rates))
                }
            }
            
        except Exception as e:
            return {'average_degradation_rate': None, 'degradation_consistency': None}
    
    def extract_driver_stints(self, driver_laps):
        """Extract individual stints from driver's laps"""
        try:
            stints = []
            current_stint = []
            current_compound = None
            
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
            
            return stints
            
        except Exception as e:
            return []
    
    def calculate_stint_degradation(self, stint):
        """Calculate degradation metrics for a stint"""
        try:
            stint_df = pd.DataFrame(stint)
            lap_times = [lt.total_seconds() for lt in stint_df['LapTime']]
            
            if len(lap_times) < 3:
                return None
            
            # Calculate degradation rate (slope of lap time vs lap number)
            lap_numbers = list(range(len(lap_times)))
            degradation_rate = np.polyfit(lap_numbers, lap_times, 1)[0]
            
            return {
                'compound': stint[0]['Compound'],
                'stint_length': len(stint),
                'degradation_rate': float(degradation_rate),
                'initial_performance': lap_times[0],
                'final_performance': lap_times[-1],
                'performance_drop': lap_times[-1] - lap_times[0]
            }
            
        except Exception as e:
            return None
    
    def rate_tire_management(self, stint_analysis):
        """Rate tire management based on stint analysis"""
        try:
            if not stint_analysis:
                return 'unknown'
            
            avg_degradation = np.mean([s['degradation_rate'] for s in stint_analysis])
            
            if avg_degradation < 0.05:
                return 'excellent'
            elif avg_degradation < 0.1:
                return 'good'
            elif avg_degradation < 0.2:
                return 'average'
            else:
                return 'poor'
                
        except Exception as e:
            return 'unknown'
    
    def rate_temperature_impact(self, track_temp):
        """Rate the impact of track temperature on tire performance"""
        try:
            if track_temp > 50:
                return 'very_high_degradation'
            elif track_temp > 40:
                return 'high_degradation'
            elif track_temp > 30:
                return 'moderate_degradation'
            elif track_temp > 20:
                return 'low_degradation'
            else:
                return 'very_low_degradation'
                
        except Exception as e:
            return 'unknown'
    
    def recommend_compounds_for_temperature(self, track_temp):
        """Recommend tire compounds based on track temperature"""
        try:
            if track_temp > 45:
                return ['HARD', 'MEDIUM']
            elif track_temp > 35:
                return ['MEDIUM', 'HARD']
            elif track_temp > 25:
                return ['SOFT', 'MEDIUM']
            else:
                return ['SOFT', 'MEDIUM', 'HARD']
                
        except Exception as e:
            return ['MEDIUM']
    
    def calculate_temperature_degradation_factor(self, track_temp):
        """Calculate degradation factor based on temperature"""
        try:
            # Base degradation factor at 30°C
            base_temp = 30
            temp_diff = track_temp - base_temp
            
            # Each degree above 30°C increases degradation by 3%
            factor = 1.0 + (temp_diff * 0.03)
            return float(max(0.5, min(3.0, factor)))  # Clamp between 0.5 and 3.0
            
        except Exception as e:
            return 1.0
    
    def rank_compounds_by_performance(self, compound_data):
        """Rank compounds by overall performance"""
        try:
            rankings = []
            
            for compound, data in compound_data.items():
                # Score based on average lap time (lower is better)
                score = data.get('average_lap_time', float('inf'))
                rankings.append((compound, score))
            
            # Sort by score (ascending - lower lap time is better)
            rankings.sort(key=lambda x: x[1])
            
            return [compound for compound, _ in rankings]
            
        except Exception as e:
            return []
    
    def get_compound_stints(self, all_laps, compound):
        """Get all stints for a specific compound"""
        try:
            compound_laps = all_laps[all_laps['Compound'] == compound]
            stints = []
            
            # Group by driver and then by consecutive usage
            for driver in compound_laps['Driver'].unique():
                driver_laps = compound_laps[compound_laps['Driver'] == driver].sort_values('LapNumber')
                
                current_stint = []
                prev_lap_num = None
                
                for _, lap in driver_laps.iterrows():
                    if prev_lap_num is None or lap['LapNumber'] == prev_lap_num + 1:
                        current_stint.append(lap)
                    else:
                        if current_stint:
                            stints.append(current_stint)
                        current_stint = [lap]
                    
                    prev_lap_num = lap['LapNumber']
                
                if current_stint:
                    stints.append(current_stint)
            
            return stints
            
        except Exception as e:
            return []
    
    def calculate_optimal_stint_length(self, compound_stints):
        """Calculate optimal stint length for a compound"""
        try:
            if not compound_stints:
                return None
            
            stint_performances = []
            
            for stint in compound_stints:
                if len(stint) >= 3:
                    performance = self.calculate_stint_performance(stint)
                    stint_performances.append((len(stint), performance))
            
            if not stint_performances:
                return None
            
            # Find stint length with best average performance
            length_performance = {}
            for length, performance in stint_performances:
                if length not in length_performance:
                    length_performance[length] = []
                length_performance[length].append(performance)
            
            # Calculate average performance for each length
            avg_performances = {
                length: np.mean(performances) 
                for length, performances in length_performance.items()
            }
            
            # Find optimal length (best performance)
            optimal_length = min(avg_performances, key=avg_performances.get)
            return int(optimal_length)
            
        except Exception as e:
            return None
    
    def calculate_stint_performance(self, stint):
        """Calculate overall performance score for a stint"""
        try:
            stint_df = pd.DataFrame(stint)
            lap_times = [lt.total_seconds() for lt in stint_df['LapTime']]
            
            # Performance is based on average lap time and consistency
            avg_time = np.mean(lap_times)
            consistency = np.std(lap_times)
            
            # Lower is better for both metrics
            performance_score = avg_time + consistency
            return performance_score
            
        except Exception as e:
            return float('inf')
    
    def correlate_length_with_performance(self, stint_lengths, stint_performances):
        """Correlate stint length with performance"""
        try:
            if len(stint_lengths) != len(stint_performances) or len(stint_lengths) < 2:
                return None
            
            correlation = np.corrcoef(stint_lengths, stint_performances)[0, 1]
            return float(correlation)
            
        except Exception as e:
            return None
    
    def extract_tire_strategy(self, driver_laps):
        """Extract tire strategy from driver's laps"""
        try:
            compounds_used = []
            stint_lengths = []
            
            current_compound = None
            current_stint_length = 0
            
            for _, lap in driver_laps.iterrows():
                if lap['Compound'] != current_compound:
                    if current_compound is not None:
                        compounds_used.append(current_compound)
                        stint_lengths.append(current_stint_length)
                    
                    current_compound = lap['Compound']
                    current_stint_length = 1
                else:
                    current_stint_length += 1
            
            # Add final stint
            if current_compound is not None:
                compounds_used.append(current_compound)
                stint_lengths.append(current_stint_length)
            
            return {
                'compounds': compounds_used,
                'stint_lengths': stint_lengths,
                'total_stops': len(compounds_used) - 1,
                'strategy_type': self.classify_strategy_type(len(compounds_used))
            }
            
        except Exception as e:
            return {'compounds': [], 'stint_lengths': [], 'total_stops': 0, 'strategy_type': 'unknown'}
    
    def classify_strategy_type(self, num_compounds):
        """Classify strategy type based on number of compounds used"""
        if num_compounds == 1:
            return 'no_stop'
        elif num_compounds == 2:
            return 'one_stop'
        elif num_compounds == 3:
            return 'two_stop'
        else:
            return 'multi_stop'
    
    def rate_strategy_effectiveness(self, strategy, final_position):
        """Rate the effectiveness of a tire strategy"""
        try:
            # Simplified rating based on final position
            if final_position is None:
                return 'unknown'
            
            if final_position <= 3:
                return 'excellent'
            elif final_position <= 6:
                return 'good'
            elif final_position <= 10:
                return 'average'
            else:
                return 'poor'
                
        except Exception as e:
            return 'unknown'
    
    def suggest_alternative_strategies(self, strategy):
        """Suggest alternative tire strategies"""
        try:
            alternatives = []
            current_stops = strategy.get('total_stops', 0)
            
            # Suggest one fewer stop
            if current_stops > 1:
                alternatives.append({
                    'type': 'fewer_stops',
                    'stops': current_stops - 1,
                    'benefit': 'Less time lost in pit lane'
                })
            
            # Suggest one more stop
            if current_stops < 3:
                alternatives.append({
                    'type': 'more_stops',
                    'stops': current_stops + 1,
                    'benefit': 'Fresher tires, potentially faster pace'
                })
            
            return alternatives
            
        except Exception as e:
            return []
    
    def calculate_tire_usage_efficiency(self, driver_laps):
        """Calculate how efficiently tires were used"""
        try:
            total_laps = len(driver_laps)
            if total_laps == 0:
                return 0
            
            # Calculate average tire life used per stint
            stints = self.extract_driver_stints(driver_laps)
            stint_efficiencies = []
            
            for stint in stints:
                stint_length = len(stint)
                compound = stint[0]['Compound']
                
                # Simplified efficiency calculation
                # Different compounds have different optimal usage ranges
                optimal_usage = self.get_optimal_usage_for_compound(compound)
                efficiency = min(1.0, stint_length / optimal_usage)
                stint_efficiencies.append(efficiency)
            
            if stint_efficiencies:
                return float(np.mean(stint_efficiencies))
            
            return 0
            
        except Exception as e:
            return 0
    
    def get_optimal_usage_for_compound(self, compound):
        """Get optimal usage range for a tire compound"""
        # Simplified optimal usage ranges
        optimal_ranges = {
            'SOFT': 15,
            'MEDIUM': 25,
            'HARD': 35,
            'INTERMEDIATE': 20,
            'WET': 15
        }
        
        return optimal_ranges.get(compound, 25)
    
    def group_laps_by_stint(self, compound_laps):
        """Group laps by stint for the same compound"""
        try:
            stints = []
            
            # Group by driver first
            for driver in compound_laps['Driver'].unique():
                driver_laps = compound_laps[compound_laps['Driver'] == driver].sort_values('LapNumber')
                
                # Then group consecutive laps
                current_stint = []
                prev_lap_num = None
                
                for _, lap in driver_laps.iterrows():
                    if prev_lap_num is None or lap['LapNumber'] == prev_lap_num + 1:
                        current_stint.append(lap)
                    else:
                        if current_stint:
                            stints.append(current_stint)
                        current_stint = [lap]
                    
                    prev_lap_num = lap['LapNumber']
                
                if current_stint:
                    stints.append(current_stint)
            
            return stints
            
        except Exception as e:
            return []
    
    def calculate_stint_degradation_rate(self, stint):
        """Calculate degradation rate for a stint"""
        try:
            if len(stint) < 3:
                return None
            
            stint_df = pd.DataFrame(stint)
            lap_times = [lt.total_seconds() for lt in stint_df['LapTime']]
            lap_numbers = list(range(len(lap_times)))
            
            # Linear regression to find degradation slope
            slope = np.polyfit(lap_numbers, lap_times, 1)[0]
            return slope
            
        except Exception as e:
            return None
    
    def find_performance_cliff(self, age_performance):
        """Find the point where tire performance drops significantly"""
        try:
            ages = sorted(age_performance.keys())
            if len(ages) < 3:
                return None
            
            # Look for significant performance drop
            for i in range(1, len(ages)):
                current_time = age_performance[ages[i]]
                previous_time = age_performance[ages[i-1]]
                
                # If lap time increases by more than 2 seconds, consider it a cliff
                if current_time - previous_time > 2.0:
                    return int(ages[i])
            
            return None
            
        except Exception as e:
            return None
