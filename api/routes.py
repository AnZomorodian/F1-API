import logging
from flask import Blueprint, jsonify, request
from utils.data_loader import DataLoader
from utils.advanced_analytics import AdvancedF1Analytics
from utils.weather_analytics import WeatherAnalytics
from utils.race_strategy import RaceStrategyAnalyzer
from utils.tire_performance import TirePerformanceAnalyzer
from utils.stress_index import DriverStressAnalyzer
from utils.downforce_analysis import DownforceAnalyzer
from utils.brake_analysis import BrakeAnalyzer
from utils.composite_performance import CompositePerformanceAnalyzer
from utils.enhanced_analytics import EnhancedF1Analytics
from utils.driver_manager import DynamicDriverManager
from utils.visualizations import create_telemetry_plot, create_tire_strategy_plot, create_race_progression_plot
from utils.track_dominance import create_track_dominance_map
from utils.constants import GRANDS_PRIX, SESSIONS, TEAM_COLORS, DRIVER_TEAMS, TIRE_COLORS
import traceback

api_bp = Blueprint('api', __name__)

# Initialize data loader
data_loader = DataLoader()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'F1 Analytics API is running'
    })

@api_bp.route('/constants', methods=['GET'])
def get_constants():
    """Get F1 constants (teams, drivers, circuits, etc.)"""
    try:
        return jsonify({
            'grands_prix': GRANDS_PRIX,
            'sessions': SESSIONS,
            'team_colors': TEAM_COLORS,
            'driver_teams': DRIVER_TEAMS,
            'tire_colors': TIRE_COLORS
        })
    except Exception as e:
        logging.error(f"Error getting constants: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/seasons', methods=['GET'])
def get_available_seasons():
    """Get available F1 seasons"""
    try:
        # Return seasons from 2018 to current
        current_year = 2024
        seasons = list(range(2018, current_year + 1))
        return jsonify({
            'seasons': seasons,
            'current_season': current_year
        })
    except Exception as e:
        logging.error(f"Error getting seasons: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/session-data', methods=['GET'])
def get_session_data():
    """Get session data for a specific year, grand prix, and session"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        
        if not all([year, grand_prix, session]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session'}), 400
        
        session_data = data_loader.load_session_data(year, grand_prix, session)
        
        if session_data is None:
            return jsonify({'error': 'Failed to load session data'}), 404
            
        return jsonify({
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session,
                'date': str(session_data.date) if hasattr(session_data, 'date') else None,
                'circuit': session_data.event.Location if hasattr(session_data, 'event') else None
            },
            'drivers': session_data.drivers.tolist() if hasattr(session_data, 'drivers') else [],
            'laps_count': len(session_data.laps) if hasattr(session_data, 'laps') else 0
        })
        
    except Exception as e:
        logging.error(f"Error getting session data: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

@api_bp.route('/telemetry', methods=['GET'])
def get_telemetry_data():
    """Get telemetry data for specific drivers"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        drivers = request.args.getlist('drivers')
        
        if not all([year, grand_prix, session, drivers]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session, drivers'}), 400
        
        session_data = data_loader.load_session_data(year, grand_prix, session)
        if session_data is None:
            return jsonify({'error': 'Failed to load session data'}), 404
        
        telemetry_data = {}
        for driver in drivers:
            try:
                driver_laps = session_data.laps.pick_driver(driver)
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()
                    telemetry = fastest_lap.get_telemetry()
                    
                    telemetry_data[driver] = {
                        'lap_time': str(fastest_lap.LapTime),
                        'speed': telemetry['Speed'].tolist(),
                        'throttle': telemetry['Throttle'].tolist(),
                        'brake': telemetry['Brake'].tolist(),
                        'rpm': telemetry['RPM'].tolist(),
                        'gear': telemetry['nGear'].tolist(),
                        'distance': telemetry['Distance'].tolist()
                    }
            except Exception as driver_error:
                logging.warning(f"Error processing driver {driver}: {str(driver_error)}")
                continue
        
        return jsonify({
            'telemetry_data': telemetry_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting telemetry data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/lap-times', methods=['GET'])
def get_lap_times():
    """Get lap times for all drivers in a session"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        
        if not all([year, grand_prix, session]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session'}), 400
        
        session_data = data_loader.load_session_data(year, grand_prix, session)
        if session_data is None:
            return jsonify({'error': 'Failed to load session data'}), 404
        
        lap_times = {}
        for driver in session_data.drivers:
            try:
                driver_laps = session_data.laps.pick_driver(driver)
                if not driver_laps.empty:
                    lap_times[driver] = {
                        'lap_numbers': driver_laps['LapNumber'].tolist(),
                        'lap_times': [str(lap_time) for lap_time in driver_laps['LapTime']],
                        'fastest_lap': str(driver_laps.pick_fastest()['LapTime']),
                        'compound': driver_laps['Compound'].tolist(),
                        'tire_life': driver_laps['TyreLife'].tolist()
                    }
            except Exception as driver_error:
                logging.warning(f"Error processing driver {driver}: {str(driver_error)}")
                continue
        
        return jsonify({
            'lap_times': lap_times,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting lap times: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tire-strategy', methods=['GET'])
def get_tire_strategy():
    """Get tire strategy analysis for a race"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        
        if not all([year, grand_prix]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix'}), 400
        
        analyzer = TirePerformanceAnalyzer()
        tire_data = analyzer.analyze_race_tire_performance(year, grand_prix)
        
        return jsonify({
            'tire_strategy': tire_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting tire strategy: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/weather-analysis', methods=['GET'])
def get_weather_analysis():
    """Get weather analysis for a session"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        
        if not all([year, grand_prix, session]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session'}), 400
        
        analyzer = WeatherAnalytics()
        weather_data = analyzer.analyze_session_weather(year, grand_prix, session)
        
        return jsonify({
            'weather_analysis': weather_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting weather analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/race-strategy', methods=['GET'])
def get_race_strategy():
    """Get race strategy analysis"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        
        if not all([year, grand_prix]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix'}), 400
        
        analyzer = RaceStrategyAnalyzer()
        strategy_data = analyzer.analyze_race_strategy(year, grand_prix)
        
        return jsonify({
            'race_strategy': strategy_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting race strategy: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/driver-stress', methods=['GET'])
def get_driver_stress():
    """Get driver stress analysis"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        driver = request.args.get('driver')
        
        if not all([year, grand_prix, session, driver]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session, driver'}), 400
        
        analyzer = DriverStressAnalyzer()
        stress_data = analyzer.analyze_driver_stress(year, grand_prix, session, driver)
        
        return jsonify({
            'stress_analysis': stress_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session,
                'driver': driver
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting driver stress analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/downforce-analysis', methods=['GET'])
def get_downforce_analysis():
    """Get downforce analysis"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        
        if not all([year, grand_prix, session]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session'}), 400
        
        analyzer = DownforceAnalyzer()
        downforce_data = analyzer.analyze_downforce_settings(year, grand_prix, session)
        
        return jsonify({
            'downforce_analysis': downforce_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting downforce analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/brake-analysis', methods=['GET'])
def get_brake_analysis():
    """Get brake analysis"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        driver = request.args.get('driver')
        
        if not all([year, grand_prix, session, driver]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session, driver'}), 400
        
        analyzer = BrakeAnalyzer()
        brake_data = analyzer.analyze_braking_performance(year, grand_prix, session, driver)
        
        return jsonify({
            'brake_analysis': brake_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session,
                'driver': driver
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting brake analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/composite-performance', methods=['GET'])
def get_composite_performance():
    """Get composite performance analysis"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        
        if not all([year, grand_prix, session]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session'}), 400
        
        analyzer = CompositePerformanceAnalyzer()
        performance_data = analyzer.analyze_composite_performance(year, grand_prix, session)
        
        return jsonify({
            'composite_performance': performance_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting composite performance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/advanced-analytics', methods=['GET'])
def get_advanced_analytics():
    """Get advanced analytics for a session"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        
        if not all([year, grand_prix, session]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session'}), 400
        
        analyzer = AdvancedF1Analytics()
        analytics_data = analyzer.comprehensive_session_analysis(year, grand_prix, session)
        
        return jsonify({
            'advanced_analytics': analytics_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting advanced analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/enhanced-analytics', methods=['GET'])
def get_enhanced_analytics():
    """Get enhanced analytics with multiple analysis types"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        
        if not all([year, grand_prix, session]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session'}), 400
        
        analyzer = EnhancedF1Analytics()
        enhanced_data = analyzer.enhanced_session_analysis(year, grand_prix, session)
        
        return jsonify({
            'enhanced_analytics': enhanced_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting enhanced analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/track-dominance', methods=['GET'])
def get_track_dominance():
    """Get track dominance analysis"""
    try:
        year = request.args.get('year', type=int)
        grand_prix = request.args.get('grand_prix')
        session = request.args.get('session')
        
        if not all([year, grand_prix, session]):
            return jsonify({'error': 'Missing required parameters: year, grand_prix, session'}), 400
        
        dominance_data = create_track_dominance_map(year, grand_prix, session)
        
        return jsonify({
            'track_dominance': dominance_data,
            'session_info': {
                'year': year,
                'grand_prix': grand_prix,
                'session': session
            }
        })
        
    except Exception as e:
        logging.error(f"Error getting track dominance: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/driver-manager', methods=['GET'])
def get_driver_manager_data():
    """Get dynamic driver manager data"""
    try:
        year = request.args.get('year', type=int)
        
        if not year:
            return jsonify({'error': 'Missing required parameter: year'}), 400
        
        manager = DynamicDriverManager()
        driver_data = manager.get_season_driver_data(year)
        
        return jsonify({
            'driver_manager_data': driver_data,
            'year': year
        })
        
    except Exception as e:
        logging.error(f"Error getting driver manager data: {str(e)}")
        return jsonify({'error': str(e)}), 500
