"""
Championship Tracking and Points Analysis Module
Track driver and constructor championship standings with predictions
"""

import fastf1
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

class ChampionshipTracker:
    """Track and analyze championship standings and predictions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.points_system = {
            1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1
        }
    
    def get_season_standings(self, year: int, up_to_race: Optional[str] = None) -> Dict[str, Any]:
        """Get current season championship standings"""
        try:
            # Get the season schedule
            schedule = fastf1.get_event_schedule(year)
            
            driver_points = {}
            constructor_points = {}
            race_results = []
            
            # Process each race up to the specified race
            for idx, event in schedule.iterrows():
                race_name = event['EventName']
                
                # Stop if we've reached the specified race
                if up_to_race and race_name == up_to_race:
                    break
                
                try:
                    # Load race session
                    session = fastf1.get_session(year, race_name, 'Race')
                    session.load()
                    
                    if hasattr(session, 'results') and session.results is not None:
                        results = session.results
                        race_points = {}
                        
                        for _, driver_result in results.iterrows():
                            driver = driver_result.get('Abbreviation')
                            position = driver_result.get('Position')
                            team = driver_result.get('TeamName')
                            
                            if driver and position and position <= 10:
                                points = self.points_system.get(position, 0)
                                
                                # Add to driver standings
                                if driver not in driver_points:
                                    driver_points[driver] = {
                                        'points': 0,
                                        'name': f"{driver_result.get('FirstName', '')} {driver_result.get('LastName', '')}".strip(),
                                        'team': team,
                                        'race_results': []
                                    }
                                
                                driver_points[driver]['points'] += points
                                driver_points[driver]['race_results'].append({
                                    'race': race_name,
                                    'position': position,
                                    'points': points
                                })
                                
                                # Add to constructor standings
                                if team:
                                    if team not in constructor_points:
                                        constructor_points[team] = {'points': 0, 'drivers': set()}
                                    constructor_points[team]['points'] += points
                                    constructor_points[team]['drivers'].add(driver)
                                
                                race_points[driver] = points
                        
                        race_results.append({
                            'race': race_name,
                            'date': str(event.get('Session5Date', event.get('EventDate', 'Unknown'))),
                            'points_awarded': race_points
                        })
                
                except Exception as race_error:
                    self.logger.warning(f"Error processing race {race_name}: {str(race_error)}")
                    continue
            
            # Sort standings
            driver_standings = sorted(driver_points.items(), key=lambda x: x[1]['points'], reverse=True)
            constructor_standings = sorted(constructor_points.items(), key=lambda x: x[1]['points'], reverse=True)
            
            return {
                'driver_standings': [
                    {
                        'position': idx + 1,
                        'driver': driver,
                        'name': data['name'],
                        'team': data['team'],
                        'points': data['points'],
                        'race_results': data['race_results']
                    }
                    for idx, (driver, data) in enumerate(driver_standings)
                ],
                'constructor_standings': [
                    {
                        'position': idx + 1,
                        'team': team,
                        'points': data['points'],
                        'drivers': list(data['drivers'])
                    }
                    for idx, (team, data) in enumerate(constructor_standings)
                ],
                'season_info': {
                    'year': year,
                    'races_processed': len(race_results),
                    'total_races': len(schedule)
                },
                'race_results': race_results
            }
            
        except Exception as e:
            self.logger.error(f"Error getting season standings: {str(e)}")
            return {'error': str(e)}
    
    def predict_championship_outcome(self, year: int, current_standings: Dict) -> Dict[str, Any]:
        """Predict championship outcome based on current form"""
        try:
            # Get remaining races
            schedule = fastf1.get_event_schedule(year)
            races_completed = current_standings.get('season_info', {}).get('races_processed', 0)
            total_races = len(schedule)
            remaining_races = total_races - races_completed
            
            if remaining_races <= 0:
                return {'message': 'Season completed', 'remaining_races': 0}
            
            # Calculate maximum possible points
            max_points_per_race = 25  # Win + fastest lap
            max_remaining_points = remaining_races * max_points_per_race
            
            predictions = []
            driver_standings = current_standings.get('driver_standings', [])
            
            if driver_standings:
                leader_points = driver_standings[0]['points']
                
                for driver_data in driver_standings:
                    current_points = driver_data['points']
                    points_behind = leader_points - current_points
                    max_possible = current_points + max_remaining_points
                    
                    # Calculate championship probability (simplified)
                    if points_behind <= max_remaining_points:
                        if points_behind == 0:
                            probability = 85.0  # Leader advantage
                        elif points_behind <= max_remaining_points * 0.3:
                            probability = 60.0  # Strong contender
                        elif points_behind <= max_remaining_points * 0.6:
                            probability = 25.0  # Outside chance
                        else:
                            probability = 5.0   # Mathematical possibility
                    else:
                        probability = 0.0  # Mathematically eliminated
                    
                    predictions.append({
                        'driver': driver_data['driver'],
                        'current_points': current_points,
                        'max_possible_points': max_possible,
                        'points_behind_leader': points_behind,
                        'championship_probability': probability,
                        'mathematically_possible': points_behind <= max_remaining_points
                    })
            
            return {
                'championship_predictions': predictions,
                'remaining_races': remaining_races,
                'max_points_available': max_remaining_points,
                'season_info': {
                    'year': year,
                    'races_completed': races_completed,
                    'total_races': total_races
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting championship: {str(e)}")
            return {'error': str(e)}
    
    def get_head_to_head_comparison(self, year: int, driver1: str, driver2: str) -> Dict[str, Any]:
        """Compare two drivers head-to-head across the season"""
        try:
            schedule = fastf1.get_event_schedule(year)
            
            comparison = {
                'driver1': driver1,
                'driver2': driver2,
                'head_to_head_wins': {driver1: 0, driver2: 0},
                'race_comparisons': [],
                'qualifying_comparisons': [],
                'average_positions': {driver1: [], driver2: []},
                'points_comparison': {driver1: 0, driver2: 0}
            }
            
            for idx, event in schedule.iterrows():
                race_name = event['EventName']
                
                try:
                    # Race comparison
                    race_session = fastf1.get_session(year, race_name, 'Race')
                    race_session.load()
                    
                    if hasattr(race_session, 'results') and race_session.results is not None:
                        results = race_session.results
                        
                        driver1_result = results[results['Abbreviation'] == driver1]
                        driver2_result = results[results['Abbreviation'] == driver2]
                        
                        if not driver1_result.empty and not driver2_result.empty:
                            pos1 = driver1_result.iloc[0]['Position']
                            pos2 = driver2_result.iloc[0]['Position']
                            
                            comparison['race_comparisons'].append({
                                'race': race_name,
                                driver1: pos1,
                                driver2: pos2,
                                'winner': driver1 if pos1 < pos2 else driver2
                            })
                            
                            if pos1 < pos2:
                                comparison['head_to_head_wins'][driver1] += 1
                            elif pos2 < pos1:
                                comparison['head_to_head_wins'][driver2] += 1
                            
                            comparison['average_positions'][driver1].append(pos1)
                            comparison['average_positions'][driver2].append(pos2)
                            
                            # Points comparison
                            points1 = self.points_system.get(pos1, 0) if pos1 <= 10 else 0
                            points2 = self.points_system.get(pos2, 0) if pos2 <= 10 else 0
                            comparison['points_comparison'][driver1] += points1
                            comparison['points_comparison'][driver2] += points2
                    
                    # Qualifying comparison
                    quali_session = fastf1.get_session(year, race_name, 'Qualifying')
                    quali_session.load()
                    
                    if hasattr(quali_session, 'results') and quali_session.results is not None:
                        quali_results = quali_session.results
                        
                        driver1_quali = quali_results[quali_results['Abbreviation'] == driver1]
                        driver2_quali = quali_results[quali_results['Abbreviation'] == driver2]
                        
                        if not driver1_quali.empty and not driver2_quali.empty:
                            quali_pos1 = driver1_quali.iloc[0]['Position']
                            quali_pos2 = driver2_quali.iloc[0]['Position']
                            
                            comparison['qualifying_comparisons'].append({
                                'race': race_name,
                                driver1: quali_pos1,
                                driver2: quali_pos2,
                                'winner': driver1 if quali_pos1 < quali_pos2 else driver2
                            })
                
                except Exception as race_error:
                    self.logger.warning(f"Error processing {race_name} for comparison: {str(race_error)}")
                    continue
            
            # Calculate averages
            if comparison['average_positions'][driver1]:
                comparison['average_race_position'] = {
                    driver1: np.mean(comparison['average_positions'][driver1]),
                    driver2: np.mean(comparison['average_positions'][driver2])
                }
            
            return comparison
            
        except Exception as e:
            self.logger.error(f"Error getting head-to-head comparison: {str(e)}")
            return {'error': str(e)}
    
    def get_team_performance_analysis(self, year: int, team_name: str) -> Dict[str, Any]:
        """Analyze team performance across the season"""
        try:
            schedule = fastf1.get_event_schedule(year)
            
            team_analysis = {
                'team': team_name,
                'drivers': set(),
                'race_results': [],
                'total_points': 0,
                'podium_finishes': 0,
                'wins': 0,
                'double_points_finishes': 0,
                'average_finish_position': []
            }
            
            for idx, event in schedule.iterrows():
                race_name = event['EventName']
                
                try:
                    race_session = fastf1.get_session(year, race_name, 'Race')
                    race_session.load()
                    
                    if hasattr(race_session, 'results') and race_session.results is not None:
                        results = race_session.results
                        team_results = results[results['TeamName'] == team_name]
                        
                        if not team_results.empty:
                            race_data = {
                                'race': race_name,
                                'drivers': {},
                                'team_points': 0
                            }
                            
                            both_in_points = True
                            for _, driver_result in team_results.iterrows():
                                driver = driver_result['Abbreviation']
                                position = driver_result['Position']
                                points = self.points_system.get(position, 0) if position <= 10 else 0
                                
                                team_analysis['drivers'].add(driver)
                                race_data['drivers'][driver] = {
                                    'position': position,
                                    'points': points
                                }
                                race_data['team_points'] += points
                                team_analysis['total_points'] += points
                                team_analysis['average_finish_position'].append(position)
                                
                                # Track special achievements
                                if position <= 3:
                                    team_analysis['podium_finishes'] += 1
                                if position == 1:
                                    team_analysis['wins'] += 1
                                if position > 10:
                                    both_in_points = False
                            
                            if both_in_points and len(team_results) == 2:
                                team_analysis['double_points_finishes'] += 1
                            
                            team_analysis['race_results'].append(race_data)
                
                except Exception as race_error:
                    self.logger.warning(f"Error processing {race_name} for team analysis: {str(race_error)}")
                    continue
            
            # Calculate final statistics
            if team_analysis['average_finish_position']:
                team_analysis['average_finish_position'] = np.mean(team_analysis['average_finish_position'])
            
            team_analysis['drivers'] = list(team_analysis['drivers'])
            
            return team_analysis
            
        except Exception as e:
            self.logger.error(f"Error getting team performance analysis: {str(e)}")
            return {'error': str(e)}