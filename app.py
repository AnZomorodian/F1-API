import os
import logging
from flask import Flask, jsonify, render_template
from flask.logging import default_handler
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "f1-analytics-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Import and register blueprints
from api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def home():
    """Home route showing enhanced API documentation"""
    return render_template('enhanced_documentation.html')

@app.route('/docs')
def docs():
    """Original documentation route"""
    return render_template('documentation.html')

@app.route('/telemetry')
def telemetry_dashboard():
    """Telemetry visualization dashboard"""
    return render_template('telemetry_dashboard.html')

@app.route('/analytics')
def analytics_dashboard():
    """Advanced analytics dashboard"""
    return render_template('analytics_dashboard.html')

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad Request',
        'message': 'Invalid request parameters'
    }), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
