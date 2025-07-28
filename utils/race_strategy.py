import pandas as pd
import numpy as np
from utils.data_loader import DataLoader

class RaceStrategyAnalyzer:
    """Analyze race strategies and pit stop effectiveness"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def analyze_race_strategy(self, year, grand_prix):
        """Comprehensive race strategy analysis"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, 'Race')
            if session_data is None:
                return None
            
            analysis = {
                'pit_stop_analysis': self.analyze_pit_stops(session_data),
                'tire_strategies': self.analyze_tire_strategies(session_data),
                'undercut_overcut': self.analyze_undercut_overcut(session_data),
                'strategy_effectiveness': self.evaluate_strategy_effectiveness(session_data),
                'alternative_strategies': self.suggest_alternative_strategies(session_data)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_pit_stops(self, session_data):
        """Analyze pit stop performance and timing"""
        try:
            pit_stop_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                # Find pit stop laps
                pit_stops = []
                
                for i, (_, lap) in enumerate(driver_laps.iterrows()):
                    if pd.notna(lap['PitInTime']) or pd.notna(lap['PitOutTime']):
                        pit_stop_info = {
                            'lap_number': int(lap['LapNumber']),
                            'in_time': str(lap['PitInTime']) if pd.notna(lap['PitInTime']) else None,
                            'out_time': str(lap['PitOutTime']) if pd.notna(lap['PitOutTime']) else None,
                            'tire_change': self.detect_tire_change(driver_laps, i),
                            'pit_duration': self.calculate_pit_duration(lap),
                            'position_before': int(lap['Position']) if pd.notna(lap['Position']) else None
                        }
                        
                        # Get position after pit stop
                        if i + 1 < len(driver_laps):
                            next_lap = driver_laps.iloc[i + 1]
                            pit_stop_info['position_after'] = int(next_lap['Position']) if pd.notna(next_lap['Position']) else None
                            pit_stop_info['positions_lost'] = pit_stop_info['position_after'] - pit_stop_info['position_before'] if both_valid(pit_stop_info['position_before'], pit_stop_info['position_after']) else None
                        
                        pit_stops.append(pit_stop_info)
                
                if pit_stops:
                    pit_stop_data[driver] = {
                        'total_pit_stops': len(pit_stops),
                        'pit_stops': pit_stops,
                        'avg_pit_duration': self.calculate_avg_pit_duration(pit_stops),
                        'strategy_type': self.classify_strategy_type(len(pit_stops))
                    }
            
            return pit_stop_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_tire_strategies(self, session_data):
        """Analyze tire compound strategies"""
        try:
            tire_strategies = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                # Analyze stint structure
                stints = []
                current_compound = None
                current_stint = []
                
                for _, lap in driver_laps.iterrows():
                    if lap['Compound'] != current_compound:
                        if current_stint:
                            stint_info = self.analyze_stint(current_stint, current_compound)
                            stints.append(stint_info)
                        
                        current_stint = [lap]
                        current_compound = lap['Compound']
                    else:
                        current_stint.append(lap)
                
                # Process final stint
                if current_stint:
                    stint_info = self.analyze_stint(current_stint, current_compound)
                    stints.append(stint_info)
                
                if stints:
                    tire_strategies[driver] = {
                        'total_stints': len(stints),
                        'stints': stints,
                        'compound_sequence': [stint['compound'] for stint in stints],
                        'strategy_classification': self.classify_tire_strategy(stints),
                        'degradation_management': self.evaluate_degradation_management(stints)
                    }
            
            return tire_strategies
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_undercut_overcut(self, session_data):
        """Analyze undercut and overcut opportunities"""
        try:
            undercut_analysis = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                undercuts = []
                overcuts = []
                
                # Find pit stop laps
                for i, (_, lap) in enumerate(driver_laps.iterrows()):
                    if pd.notna(lap['PitInTime']) or pd.notna(lap['PitOutTime']):
                        # Analyze undercut/overcut potential
                        analysis = self.analyze_strategic_move(driver_laps, i, session_data)
                        
                        if analysis['type'] == 'undercut':
                            undercuts.append(analysis)
                        elif analysis['type'] == 'overcut':
                            overcuts.append(analysis)
                
                undercut_analysis[driver] = {
                    'undercuts_attempted': len(undercuts),
                    'overcuts_attempted': len(overcuts),
                    'undercut_details': undercuts,
                    'overcut_details': overcuts,
                    'strategic_effectiveness': self.rate_strategic_effectiveness(undercuts + overcuts)
                }
            
            return undercut_analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def evaluate_strategy_effectiveness(self, session_data):
        """Evaluate overall strategy effectiveness"""
        try:
            effectiveness = {}
            
            results = session_data.results if hasattr(session_data, 'results') else None
            if results is None:
                return {'error': 'No results data available'}
            
            for driver in session_data.drivers:
                driver_result = results[results['Abbreviation'] == driver]
                if driver_result.empty:
                    continue
                
                final_position = int(driver_result['Position'].iloc[0]) if pd.notna(driver_result['Position'].iloc[0]) else None
                grid_position = int(driver_result['GridPosition'].iloc[0]) if 'GridPosition' in driver_result.columns and pd.notna(driver_result['GridPosition'].iloc[0]) else None
                
                if final_position and grid_position:
                    position_change = grid_position - final_position
                    
                    effectiveness[driver] = {
                        'grid_position': grid_position,
                        'final_position': final_position,
                        'position_change': position_change,
                        'effectiveness_rating': self.rate_strategy_effectiveness(position_change, grid_position),
                        'points_scored': int(driver_result['Points'].iloc[0]) if 'Points' in driver_result.columns else 0
                    }
            
            return effectiveness
            
        except Exception as e:
            return {'error': str(e)}
    
    def suggest_alternative_strategies(self, session_data):
        """Suggest alternative strategies that could have been used"""
        try:
            suggestions = {}
            
            # Analyze race conditions
            race_length = session_data.laps['LapNumber'].max() if hasattr(session_data, 'laps') else 0
            
            for driver in session_data.drivers[:5]:  # Limit to top 5 for performance
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                current_strategy = self.extract_current_strategy(driver_laps)
                alternatives = []
                
                # Suggest one-stop strategy if they did two-stop
                if current_strategy['stops'] >= 2:
                    one_stop = self.simulate_one_stop_strategy(driver_laps, race_length)
                    if one_stop:
                        alternatives.append(one_stop)
                
                # Suggest two-stop if they did one-stop
                if current_strategy['stops'] == 1:
                    two_stop = self.simulate_two_stop_strategy(driver_laps, race_length)
                    if two_stop:
                        alternatives.append(two_stop)
                
                # Suggest different compound sequences
                compound_alternatives = self.suggest_compound_alternatives(current_strategy)
                alternatives.extend(compound_alternatives)
                
                suggestions[driver] = {
                    'current_strategy': current_strategy,
                    'alternative_strategies': alternatives,
                    'recommendation': self.recommend_best_alternative(current_strategy, alternatives)
                }
            
            return suggestions
            
        except Exception as e:
            return {'error': str(e)}
    
    def detect_tire_change(self, driver_laps, pit_lap_index):
        """Detect if tires were changed during pit stop"""
        try:
            if pit_lap_index == 0 or pit_lap_index >= len(driver_laps) - 1:
                return {'changed': False, 'from': None, 'to': None}
            
            before_compound = driver_laps.iloc[pit_lap_index - 1]['Compound']
            after_compound = driver_laps.iloc[pit_lap_index + 1]['Compound']
            
            changed = before_compound != after_compound
            
            return {
                'changed': changed,
                'from': before_compound,
                'to': after_compound
            }
            
        except Exception as e:
            return {'changed': False, 'from': None, 'to': None}
    
    def calculate_pit_duration(self, lap):
        """Calculate pit stop duration"""
        try:
            if pd.notna(lap['PitInTime']) and pd.notna(lap['PitOutTime']):
                duration = lap['PitOutTime'] - lap['PitInTime']
                return duration.total_seconds()
            return None
            
        except Exception as e:
            return None
    
    def calculate_avg_pit_duration(self, pit_stops):
        """Calculate average pit stop duration"""
        try:
            durations = [ps['pit_duration'] for ps in pit_stops if ps['pit_duration'] is not None]
            return float(np.mean(durations)) if durations else None
            
        except Exception as e:
            return None
    
    def classify_strategy_type(self, num_stops):
        """Classify strategy type based on number of stops"""
        if num_stops == 0:
            return 'no_stop'
        elif num_stops == 1:
            return 'one_stop'
        elif num_stops == 2:
            return 'two_stop'
        elif num_stops == 3:
            return 'three_stop'
        else:
            return 'multi_stop'
    
    def analyze_stint(self, stint_laps, compound):
        """Analyze individual stint performance"""
        try:
            stint_df = pd.DataFrame(stint_laps)
            
            return {
                'compound': compound,
                'laps': len(stint_laps),
                'start_lap': int(stint_df['LapNumber'].min()),
                'end_lap': int(stint_df['LapNumber'].max()),
                'avg_lap_time': str(stint_df['LapTime'].mean()),
                'best_lap_time': str(stint_df['LapTime'].min()),
                'degradation_rate': self.calculate_degradation_rate(stint_df),
                'tire_life_used': len(stint_laps)
            }
            
        except Exception as e:
            return {}
    
    def calculate_degradation_rate(self, stint_df):
        """Calculate tire degradation rate for a stint"""
        try:
            if len(stint_df) < 3:
                return 0
            
            lap_times = [lt.total_seconds() for lt in stint_df['LapTime']]
            lap_numbers = list(range(len(lap_times)))
            
            # Linear regression to find degradation trend
            slope = np.polyfit(lap_numbers, lap_times, 1)[0]
            return float(slope)
            
        except Exception as e:
            return 0
    
    def classify_tire_strategy(self, stints):
        """Classify overall tire strategy"""
        try:
            compounds = [stint['compound'] for stint in stints]
            num_stints = len(stints)
            
            if num_stints == 1:
                return f"one_stop_{compounds[0].lower()}"
            elif num_stints == 2:
                return f"two_stop_{compounds[0].lower()}_to_{compounds[1].lower()}"
            elif num_stints == 3:
                return f"three_stop_strategy"
            else:
                return "complex_strategy"
                
        except Exception as e:
            return "unknown_strategy"
    
    def evaluate_degradation_management(self, stints):
        """Evaluate how well tire degradation was managed"""
        try:
            if not stints:
                return 'unknown'
            
            avg_degradation = np.mean([stint.get('degradation_rate', 0) for stint in stints])
            
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
    
    def analyze_strategic_move(self, driver_laps, pit_lap_index, session_data):
        """Analyze if a pit stop was an undercut or overcut attempt"""
        try:
            # This is a simplified analysis - in reality, this would require
            # complex position tracking and competitor analysis
            
            lap_number = driver_laps.iloc[pit_lap_index]['LapNumber']
            
            # Simplified classification based on timing
            if lap_number < 20:
                return {'type': 'early_stop', 'lap': int(lap_number), 'effectiveness': 'unknown'}
            elif lap_number < 40:
                return {'type': 'undercut', 'lap': int(lap_number), 'effectiveness': 'unknown'}
            else:
                return {'type': 'overcut', 'lap': int(lap_number), 'effectiveness': 'unknown'}
                
        except Exception as e:
            return {'type': 'unknown', 'lap': 0, 'effectiveness': 'unknown'}
    
    def rate_strategic_effectiveness(self, strategic_moves):
        """Rate the effectiveness of strategic moves"""
        try:
            if not strategic_moves:
                return 'no_moves'
            
            # Simplified rating - would need position tracking for accurate assessment
            return 'unknown'
            
        except Exception as e:
            return 'unknown'
    
    def rate_strategy_effectiveness(self, position_change, grid_position):
        """Rate overall strategy effectiveness"""
        try:
            if position_change > 5:
                return 'excellent'
            elif position_change > 2:
                return 'good'
            elif position_change >= 0:
                return 'adequate'
            elif position_change > -3:
                return 'poor'
            else:
                return 'very_poor'
                
        except Exception as e:
            return 'unknown'
    
    def extract_current_strategy(self, driver_laps):
        """Extract current strategy information"""
        try:
            pit_stops = 0
            compounds_used = []
            
            current_compound = None
            for _, lap in driver_laps.iterrows():
                if lap['Compound'] != current_compound:
                    if current_compound is not None:
                        pit_stops += 1
                    compounds_used.append(lap['Compound'])
                    current_compound = lap['Compound']
            
            return {
                'stops': pit_stops,
                'compounds': compounds_used,
                'strategy_type': self.classify_strategy_type(pit_stops)
            }
            
        except Exception as e:
            return {'stops': 0, 'compounds': [], 'strategy_type': 'unknown'}
    
    def simulate_one_stop_strategy(self, driver_laps, race_length):
        """Simulate a one-stop strategy alternative"""
        try:
            # Simplified simulation
            optimal_stop_lap = race_length // 2
            
            return {
                'type': 'one_stop',
                'stop_lap': optimal_stop_lap,
                'compounds': ['MEDIUM', 'HARD'],
                'estimated_benefit': 'unknown'  # Would require complex simulation
            }
            
        except Exception as e:
            return None
    
    def simulate_two_stop_strategy(self, driver_laps, race_length):
        """Simulate a two-stop strategy alternative"""
        try:
            # Simplified simulation
            stop1_lap = race_length // 3
            stop2_lap = (race_length * 2) // 3
            
            return {
                'type': 'two_stop',
                'stop_laps': [stop1_lap, stop2_lap],
                'compounds': ['SOFT', 'MEDIUM', 'SOFT'],
                'estimated_benefit': 'unknown'
            }
            
        except Exception as e:
            return None
    
    def suggest_compound_alternatives(self, current_strategy):
        """Suggest alternative compound sequences"""
        try:
            alternatives = []
            current_compounds = current_strategy.get('compounds', [])
            
            # Suggest alternative compound sequences based on current strategy
            if 'SOFT' not in current_compounds:
                alternatives.append({
                    'type': 'aggressive_soft',
                    'compounds': ['SOFT'] + current_compounds[1:],
                    'benefit': 'Better qualifying, higher degradation'
                })
            
            if 'HARD' not in current_compounds:
                alternatives.append({
                    'type': 'conservative_hard',
                    'compounds': current_compounds[:-1] + ['HARD'],
                    'benefit': 'Lower degradation, longer stint'
                })
            
            return alternatives
            
        except Exception as e:
            return []
    
    def recommend_best_alternative(self, current_strategy, alternatives):
        """Recommend the best alternative strategy"""
        try:
            if not alternatives:
                return 'current_strategy_optimal'
            
            # Simplified recommendation logic
            # In reality, this would involve complex simulation and analysis
            return alternatives[0] if alternatives else None
            
        except Exception as e:
            return None

def both_valid(val1, val2):
    """Check if both values are valid (not None)"""
    return val1 is not None and val2 is not None
