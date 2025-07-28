import pandas as pd
import numpy as np
from utils.data_loader import DataLoader

class DownforceAnalyzer:
    """Analyze downforce settings and aerodynamic performance"""
    
    def __init__(self):
        self.data_loader = DataLoader()
    
    def analyze_downforce_settings(self, year, grand_prix, session):
        """Comprehensive downforce analysis"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return None
            
            analysis = {
                'aerodynamic_efficiency': self.analyze_aerodynamic_efficiency(session_data),
                'downforce_balance': self.analyze_downforce_balance(session_data),
                'drag_analysis': self.analyze_drag_characteristics(session_data),
                'corner_speed_analysis': self.analyze_corner_speeds(session_data),
                'straight_line_performance': self.analyze_straight_line_speed(session_data),
                'setup_comparison': self.compare_aerodynamic_setups(session_data),
                'track_specific_analysis': self.analyze_track_specific_requirements(session_data, grand_prix)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_aerodynamic_efficiency(self, session_data):
        """Analyze overall aerodynamic efficiency"""
        try:
            efficiency_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                fastest_lap = driver_laps.pick_fastest()
                telemetry = self.data_loader.get_telemetry_data(fastest_lap)
                
                if telemetry is None or telemetry.empty:
                    continue
                
                # Calculate aerodynamic efficiency metrics
                speed_data = telemetry['Speed']
                throttle_data = telemetry['Throttle']
                
                if speed_data.empty or throttle_data.empty:
                    continue
                
                # Analyze speed vs throttle relationship
                efficiency_metrics = self.calculate_aero_efficiency_metrics(speed_data, throttle_data)
                
                # Analyze corner vs straight performance
                corner_straight_analysis = self.analyze_corner_vs_straight_performance(telemetry)
                
                efficiency_data[driver] = {
                    'overall_efficiency_score': efficiency_metrics['efficiency_score'],
                    'speed_throttle_correlation': efficiency_metrics['correlation'],
                    'max_speed_achieved': float(speed_data.max()),
                    'avg_speed_high_throttle': efficiency_metrics['avg_speed_high_throttle'],
                    'corner_performance': corner_straight_analysis['corner_performance'],
                    'straight_performance': corner_straight_analysis['straight_performance'],
                    'efficiency_rating': self.rate_aerodynamic_efficiency(efficiency_metrics['efficiency_score'])
                }
            
            return efficiency_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_downforce_balance(self, session_data):
        """Analyze front/rear downforce balance"""
        try:
            balance_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                balance_analysis = []
                
                for _, lap in driver_laps.iterrows():
                    try:
                        telemetry = self.data_loader.get_telemetry_data(lap)
                        if telemetry is None or telemetry.empty:
                            continue
                        
                        # Analyze balance through speed and throttle patterns
                        balance_metrics = self.calculate_balance_metrics(telemetry)
                        
                        if balance_metrics:
                            balance_analysis.append({
                                'lap_number': int(lap['LapNumber']),
                                'balance_score': balance_metrics['balance_score'],
                                'understeer_tendency': balance_metrics['understeer_tendency'],
                                'oversteer_tendency': balance_metrics['oversteer_tendency'],
                                'corner_entry_balance': balance_metrics['corner_entry'],
                                'corner_exit_balance': balance_metrics['corner_exit']
                            })
                    
                    except Exception as lap_error:
                        continue
                
                if balance_analysis:
                    avg_balance = np.mean([ba['balance_score'] for ba in balance_analysis])
                    avg_understeer = np.mean([ba['understeer_tendency'] for ba in balance_analysis])
                    avg_oversteer = np.mean([ba['oversteer_tendency'] for ba in balance_analysis])
                    
                    balance_data[driver] = {
                        'lap_by_lap_analysis': balance_analysis,
                        'average_balance_score': float(avg_balance),
                        'understeer_tendency': float(avg_understeer),
                        'oversteer_tendency': float(avg_oversteer),
                        'balance_rating': self.rate_downforce_balance(avg_balance),
                        'setup_recommendation': self.recommend_balance_adjustment(avg_understeer, avg_oversteer)
                    }
            
            return balance_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_drag_characteristics(self, session_data):
        """Analyze drag characteristics and impact on performance"""
        try:
            drag_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                drag_analysis = []
                
                for _, lap in driver_laps.iterrows():
                    try:
                        telemetry = self.data_loader.get_telemetry_data(lap)
                        if telemetry is None or telemetry.empty:
                            continue
                        
                        # Analyze drag through deceleration patterns
                        drag_metrics = self.calculate_drag_metrics(telemetry)
                        
                        if drag_metrics:
                            drag_analysis.append({
                                'lap_number': int(lap['LapNumber']),
                                'drag_coefficient_estimate': drag_metrics['drag_estimate'],
                                'deceleration_efficiency': drag_metrics['decel_efficiency'],
                                'top_speed_loss': drag_metrics['top_speed_loss'],
                                'acceleration_impact': drag_metrics['accel_impact']
                            })
                    
                    except Exception as lap_error:
                        continue
                
                if drag_analysis:
                    avg_drag = np.mean([da['drag_coefficient_estimate'] for da in drag_analysis])
                    avg_top_speed_loss = np.mean([da['top_speed_loss'] for da in drag_analysis])
                    
                    drag_data[driver] = {
                        'lap_by_lap_analysis': drag_analysis,
                        'average_drag_estimate': float(avg_drag),
                        'average_top_speed_loss': float(avg_top_speed_loss),
                        'drag_efficiency_rating': self.rate_drag_efficiency(avg_drag),
                        'straight_line_impact': self.assess_straight_line_impact(avg_top_speed_loss)
                    }
            
            return drag_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_corner_speeds(self, session_data):
        """Analyze cornering speeds and downforce effectiveness"""
        try:
            corner_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                fastest_lap = driver_laps.pick_fastest()
                telemetry = self.data_loader.get_telemetry_data(fastest_lap)
                
                if telemetry is None or telemetry.empty:
                    continue
                
                # Identify corner sections
                corner_sections = self.identify_corner_sections(telemetry)
                
                corner_analysis = []
                for i, section in enumerate(corner_sections):
                    corner_metrics = self.analyze_corner_section(section, i + 1)
                    if corner_metrics:
                        corner_analysis.append(corner_metrics)
                
                if corner_analysis:
                    avg_corner_speed = np.mean([ca['avg_speed'] for ca in corner_analysis])
                    min_corner_speeds = [ca['min_speed'] for ca in corner_analysis]
                    
                    corner_data[driver] = {
                        'corner_by_corner_analysis': corner_analysis,
                        'average_corner_speed': float(avg_corner_speed),
                        'slowest_corner_speed': float(min(min_corner_speeds)),
                        'fastest_corner_speed': float(max([ca['max_speed'] for ca in corner_analysis])),
                        'corner_speed_consistency': float(np.std([ca['avg_speed'] for ca in corner_analysis])),
                        'downforce_effectiveness': self.rate_downforce_effectiveness(avg_corner_speed)
                    }
            
            return corner_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_straight_line_speed(self, session_data):
        """Analyze straight-line speed performance"""
        try:
            straight_line_data = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                fastest_lap = driver_laps.pick_fastest()
                telemetry = self.data_loader.get_telemetry_data(fastest_lap)
                
                if telemetry is None or telemetry.empty:
                    continue
                
                # Identify straight sections
                straight_sections = self.identify_straight_sections(telemetry)
                
                straight_analysis = []
                for i, section in enumerate(straight_sections):
                    straight_metrics = self.analyze_straight_section(section, i + 1)
                    if straight_metrics:
                        straight_analysis.append(straight_metrics)
                
                if straight_analysis:
                    max_speeds = [sa['max_speed'] for sa in straight_analysis]
                    acceleration_rates = [sa['acceleration_rate'] for sa in straight_analysis]
                    
                    straight_line_data[driver] = {
                        'straight_by_straight_analysis': straight_analysis,
                        'absolute_top_speed': float(max(max_speeds)),
                        'average_top_speed': float(np.mean(max_speeds)),
                        'average_acceleration_rate': float(np.mean(acceleration_rates)),
                        'straight_line_consistency': float(np.std(max_speeds)),
                        'drag_penalty_assessment': self.assess_drag_penalty(max_speeds)
                    }
            
            return straight_line_data
            
        except Exception as e:
            return {'error': str(e)}
    
    def compare_aerodynamic_setups(self, session_data):
        """Compare aerodynamic setups between drivers"""
        try:
            # This is a simplified comparison based on performance characteristics
            setup_comparison = {}
            
            all_driver_data = {}
            
            # Collect data for all drivers
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                fastest_lap = driver_laps.pick_fastest()
                telemetry = self.data_loader.get_telemetry_data(fastest_lap)
                
                if telemetry is None or telemetry.empty:
                    continue
                
                speed_data = telemetry['Speed']
                if speed_data.empty:
                    continue
                
                all_driver_data[driver] = {
                    'max_speed': float(speed_data.max()),
                    'avg_corner_speed': float(speed_data[speed_data < 200].mean() if len(speed_data[speed_data < 200]) > 0 else 0),
                    'speed_range': float(speed_data.max() - speed_data.min()),
                    'lap_time': float(fastest_lap['LapTime'].total_seconds())
                }
            
            if len(all_driver_data) < 2:
                return {'error': 'Insufficient data for comparison'}
            
            # Classify setups
            max_speeds = [data['max_speed'] for data in all_driver_data.values()]
            corner_speeds = [data['avg_corner_speed'] for data in all_driver_data.values()]
            
            speed_threshold = np.percentile(max_speeds, 50)
            corner_threshold = np.percentile(corner_speeds, 50)
            
            for driver, data in all_driver_data.items():
                if data['max_speed'] > speed_threshold and data['avg_corner_speed'] < corner_threshold:
                    setup_type = 'low_downforce'
                elif data['max_speed'] < speed_threshold and data['avg_corner_speed'] > corner_threshold:
                    setup_type = 'high_downforce'
                else:
                    setup_type = 'balanced'
                
                setup_comparison[driver] = {
                    'setup_type': setup_type,
                    'performance_data': data,
                    'relative_max_speed': float((data['max_speed'] - np.mean(max_speeds)) / np.std(max_speeds)),
                    'relative_corner_speed': float((data['avg_corner_speed'] - np.mean(corner_speeds)) / np.std(corner_speeds)),
                    'setup_effectiveness': self.rate_setup_effectiveness(data, setup_type)
                }
            
            return setup_comparison
            
        except Exception as e:
            return {'error': str(e)}
    
    def analyze_track_specific_requirements(self, session_data, grand_prix):
        """Analyze downforce requirements specific to the track"""
        try:
            # Track characteristics database (simplified)
            track_characteristics = {
                'Monaco': {'downforce_requirement': 'very_high', 'straight_line_importance': 'low'},
                'Monza': {'downforce_requirement': 'very_low', 'straight_line_importance': 'very_high'},
                'Silverstone': {'downforce_requirement': 'medium_high', 'straight_line_importance': 'medium'},
                'Spa': {'downforce_requirement': 'medium_low', 'straight_line_importance': 'high'},
                'Hungary': {'downforce_requirement': 'high', 'straight_line_importance': 'low'},
                'Singapore': {'downforce_requirement': 'high', 'straight_line_importance': 'low'},
                'Bahrain': {'downforce_requirement': 'medium', 'straight_line_importance': 'medium_high'},
                'default': {'downforce_requirement': 'medium', 'straight_line_importance': 'medium'}
            }
            
            track_info = track_characteristics.get(grand_prix, track_characteristics['default'])
            
            # Analyze how well drivers adapted to track requirements
            adaptation_analysis = {}
            
            for driver in session_data.drivers:
                driver_laps = session_data.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                fastest_lap = driver_laps.pick_fastest()
                telemetry = self.data_loader.get_telemetry_data(fastest_lap)
                
                if telemetry is None or telemetry.empty:
                    continue
                
                # Assess setup suitability for track
                setup_suitability = self.assess_setup_suitability(telemetry, track_info)
                
                adaptation_analysis[driver] = {
                    'track_requirements': track_info,
                    'setup_suitability_score': setup_suitability['suitability_score'],
                    'downforce_level_assessment': setup_suitability['downforce_level'],
                    'adaptation_rating': setup_suitability['adaptation_rating'],
                    'improvement_suggestions': setup_suitability['suggestions']
                }
            
            return {
                'track_characteristics': track_info,
                'driver_adaptations': adaptation_analysis,
                'optimal_setup_recommendation': self.recommend_optimal_setup(track_info)
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def calculate_aero_efficiency_metrics(self, speed_data, throttle_data):
        """Calculate aerodynamic efficiency metrics"""
        try:
            # Analyze speed vs throttle relationship
            high_throttle_mask = throttle_data > 95
            high_throttle_speeds = speed_data[high_throttle_mask]
            
            if len(high_throttle_speeds) == 0:
                return {'efficiency_score': 0, 'correlation': 0, 'avg_speed_high_throttle': 0}
            
            avg_speed_high_throttle = float(high_throttle_speeds.mean())
            max_possible_speed = float(speed_data.max())
            
            # Efficiency score based on ability to maintain high speeds with high throttle
            efficiency_score = (avg_speed_high_throttle / max_possible_speed) * 100
            
            # Calculate correlation between speed and throttle
            correlation = float(np.corrcoef(speed_data, throttle_data)[0, 1])
            
            return {
                'efficiency_score': efficiency_score,
                'correlation': correlation,
                'avg_speed_high_throttle': avg_speed_high_throttle
            }
            
        except Exception as e:
            return {'efficiency_score': 0, 'correlation': 0, 'avg_speed_high_throttle': 0}
    
    def analyze_corner_vs_straight_performance(self, telemetry):
        """Analyze corner vs straight line performance"""
        try:
            speed_data = telemetry['Speed']
            
            # Define corner and straight sections
            corner_speeds = speed_data[speed_data < 200]  # Simplified corner definition
            straight_speeds = speed_data[speed_data >= 200]  # Simplified straight definition
            
            corner_performance = float(corner_speeds.mean()) if len(corner_speeds) > 0 else 0
            straight_performance = float(straight_speeds.mean()) if len(straight_speeds) > 0 else 0
            
            return {
                'corner_performance': corner_performance,
                'straight_performance': straight_performance
            }
            
        except Exception as e:
            return {'corner_performance': 0, 'straight_performance': 0}
    
    def calculate_balance_metrics(self, telemetry):
        """Calculate downforce balance metrics"""
        try:
            speed_data = telemetry['Speed']
            throttle_data = telemetry['Throttle']
            brake_data = telemetry['Brake'] if 'Brake' in telemetry.columns else None
            
            if speed_data.empty or throttle_data.empty:
                return None
            
            # Simplified balance analysis based on speed and throttle patterns
            # This is a basic implementation - real analysis would require more sophisticated methods
            
            corner_entry_mask = (speed_data.diff() < -5) & (throttle_data < 50)
            corner_exit_mask = (speed_data.diff() > 5) & (throttle_data > 70)
            
            corner_entry_balance = self.calculate_section_balance(telemetry[corner_entry_mask])
            corner_exit_balance = self.calculate_section_balance(telemetry[corner_exit_mask])
            
            # Overall balance score (0-100, 50 is perfect balance)
            balance_score = (corner_entry_balance + corner_exit_balance) / 2
            
            # Simplified understeer/oversteer tendencies
            understeer_tendency = max(0, 50 - balance_score) * 2
            oversteer_tendency = max(0, balance_score - 50) * 2
            
            return {
                'balance_score': float(balance_score),
                'understeer_tendency': float(understeer_tendency),
                'oversteer_tendency': float(oversteer_tendency),
                'corner_entry': float(corner_entry_balance),
                'corner_exit': float(corner_exit_balance)
            }
            
        except Exception as e:
            return None
    
    def calculate_section_balance(self, section_telemetry):
        """Calculate balance for a specific section of track"""
        try:
            if section_telemetry.empty:
                return 50  # Neutral balance
            
            speed_data = section_telemetry['Speed']
            throttle_data = section_telemetry['Throttle']
            
            # Simplified balance calculation
            speed_consistency = speed_data.std()
            throttle_consistency = throttle_data.std()
            
            # Lower variability suggests better balance
            balance_score = 50 + (25 - min(25, speed_consistency / 2))
            
            return float(balance_score)
            
        except Exception as e:
            return 50
    
    def calculate_drag_metrics(self, telemetry):
        """Calculate drag-related metrics"""
        try:
            speed_data = telemetry['Speed']
            throttle_data = telemetry['Throttle']
            
            if speed_data.empty or throttle_data.empty:
                return None
            
            # Analyze deceleration patterns to estimate drag
            speed_diff = speed_data.diff()
            deceleration_mask = (speed_diff < -2) & (throttle_data < 10)  # Coasting deceleration
            
            if not any(deceleration_mask):
                return None
            
            deceleration_rates = -speed_diff[deceleration_mask]
            avg_deceleration = float(deceleration_rates.mean())
            
            # Simplified drag estimate (higher deceleration = higher drag)
            drag_estimate = avg_deceleration / 10  # Normalized estimate
            
            # Top speed analysis
            max_speed = float(speed_data.max())
            theoretical_max = 350  # Theoretical F1 max speed
            top_speed_loss = theoretical_max - max_speed
            
            return {
                'drag_estimate': drag_estimate,
                'decel_efficiency': float(avg_deceleration),
                'top_speed_loss': top_speed_loss,
                'accel_impact': self.estimate_acceleration_impact(drag_estimate)
            }
            
        except Exception as e:
            return None
    
    def estimate_acceleration_impact(self, drag_estimate):
        """Estimate impact of drag on acceleration"""
        # Simplified relationship between drag and acceleration impact
        return float(drag_estimate * 5)  # Higher drag reduces acceleration more
    
    def identify_corner_sections(self, telemetry):
        """Identify corner sections from telemetry"""
        try:
            speed_data = telemetry['Speed']
            sections = []
            
            # Simple corner identification based on speed
            in_corner = False
            corner_start = None
            
            for i, speed in enumerate(speed_data):
                if speed < 200 and not in_corner:  # Enter corner
                    in_corner = True
                    corner_start = i
                elif speed >= 200 and in_corner:  # Exit corner
                    in_corner = False
                    if corner_start is not None:
                        sections.append(telemetry.iloc[corner_start:i])
            
            return sections
            
        except Exception as e:
            return []
    
    def analyze_corner_section(self, section, corner_number):
        """Analyze individual corner section"""
        try:
            if section.empty:
                return None
            
            speed_data = section['Speed']
            
            return {
                'corner_number': corner_number,
                'min_speed': float(speed_data.min()),
                'max_speed': float(speed_data.max()),
                'avg_speed': float(speed_data.mean()),
                'speed_range': float(speed_data.max() - speed_data.min()),
                'section_length': len(section)
            }
            
        except Exception as e:
            return None
    
    def identify_straight_sections(self, telemetry):
        """Identify straight sections from telemetry"""
        try:
            speed_data = telemetry['Speed']
            sections = []
            
            # Simple straight identification based on speed
            in_straight = False
            straight_start = None
            
            for i, speed in enumerate(speed_data):
                if speed >= 250 and not in_straight:  # Enter straight
                    in_straight = True
                    straight_start = i
                elif speed < 250 and in_straight:  # Exit straight
                    in_straight = False
                    if straight_start is not None and i - straight_start > 10:  # Minimum length
                        sections.append(telemetry.iloc[straight_start:i])
            
            return sections
            
        except Exception as e:
            return []
    
    def analyze_straight_section(self, section, straight_number):
        """Analyze individual straight section"""
        try:
            if section.empty:
                return None
            
            speed_data = section['Speed']
            
            # Calculate acceleration rate
            speed_diff = speed_data.diff().dropna()
            avg_acceleration = float(speed_diff.mean()) if len(speed_diff) > 0 else 0
            
            return {
                'straight_number': straight_number,
                'max_speed': float(speed_data.max()),
                'min_speed': float(speed_data.min()),
                'acceleration_rate': avg_acceleration,
                'section_length': len(section),
                'speed_gain': float(speed_data.max() - speed_data.min())
            }
            
        except Exception as e:
            return None
    
    def assess_setup_suitability(self, telemetry, track_info):
        """Assess how suitable the setup is for the track"""
        try:
            speed_data = telemetry['Speed']
            
            # Analyze speed characteristics
            max_speed = float(speed_data.max())
            corner_speeds = speed_data[speed_data < 200]
            avg_corner_speed = float(corner_speeds.mean()) if len(corner_speeds) > 0 else 0
            
            # Assess based on track requirements
            downforce_req = track_info['downforce_requirement']
            straight_importance = track_info['straight_line_importance']
            
            suitability_score = 50  # Start with neutral
            
            # Adjust based on track requirements and actual performance
            if downforce_req == 'very_high':
                if avg_corner_speed > 150:
                    suitability_score += 25
                if max_speed < 300:
                    suitability_score += 10  # Less penalty for lower top speed
            elif downforce_req == 'very_low':
                if max_speed > 320:
                    suitability_score += 25
                if avg_corner_speed < 140:
                    suitability_score += 10  # Less penalty for lower corner speed
            
            # Determine downforce level
            if avg_corner_speed > 160 and max_speed < 310:
                downforce_level = 'high'
            elif avg_corner_speed < 140 and max_speed > 320:
                downforce_level = 'low'
            else:
                downforce_level = 'medium'
            
            # Generate suggestions
            suggestions = self.generate_setup_suggestions(downforce_level, track_info)
            
            return {
                'suitability_score': float(min(100, max(0, suitability_score))),
                'downforce_level': downforce_level,
                'adaptation_rating': self.rate_adaptation(suitability_score),
                'suggestions': suggestions
            }
            
        except Exception as e:
            return {
                'suitability_score': 50,
                'downforce_level': 'unknown',
                'adaptation_rating': 'unknown',
                'suggestions': []
            }
    
    def generate_setup_suggestions(self, current_downforce, track_info):
        """Generate setup suggestions based on analysis"""
        suggestions = []
        
        required_downforce = track_info['downforce_requirement']
        
        if required_downforce == 'very_high' and current_downforce != 'high':
            suggestions.append("Increase rear wing angle for better corner performance")
            suggestions.append("Consider higher front wing angle for balance")
        elif required_downforce == 'very_low' and current_downforce != 'low':
            suggestions.append("Reduce rear wing angle for better straight-line speed")
            suggestions.append("Lower front wing for reduced drag")
        elif required_downforce == 'medium' and current_downforce in ['high', 'low']:
            suggestions.append("Adjust wing angles toward more balanced setup")
        
        return suggestions
    
    def recommend_optimal_setup(self, track_info):
        """Recommend optimal setup for track"""
        downforce_req = track_info['downforce_requirement']
        
        recommendations = {
            'very_high': {
                'rear_wing': 'maximum',
                'front_wing': 'high',
                'setup_philosophy': 'maximum_downforce'
            },
            'high': {
                'rear_wing': 'high',
                'front_wing': 'medium_high',
                'setup_philosophy': 'downforce_priority'
            },
            'medium': {
                'rear_wing': 'medium',
                'front_wing': 'medium',
                'setup_philosophy': 'balanced'
            },
            'medium_low': {
                'rear_wing': 'medium_low',
                'front_wing': 'medium',
                'setup_philosophy': 'slight_speed_bias'
            },
            'very_low': {
                'rear_wing': 'minimum',
                'front_wing': 'low',
                'setup_philosophy': 'maximum_speed'
            }
        }
        
        return recommendations.get(downforce_req, recommendations['medium'])
    
    # Rating functions
    def rate_aerodynamic_efficiency(self, efficiency_score):
        """Rate aerodynamic efficiency"""
        if efficiency_score > 85:
            return 'excellent'
        elif efficiency_score > 75:
            return 'good'
        elif efficiency_score > 65:
            return 'average'
        else:
            return 'poor'
    
    def rate_downforce_balance(self, balance_score):
        """Rate downforce balance"""
        deviation = abs(balance_score - 50)
        if deviation < 5:
            return 'excellent'
        elif deviation < 10:
            return 'good'
        elif deviation < 20:
            return 'average'
        else:
            return 'poor'
    
    def rate_drag_efficiency(self, drag_estimate):
        """Rate drag efficiency"""
        if drag_estimate < 2:
            return 'excellent'
        elif drag_estimate < 4:
            return 'good'
        elif drag_estimate < 6:
            return 'average'
        else:
            return 'poor'
    
    def rate_downforce_effectiveness(self, avg_corner_speed):
        """Rate downforce effectiveness"""
        if avg_corner_speed > 160:
            return 'excellent'
        elif avg_corner_speed > 150:
            return 'good'
        elif avg_corner_speed > 140:
            return 'average'
        else:
            return 'poor'
    
    def assess_straight_line_impact(self, top_speed_loss):
        """Assess straight line impact"""
        if top_speed_loss < 10:
            return 'minimal'
        elif top_speed_loss < 20:
            return 'moderate'
        elif top_speed_loss < 30:
            return 'significant'
        else:
            return 'severe'
    
    def assess_drag_penalty(self, max_speeds):
        """Assess drag penalty based on top speeds"""
        avg_max_speed = np.mean(max_speeds)
        
        if avg_max_speed > 320:
            return 'low'
        elif avg_max_speed > 310:
            return 'moderate'
        elif avg_max_speed > 300:
            return 'high'
        else:
            return 'very_high'
    
    def rate_setup_effectiveness(self, performance_data, setup_type):
        """Rate setup effectiveness"""
        lap_time = performance_data['lap_time']
        
        # Simplified rating based on lap time (would need more context in reality)
        if lap_time < 90:  # Very fast lap
            return 'excellent'
        elif lap_time < 95:
            return 'good'
        elif lap_time < 100:
            return 'average'
        else:
            return 'poor'
    
    def rate_adaptation(self, suitability_score):
        """Rate adaptation to track requirements"""
        if suitability_score > 80:
            return 'excellent'
        elif suitability_score > 65:
            return 'good'
        elif suitability_score > 50:
            return 'average'
        else:
            return 'poor'
