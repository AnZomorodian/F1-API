import pandas as pd
import numpy as np
from utils.data_loader import DataLoader
from utils.constants import DRIVER_TEAMS

class DynamicDriverManager:
    """Manage dynamic driver information and career statistics"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def get_season_driver_data(self, year):
        """Get comprehensive driver data for a season"""
        try:
            season_data = {
                'driver_profiles': self.get_driver_profiles(year),
                'performance_rankings': self.calculate_performance_rankings(year),
                'team_dynamics': self.analyze_team_dynamics(year),
                'career_statistics': self.get_career_statistics(year),
                'driver_comparisons': self.generate_driver_comparisons(year)
            }
            
            return season_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_driver_profiles(self, year):
        """Get detailed driver profiles"""
        try:
            profiles = {}
            
            # Get a sample race to extract current drivers
            sample_race = self.get_sample_race_data(year)
            if not sample_race:
                return {'error': 'No race data available for season'}
            
            for driver in sample_race.drivers:
                try:
                    profile = self.build_driver_profile(driver, year)
                    if profile:
                        profiles[driver] = profile
                except Exception as driver_error:
                    continue
            
            return profiles
            
        except Exception as e:
            return {'error': str(e)}
    
    def build_driver_profile(self, driver, year):
        """Build comprehensive driver profile"""
        try:
            # Get team information
            team = DRIVER_TEAMS.get(driver, 'Unknown')
            
            # Get performance statistics across multiple races
            performance_stats = self.calculate_driver_season_stats(driver, year)
            
            # Get consistency metrics
            consistency_metrics = self.calculate_consistency_metrics(driver, year)
            
            # Get specialization analysis
            specializations = self.analyze_driver_specializations(driver, year)
            
            profile = {
                'driver_code': driver,
                'team': team,
                'season_year': year,
                'performance_statistics': performance_stats,
                'consistency_metrics': consistency_metrics,
                'specializations': specializations,
                'overall_rating': self.calculate_overall_rating(performance_stats, consistency_metrics),
                'strengths': self.identify_strengths(performance_stats, specializations),
                'areas_for_improvement': self.identify_improvement_areas(performance_stats, consistency_metrics)
            }
            
            return profile
            
        except Exception as e:
            return None
    
    def calculate_driver_season_stats(self, driver, year):
        """Calculate comprehensive season statistics for a driver"""
        try:
            stats = {
                'races_analyzed': 0,
                'average_qualifying_position': None,
                'average_race_position': None,
                'fastest_laps_count': 0,
                'average_lap_time': None,
                'best_lap_time': None,
                'points_scored': 0,
                'podium_finishes': 0,
                'dnf_count': 0
            }
            
            # Analyze multiple races for comprehensive statistics
            race_count = 0
            qualifying_positions = []
            race_positions = []
            lap_times = []
            
            # Sample key races from the season (would need full season data in production)
            sample_races = ['Bahrain', 'Spain', 'Great Britain', 'Italy', 'Abu Dhabi']
            
            for race in sample_races:
                try:
                    # Try qualifying data first
                    qualifying_data = self.data_loader.load_session_data(year, race, 'Qualifying')
                    if qualifying_data and hasattr(qualifying_data, 'results'):
                        driver_qual_result = qualifying_data.results[qualifying_data.results['Abbreviation'] == driver]
                        if not driver_qual_result.empty:
                            qual_pos = driver_qual_result['Position'].iloc[0]
                            if pd.notna(qual_pos):
                                qualifying_positions.append(int(qual_pos))
                    
                    # Try race data
                    race_data = self.data_loader.load_session_data(year, race, 'Race')
                    if race_data:
                        race_count += 1
                        
                        # Get race result
                        if hasattr(race_data, 'results'):
                            driver_race_result = race_data.results[race_data.results['Abbreviation'] == driver]
                            if not driver_race_result.empty:
                                race_pos = driver_race_result['Position'].iloc[0]
                                if pd.notna(race_pos):
                                    race_positions.append(int(race_pos))
                                    
                                    # Count podiums
                                    if int(race_pos) <= 3:
                                        stats['podium_finishes'] += 1
                                
                                # Get points
                                if 'Points' in driver_race_result.columns:
                                    points = driver_race_result['Points'].iloc[0]
                                    if pd.notna(points):
                                        stats['points_scored'] += int(points)
                        
                        # Get lap times
                        driver_laps = race_data.laps.pick_driver(driver)
                        if not driver_laps.empty:
                            valid_lap_times = driver_laps['LapTime'].dropna()
                            for lap_time in valid_lap_times:
                                lap_times.append(lap_time.total_seconds())
                            
                            # Check for fastest lap
                            fastest_lap = driver_laps.pick_fastest()
                            if not fastest_lap.empty and hasattr(fastest_lap, 'IsPersonalBest'):
                                if fastest_lap['IsPersonalBest']:
                                    stats['fastest_laps_count'] += 1
                
                except Exception as race_error:
                    continue
            
            # Calculate averages
            stats['races_analyzed'] = race_count
            
            if qualifying_positions:
                stats['average_qualifying_position'] = float(np.mean(qualifying_positions))
            
            if race_positions:
                stats['average_race_position'] = float(np.mean(race_positions))
            
            if lap_times:
                stats['average_lap_time'] = float(np.mean(lap_times))
                stats['best_lap_time'] = float(min(lap_times))
            
            return stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_consistency_metrics(self, driver, year):
        """Calculate driver consistency metrics"""
        try:
            consistency_data = {
                'qualifying_consistency': None,
                'race_consistency': None,
                'lap_time_consistency': None,
                'position_stability': None,
                'error_rate': None
            }
            
            all_qualifying_positions = []
            all_race_positions = []
            all_lap_times = []
            position_changes = []
            
            # Sample races for consistency analysis
            sample_races = ['Bahrain', 'Spain', 'Great Britain', 'Italy']
            
            for race in sample_races:
                try:
                    # Qualifying consistency
                    qualifying_data = self.data_loader.load_session_data(year, race, 'Qualifying')
                    if qualifying_data and hasattr(qualifying_data, 'results'):
                        driver_result = qualifying_data.results[qualifying_data.results['Abbreviation'] == driver]
                        if not driver_result.empty:
                            qual_pos = driver_result['Position'].iloc[0]
                            if pd.notna(qual_pos):
                                all_qualifying_positions.append(int(qual_pos))
                    
                    # Race consistency
                    race_data = self.data_loader.load_session_data(year, race, 'Race')
                    if race_data:
                        if hasattr(race_data, 'results'):
                            driver_result = race_data.results[race_data.results['Abbreviation'] == driver]
                            if not driver_result.empty:
                                race_pos = driver_result['Position'].iloc[0]
                                if pd.notna(race_pos):
                                    all_race_positions.append(int(race_pos))
                        
                        # Lap time consistency
                        driver_laps = race_data.laps.pick_driver(driver)
                        if not driver_laps.empty:
                            valid_lap_times = driver_laps['LapTime'].dropna()
                            race_lap_times = [lt.total_seconds() for lt in valid_lap_times]
                            all_lap_times.extend(race_lap_times)
                            
                            # Position changes within race
                            positions = driver_laps['Position'].dropna()
                            if len(positions) > 1:
                                race_position_changes = np.abs(np.diff(positions.values))
                                position_changes.extend(race_position_changes)
                
                except Exception as race_error:
                    continue
            
            # Calculate consistency metrics
            if len(all_qualifying_positions) > 1:
                consistency_data['qualifying_consistency'] = float(np.std(all_qualifying_positions))
            
            if len(all_race_positions) > 1:
                consistency_data['race_consistency'] = float(np.std(all_race_positions))
            
            if len(all_lap_times) > 1:
                mean_lap_time = np.mean(all_lap_times)
                consistency_data['lap_time_consistency'] = float(np.std(all_lap_times) / mean_lap_time)
            
            if position_changes:
                consistency_data['position_stability'] = float(np.mean(position_changes))
            
            # Error rate (simplified - based on lap time outliers)
            if len(all_lap_times) > 5:
                outlier_threshold = np.percentile(all_lap_times, 95)
                outliers = [lt for lt in all_lap_times if lt > outlier_threshold]
                consistency_data['error_rate'] = float(len(outliers) / len(all_lap_times))
            
            return consistency_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_driver_specializations(self, driver, year):
        """Analyze driver specializations and strengths"""
        try:
            specializations = {
                'qualifying_specialist': False,
                'race_pace_specialist': False,
                'wet_weather_specialist': False,
                'overtaking_specialist': False,
                'consistency_specialist': False,
                'tyre_management_specialist': False
            }
            
            # This would require extensive data analysis across multiple sessions
            # For now, providing a simplified analysis framework
            
            # Sample analysis for one race
            sample_race_data = self.data_loader.load_session_data(year, 'Spain', 'Race')
            if sample_race_data:
                driver_laps = sample_race_data.laps.pick_driver(driver)
                if not driver_laps.empty:
                    # Consistency analysis
                    lap_times = [lt.total_seconds() for lt in driver_laps['LapTime'].dropna()]
                    if len(lap_times) > 5:
                        consistency_score = np.std(lap_times) / np.mean(lap_times)
                        if consistency_score < 0.02:  # Very consistent
                            specializations['consistency_specialist'] = True
                    
                    # Tire management (simplified)
                    if len(driver_laps) > 20:  # Long stint capability
                        stint_performance = self.analyze_stint_performance(driver_laps)
                        if stint_performance and stint_performance['degradation_rate'] < 0.1:
                            specializations['tyre_management_specialist'] = True
            
            return specializations
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_stint_performance(self, driver_laps):
        """Analyze stint performance for tire management assessment"""
        try:
            # Find longest stint
            compounds = driver_laps['Compound'].dropna()
            if compounds.empty:
                return None
            
            # Group by compound to find stints
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
            
            # Analyze longest stint
            longest_stint = max(stints, key=len) if stints else None
            if not longest_stint or len(longest_stint) < 5:
                return None
            
            # Calculate degradation rate
            stint_df = pd.DataFrame(longest_stint)
            lap_times = [lt.total_seconds() for lt in stint_df['LapTime']]
            
            # Linear regression to find degradation trend
            lap_numbers = list(range(len(lap_times)))
            degradation_rate = np.polyfit(lap_numbers, lap_times, 1)[0]
            
            return {
                'stint_length': len(longest_stint),
                'degradation_rate': float(degradation_rate),
                'compound': longest_stint[0]['Compound']
            }
            
        except Exception as e:
            return None
    
    def calculate_overall_rating(self, performance_stats, consistency_metrics):
        """Calculate overall driver rating"""
        try:
            rating_components = []
            
            # Performance component
            if performance_stats.get('average_race_position'):
                position_score = max(0, 21 - performance_stats['average_race_position']) / 20 * 100
                rating_components.append(position_score * 0.4)  # 40% weight
            
            # Consistency component
            if consistency_metrics.get('lap_time_consistency'):
                consistency_score = max(0, 1 - consistency_metrics['lap_time_consistency']) * 100
                rating_components.append(consistency_score * 0.3)  # 30% weight
            
            # Points component
            if performance_stats.get('points_scored') is not None:
                points_score = min(100, performance_stats['points_scored'] / 5)  # Normalize to 100
                rating_components.append(points_score * 0.3)  # 30% weight
            
            if rating_components:
                overall_rating = float(sum(rating_components) / len(rating_components))
                return {
                    'overall_score': overall_rating,
                    'rating_tier': self.get_rating_tier(overall_rating),
                    'components_analyzed': len(rating_components)
                }
            
            return {'overall_score': 50, 'rating_tier': 'unrated', 'components_analyzed': 0}
            
        except Exception as e:
            return {'overall_score': 50, 'rating_tier': 'error', 'components_analyzed': 0}
    
    def get_rating_tier(self, score):
        """Get rating tier based on score"""
        if score >= 90:
            return 'elite'
        elif score >= 80:
            return 'excellent'
        elif score >= 70:
            return 'very_good'
        elif score >= 60:
            return 'good'
        elif score >= 50:
            return 'average'
        else:
            return 'developing'
    
    def identify_strengths(self, performance_stats, specializations):
        """Identify driver strengths"""
        strengths = []
        
        # Performance-based strengths
        if performance_stats.get('average_qualifying_position', 20) < 8:
            strengths.append('Strong qualifying performance')
        
        if performance_stats.get('average_race_position', 20) < 8:
            strengths.append('Consistent race finishes')
        
        if performance_stats.get('podium_finishes', 0) > 0:
            strengths.append('Podium contender')
        
        if performance_stats.get('fastest_laps_count', 0) > 0:
            strengths.append('Strong race pace')
        
        # Specialization-based strengths
        for spec_name, is_specialist in specializations.items():
            if is_specialist:
                readable_name = spec_name.replace('_', ' ').title()
                strengths.append(readable_name)
        
        return strengths if strengths else ['Developing potential']
    
    def identify_improvement_areas(self, performance_stats, consistency_metrics):
        """Identify areas for improvement"""
        improvements = []
        
        # Performance improvements
        if performance_stats.get('average_qualifying_position', 0) > 12:
            improvements.append('Qualifying performance')
        
        if performance_stats.get('average_race_position', 0) > 12:
            improvements.append('Race execution')
        
        if performance_stats.get('dnf_count', 0) > 2:
            improvements.append('Reliability/consistency')
        
        # Consistency improvements
        if consistency_metrics.get('lap_time_consistency', 0) > 0.05:
            improvements.append('Lap time consistency')
        
        if consistency_metrics.get('error_rate', 0) > 0.1:
            improvements.append('Error reduction')
        
        return improvements if improvements else ['Maintain current performance level']
    
    def calculate_performance_rankings(self, year):
        """Calculate performance rankings across all drivers"""
        try:
            # Get all drivers from a sample race
            sample_race = self.get_sample_race_data(year)
            if not sample_race:
                return {'error': 'No race data available'}
            
            driver_rankings = {}
            
            for driver in sample_race.drivers:
                try:
                    performance_stats = self.calculate_driver_season_stats(driver, year)
                    consistency_metrics = self.calculate_consistency_metrics(driver, year)
                    overall_rating = self.calculate_overall_rating(performance_stats, consistency_metrics)
                    
                    driver_rankings[driver] = {
                        'overall_rating': overall_rating['overall_score'],
                        'average_position': performance_stats.get('average_race_position', 20),
                        'points_scored': performance_stats.get('points_scored', 0),
                        'consistency_score': 1 - consistency_metrics.get('lap_time_consistency', 1)
                    }
                
                except Exception as driver_error:
                    continue
            
            # Sort by overall rating
            sorted_rankings = sorted(
                driver_rankings.items(), 
                key=lambda x: x[1]['overall_rating'], 
                reverse=True
            )
            
            return {
                'rankings': [{'driver': driver, 'data': data} for driver, data in sorted_rankings],
                'total_drivers': len(sorted_rankings)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_team_dynamics(self, year):
        """Analyze team dynamics and teammate comparisons"""
        try:
            team_analysis = {}
            
            # Group drivers by team
            teams = {}
            for driver, team in DRIVER_TEAMS.items():
                if team not in teams:
                    teams[team] = []
                teams[team].append(driver)
            
            for team, drivers in teams.items():
                if len(drivers) >= 2:  # Only analyze teams with 2+ drivers
                    team_comparison = self.compare_teammates(drivers, year)
                    team_analysis[team] = team_comparison
            
            return team_analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def compare_teammates(self, drivers, year):
        """Compare teammates within a team"""
        try:
            if len(drivers) < 2:
                return {'error': 'Insufficient drivers for comparison'}
            
            driver_data = {}
            
            for driver in drivers[:2]:  # Compare first two drivers
                try:
                    performance_stats = self.calculate_driver_season_stats(driver, year)
                    consistency_metrics = self.calculate_consistency_metrics(driver, year)
                    
                    driver_data[driver] = {
                        'average_position': performance_stats.get('average_race_position', 20),
                        'average_qualifying': performance_stats.get('average_qualifying_position', 20),
                        'points_scored': performance_stats.get('points_scored', 0),
                        'consistency': consistency_metrics.get('lap_time_consistency', 1)
                    }
                
                except Exception as driver_error:
                    continue
            
            if len(driver_data) < 2:
                return {'error': 'Insufficient data for comparison'}
            
            # Compare the two drivers
            drivers_list = list(driver_data.keys())
            driver1, driver2 = drivers_list[0], drivers_list[1]
            
            comparison = {
                'driver_1': driver1,
                'driver_2': driver2,
                'performance_comparison': {
                    'qualifying_advantage': driver_data[driver1]['average_qualifying'] - driver_data[driver2]['average_qualifying'],
                    'race_advantage': driver_data[driver1]['average_position'] - driver_data[driver2]['average_position'],
                    'points_difference': driver_data[driver1]['points_scored'] - driver_data[driver2]['points_scored'],
                    'consistency_comparison': driver_data[driver1]['consistency'] - driver_data[driver2]['consistency']
                },
                'leading_driver': self.determine_leading_driver(driver_data),
                'team_dynamics_rating': self.rate_team_dynamics(driver_data)
            }
            
            return comparison
            
        except Exception as e:
            return {'error': str(e)}
    
    def determine_leading_driver(self, driver_data):
        """Determine which driver is leading based on multiple metrics"""
        try:
            drivers_list = list(driver_data.keys())
            if len(drivers_list) != 2:
                return 'unknown'
            
            driver1, driver2 = drivers_list[0], drivers_list[1]
            
            # Count wins in different categories
            wins = {driver1: 0, driver2: 0}
            
            # Better average position (lower is better)
            if driver_data[driver1]['average_position'] < driver_data[driver2]['average_position']:
                wins[driver1] += 1
            else:
                wins[driver2] += 1
            
            # Better qualifying (lower is better)
            if driver_data[driver1]['average_qualifying'] < driver_data[driver2]['average_qualifying']:
                wins[driver1] += 1
            else:
                wins[driver2] += 1
            
            # More points
            if driver_data[driver1]['points_scored'] > driver_data[driver2]['points_scored']:
                wins[driver1] += 1
            else:
                wins[driver2] += 1
            
            # Better consistency (lower is better)
            if driver_data[driver1]['consistency'] < driver_data[driver2]['consistency']:
                wins[driver1] += 1
            else:
                wins[driver2] += 1
            
            return driver1 if wins[driver1] > wins[driver2] else driver2
            
        except Exception as e:
            return 'unknown'
    
    def rate_team_dynamics(self, driver_data):
        """Rate team dynamics based on performance gap"""
        try:
            drivers_list = list(driver_data.keys())
            if len(drivers_list) != 2:
                return 'unknown'
            
            driver1, driver2 = drivers_list[0], drivers_list[1]
            
            # Calculate performance gaps
            position_gap = abs(driver_data[driver1]['average_position'] - driver_data[driver2]['average_position'])
            points_gap = abs(driver_data[driver1]['points_scored'] - driver_data[driver2]['points_scored'])
            
            # Rate based on gaps
            if position_gap < 2 and points_gap < 20:
                return 'very_close'
            elif position_gap < 4 and points_gap < 50:
                return 'competitive'
            elif position_gap < 6 and points_gap < 100:
                return 'moderate_gap'
            else:
                return 'large_gap'
                
        except Exception as e:
            return 'unknown'
    
    def get_career_statistics(self, year):
        """Get career statistics (simplified for this implementation)"""
        try:
            # This would typically require historical data across multiple years
            # For now, returning current season stats as career summary
            
            career_stats = {}
            sample_race = self.get_sample_race_data(year)
            
            if not sample_race:
                return {'error': 'No race data available'}
            
            for driver in sample_race.drivers:
                try:
                    season_stats = self.calculate_driver_season_stats(driver, year)
                    
                    # Simplified career stats (would need multi-year data)
                    career_stats[driver] = {
                        'seasons_analyzed': 1,
                        'career_races': season_stats.get('races_analyzed', 0),
                        'career_podiums': season_stats.get('podium_finishes', 0),
                        'career_points': season_stats.get('points_scored', 0),
                        'career_fastest_laps': season_stats.get('fastest_laps_count', 0),
                        'best_championship_position': 'TBD',  # Would need full season data
                        'experience_level': self.assess_experience_level(driver)
                    }
                
                except Exception as driver_error:
                    continue
            
            return career_stats
            
        except Exception as e:
            return {'error': str(e)}
    
    def assess_experience_level(self, driver):
        """Assess driver experience level (simplified)"""
        # This would typically use driver age, years in F1, etc.
        # For now, using a simplified classification
        return 'current_season'  # Would be replaced with actual experience data
    
    def generate_driver_comparisons(self, year):
        """Generate comprehensive driver comparisons"""
        try:
            sample_race = self.get_sample_race_data(year)
            if not sample_race:
                return {'error': 'No race data available'}
            
            comparisons = {}
            drivers = list(sample_race.drivers)
            
            # Generate comparisons for top drivers (limit for performance)
            for i, driver1 in enumerate(drivers[:8]):  # Top 8 drivers
                for driver2 in drivers[i+1:9]:  # Compare with next driver
                    try:
                        comparison_key = f"{driver1}_vs_{driver2}"
                        comparison = self.compare_two_drivers(driver1, driver2, year)
                        if comparison:
                            comparisons[comparison_key] = comparison
                    except Exception as comp_error:
                        continue
            
            return comparisons
            
        except Exception as e:
            return {'error': str(e)}
    
    def compare_two_drivers(self, driver1, driver2, year):
        """Compare two specific drivers"""
        try:
            # Get performance data for both drivers
            driver1_stats = self.calculate_driver_season_stats(driver1, year)
            driver2_stats = self.calculate_driver_season_stats(driver2, year)
            
            driver1_consistency = self.calculate_consistency_metrics(driver1, year)
            driver2_consistency = self.calculate_consistency_metrics(driver2, year)
            
            comparison = {
                'driver_1': {
                    'code': driver1,
                    'team': DRIVER_TEAMS.get(driver1, 'Unknown'),
                    'stats': driver1_stats,
                    'consistency': driver1_consistency
                },
                'driver_2': {
                    'code': driver2,
                    'team': DRIVER_TEAMS.get(driver2, 'Unknown'),
                    'stats': driver2_stats,
                    'consistency': driver2_consistency
                },
                'head_to_head': {
                    'qualifying_comparison': self.compare_metric(
                        driver1_stats.get('average_qualifying_position'),
                        driver2_stats.get('average_qualifying_position'),
                        lower_is_better=True
                    ),
                    'race_comparison': self.compare_metric(
                        driver1_stats.get('average_race_position'),
                        driver2_stats.get('average_race_position'),
                        lower_is_better=True
                    ),
                    'points_comparison': self.compare_metric(
                        driver1_stats.get('points_scored'),
                        driver2_stats.get('points_scored'),
                        lower_is_better=False
                    ),
                    'consistency_comparison': self.compare_metric(
                        driver1_consistency.get('lap_time_consistency'),
                        driver2_consistency.get('lap_time_consistency'),
                        lower_is_better=True
                    )
                }
            }
            
            return comparison
            
        except Exception as e:
            return None
    
    def compare_metric(self, value1, value2, lower_is_better=True):
        """Compare two metric values"""
        if value1 is None or value2 is None:
            return {'advantage': 'unknown', 'difference': None}
        
        difference = value1 - value2
        
        if lower_is_better:
            advantage = 'driver_1' if difference < 0 else 'driver_2' if difference > 0 else 'equal'
        else:
            advantage = 'driver_1' if difference > 0 else 'driver_2' if difference < 0 else 'equal'
        
        return {
            'advantage': advantage,
            'difference': float(abs(difference)),
            'percentage_difference': float(abs(difference) / max(abs(value1), abs(value2)) * 100) if max(abs(value1), abs(value2)) > 0 else 0
        }
    
    def get_sample_race_data(self, year):
        """Get sample race data for driver extraction"""
        try:
            # Try to get a mid-season race for representative driver lineup
            sample_races = ['Spain', 'Great Britain', 'Hungary', 'Italy', 'Bahrain']
            
            for race in sample_races:
                try:
                    session_data = self.data_loader.load_session_data(year, race, 'Race')
                    if session_data and hasattr(session_data, 'drivers'):
                        return session_data
                except Exception as race_error:
                    continue
            
            return None
            
        except Exception as e:
            return None
