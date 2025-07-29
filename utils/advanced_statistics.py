"""
Advanced Statistical Analysis for F1 Data
Provides comprehensive statistical analysis, predictive modeling, and advanced metrics
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from .data_loader import DataLoader
from .constants import TEAM_COLORS, DRIVER_TEAMS

class StatisticalAnalyzer:
    """Advanced statistical analysis for F1 performance data"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.logger = logging.getLogger(__name__)
    
    def perform_regression_analysis(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Perform regression analysis on lap time vs various factors"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return {'error': 'No session data available'}
            
            laps_data = session_data.laps
            if laps_data.empty:
                return {'error': 'No lap data available'}
            
            # Prepare data for regression
            analysis_data = []
            for driver in laps_data['Driver'].unique()[:10]:  # Limit to 10 drivers for performance
                driver_laps = laps_data[laps_data['Driver'] == driver].copy()
                
                if len(driver_laps) > 3:
                    driver_laps['LapTime_seconds'] = pd.to_timedelta(driver_laps['LapTime']).dt.total_seconds()
                    
                    for _, lap in driver_laps.iterrows():
                        analysis_data.append({
                            'driver': driver,
                            'lap_time': lap['LapTime_seconds'],
                            'tire_life': lap.get('TyreLife', 0),
                            'lap_number': lap['LapNumber'],
                            'compound': lap.get('Compound', 'Unknown'),
                            'track_status': lap.get('TrackStatus', 1),
                            'air_temp': lap.get('AirTemp', 25),
                            'track_temp': lap.get('TrackTemp', 35)
                        })
            
            if not analysis_data:
                return {'error': 'Insufficient data for regression analysis'}
            
            df = pd.DataFrame(analysis_data)
            
            # Perform multiple regression analyses
            results = {}
            
            # 1. Lap time vs tire life
            results['tire_degradation'] = self._analyze_tire_degradation(df)
            
            # 2. Lap time vs track temperature
            results['temperature_effect'] = self._analyze_temperature_effect(df)
            
            # 3. Driver performance consistency
            results['consistency_analysis'] = self._analyze_driver_consistency(df)
            
            # 4. Compound performance comparison
            results['compound_analysis'] = self._analyze_compound_performance(df)
            
            return {
                'regression_analysis': results,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                },
                'sample_size': len(df),
                'drivers_analyzed': len(df['driver'].unique())
            }
            
        except Exception as e:
            self.logger.error(f"Error in regression analysis: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_tire_degradation(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze tire degradation patterns"""
        try:
            # Filter out outliers
            q99 = df['lap_time'].quantile(0.99)
            q1 = df['lap_time'].quantile(0.01)
            filtered_df = df[(df['lap_time'] >= q1) & (df['lap_time'] <= q99)]
            
            if len(filtered_df) < 10:
                return {'error': 'Insufficient data for tire analysis'}
            
            X = filtered_df[['tire_life']].values
            y = filtered_df['lap_time'].values
            
            # Perform linear regression
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate R-squared
            r2 = model.score(X, y)
            
            # Calculate degradation rate (seconds per lap)
            degradation_rate = model.coef_[0]
            
            return {
                'degradation_rate_per_lap': float(degradation_rate),
                'r_squared': float(r2),
                'base_lap_time': float(model.intercept_),
                'correlation_strength': 'strong' if r2 > 0.7 else 'moderate' if r2 > 0.4 else 'weak',
                'sample_size': int(len(filtered_df))
            }
            
        except Exception as e:
            self.logger.error(f"Error in tire degradation analysis: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_temperature_effect(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze effect of track temperature on lap times"""
        try:
            # Remove outliers
            q99 = df['lap_time'].quantile(0.99)
            q1 = df['lap_time'].quantile(0.01)
            filtered_df = df[(df['lap_time'] >= q1) & (df['lap_time'] <= q99)]
            
            if len(filtered_df) < 10:
                return {'error': 'Insufficient data for temperature analysis'}
            
            X = filtered_df[['track_temp']].values
            y = filtered_df['lap_time'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            r2 = model.score(X, y)
            temp_effect = model.coef_[0]
            
            return {
                'temperature_effect_per_degree': float(temp_effect),
                'r_squared': float(r2),
                'optimal_temperature': float(filtered_df.loc[filtered_df['lap_time'].idxmin(), 'track_temp']),
                'temperature_range': {
                    'min': float(filtered_df['track_temp'].min()),
                    'max': float(filtered_df['track_temp'].max())
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in temperature analysis: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_driver_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze driver consistency using statistical measures"""
        try:
            consistency_data = {}
            
            for driver in df['driver'].unique():
                driver_data = df[df['driver'] == driver]
                
                if len(driver_data) > 3:
                    lap_times = driver_data['lap_time']
                    
                    # Calculate various consistency metrics
                    mean_time = lap_times.mean()
                    std_dev = lap_times.std()
                    cv = std_dev / mean_time  # Coefficient of variation
                    
                    # Calculate percentile ranges
                    p25 = lap_times.quantile(0.25)
                    p75 = lap_times.quantile(0.75)
                    iqr = p75 - p25
                    
                    consistency_data[driver] = {
                        'mean_lap_time': float(mean_time),
                        'standard_deviation': float(std_dev),
                        'coefficient_of_variation': float(cv),
                        'interquartile_range': float(iqr),
                        'consistency_score': float(1 / cv),  # Higher is more consistent
                        'lap_count': len(driver_data)
                    }
            
            # Rank drivers by consistency
            if consistency_data:
                sorted_drivers = sorted(consistency_data.items(), 
                                      key=lambda x: x[1]['coefficient_of_variation'])
                
                return {
                    'driver_consistency': consistency_data,
                    'most_consistent': sorted_drivers[0][0] if sorted_drivers else None,
                    'least_consistent': sorted_drivers[-1][0] if sorted_drivers else None
                }
            
            return {'error': 'No consistency data available'}
            
        except Exception as e:
            self.logger.error(f"Error in consistency analysis: {str(e)}")
            return {'error': str(e)}
    
    def _analyze_compound_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze performance differences between tire compounds"""
        try:
            compound_data = {}
            
            for compound in df['compound'].unique():
                if compound != 'Unknown':
                    compound_laps = df[df['compound'] == compound]
                    
                    if len(compound_laps) > 5:
                        lap_times = compound_laps['lap_time']
                        
                        compound_data[compound] = {
                            'mean_lap_time': float(lap_times.mean()),
                            'median_lap_time': float(lap_times.median()),
                            'fastest_lap': float(lap_times.min()),
                            'standard_deviation': float(lap_times.std()),
                            'sample_size': len(compound_laps),
                            'average_tire_life': float(compound_laps['tire_life'].mean())
                        }
            
            # Perform statistical tests between compounds
            compound_comparisons = {}
            compounds = list(compound_data.keys())
            
            for i, comp1 in enumerate(compounds):
                for comp2 in compounds[i+1:]:
                    comp1_times = df[df['compound'] == comp1]['lap_time']
                    comp2_times = df[df['compound'] == comp2]['lap_time']
                    
                    if len(comp1_times) > 5 and len(comp2_times) > 5:
                        # Perform t-test
                        t_stat, p_value = stats.ttest_ind(comp1_times, comp2_times)
                        
                        compound_comparisons[f"{comp1}_vs_{comp2}"] = {
                            't_statistic': float(t_stat),
                            'p_value': float(p_value),
                            'significant_difference': p_value < 0.05,
                            'faster_compound': comp1 if comp1_times.mean() < comp2_times.mean() else comp2,
                            'time_difference': float(abs(comp1_times.mean() - comp2_times.mean()))
                        }
            
            return {
                'compound_performance': compound_data,
                'statistical_comparisons': compound_comparisons
            }
            
        except Exception as e:
            self.logger.error(f"Error in compound analysis: {str(e)}")
            return {'error': str(e)}

class PredictiveModeling:
    """Predictive modeling for F1 performance"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.logger = logging.getLogger(__name__)
    
    def predict_lap_times(self, year: int, grand_prix: str, session: str, 
                         driver: str, tire_age: int, track_temp: float) -> Dict[str, Any]:
        """Predict lap times based on conditions"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return {'error': 'No session data available'}
            
            laps_data = session_data.laps
            driver_laps = laps_data[laps_data['Driver'] == driver].copy()
            
            if len(driver_laps) < 5:
                return {'error': f'Insufficient data for driver {driver}'}
            
            # Prepare features for prediction
            driver_laps['LapTime_seconds'] = pd.to_timedelta(driver_laps['LapTime']).dt.total_seconds()
            
            # Features: tire_life, track_temp, lap_number
            X = driver_laps[['TyreLife', 'LapNumber']].values
            y = driver_laps['LapTime_seconds'].values
            
            # Add track temperature if available
            if 'TrackTemp' in driver_laps.columns:
                X = np.column_stack([X, driver_laps['TrackTemp'].values])
            else:
                X = np.column_stack([X, np.full(len(X), track_temp)])
            
            # Train model
            model = LinearRegression()
            model.fit(X, y)
            
            # Predict for given conditions
            prediction_input = np.array([[tire_age, driver_laps['LapNumber'].max() + 1, track_temp]])
            predicted_time = model.predict(prediction_input)[0]
            
            # Calculate confidence interval
            residuals = y - model.predict(X)
            mse = np.mean(residuals ** 2)
            std_error = np.sqrt(mse)
            
            return {
                'predicted_lap_time': float(predicted_time),
                'confidence_interval': {
                    'lower': float(predicted_time - 1.96 * std_error),
                    'upper': float(predicted_time + 1.96 * std_error)
                },
                'model_accuracy': float(model.score(X, y)),
                'prediction_conditions': {
                    'tire_age': tire_age,
                    'track_temperature': track_temp,
                    'driver': driver
                },
                'baseline_performance': {
                    'fastest_lap': float(driver_laps['LapTime_seconds'].min()),
                    'average_lap': float(driver_laps['LapTime_seconds'].mean())
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in lap time prediction: {str(e)}")
            return {'error': str(e)}
    
    def cluster_driver_performance(self, year: int, grand_prix: str, session: str) -> Dict[str, Any]:
        """Cluster drivers based on performance characteristics"""
        try:
            session_data = self.data_loader.load_session_data(year, grand_prix, session)
            if session_data is None:
                return {'error': 'No session data available'}
            
            laps_data = session_data.laps
            
            # Calculate performance metrics for each driver
            driver_metrics = []
            driver_names = []
            
            for driver in laps_data['Driver'].unique():
                driver_laps = laps_data[laps_data['Driver'] == driver].copy()
                
                if len(driver_laps) > 3:
                    driver_laps['LapTime_seconds'] = pd.to_timedelta(driver_laps['LapTime']).dt.total_seconds()
                    
                    metrics = [
                        driver_laps['LapTime_seconds'].mean(),  # Average pace
                        driver_laps['LapTime_seconds'].std(),   # Consistency
                        driver_laps['LapTime_seconds'].min(),   # Peak performance
                        len(driver_laps)                        # Number of laps
                    ]
                    
                    driver_metrics.append(metrics)
                    driver_names.append(driver)
            
            if len(driver_metrics) < 3:
                return {'error': 'Insufficient drivers for clustering'}
            
            # Standardize features
            scaler = StandardScaler()
            scaled_metrics = scaler.fit_transform(driver_metrics)
            
            # Perform clustering
            n_clusters = min(3, len(driver_metrics))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(scaled_metrics)
            
            # Organize results
            cluster_results = {}
            for i in range(n_clusters):
                cluster_drivers = [driver_names[j] for j, cluster in enumerate(clusters) if cluster == i]
                
                # Calculate cluster characteristics
                cluster_data = [driver_metrics[j] for j, cluster in enumerate(clusters) if cluster == i]
                if cluster_data:
                    avg_pace = np.mean([d[0] for d in cluster_data])
                    avg_consistency = np.mean([d[1] for d in cluster_data])
                    
                    cluster_results[f"cluster_{i}"] = {
                        'drivers': cluster_drivers,
                        'characteristics': {
                            'average_pace': float(avg_pace),
                            'average_consistency': float(avg_consistency),
                            'cluster_size': len(cluster_drivers)
                        },
                        'performance_profile': self._characterize_cluster(avg_pace, avg_consistency)
                    }
            
            return {
                'clustering_results': cluster_results,
                'total_drivers': len(driver_names),
                'number_of_clusters': n_clusters,
                'session_info': {
                    'year': year,
                    'grand_prix': grand_prix,
                    'session': session
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in driver clustering: {str(e)}")
            return {'error': str(e)}
    
    def _characterize_cluster(self, avg_pace: float, avg_consistency: float) -> str:
        """Characterize a performance cluster"""
        if avg_consistency < 0.5:  # Low standard deviation = high consistency
            if avg_pace < 85:  # Fast pace
                return "elite_consistent"
            else:
                return "consistent_midfield"
        else:  # High variance
            if avg_pace < 85:
                return "fast_inconsistent" 
            else:
                return "struggling_variable"