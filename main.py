from app import app
from flask import render_template

@app.route('/telemetry')
def telemetry_dashboard():
    """Enhanced telemetry dashboard"""
    return render_template('telemetry_dashboard.html')

@app.route('/analytics')
def analytics_dashboard():
    """Advanced analytics dashboard"""
    return render_template('analytics_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)