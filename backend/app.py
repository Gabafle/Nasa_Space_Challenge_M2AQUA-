# backend/app.py - Complete version with all routes
from flask import Flask, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime
import json
import logging

# Add this import at the top
from services.csv_validator import EnhancedCSVValidator

# Import config
from config import Config

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
from models import db, User, Dataset, Analysis
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def convert_numpy_types(obj):
    """
    Recursively convert numpy/pandas types to native Python types for JSON serialization
    """
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, pd.Int64Dtype)):
        return int(obj)
    elif isinstance(obj, (np.floating, pd.Float64Dtype)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.to_dict()
    elif hasattr(obj, 'item'):  # Handle numpy scalars
        return obj.item()
    else:
        return obj

# Validation functions (FIXED)
def validate_csv_data(filepath, filename):
    """Enhanced CSV validation with detailed error reporting"""
    errors = []
    warnings = []
    
    try:
        df = None
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(filepath, encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            return {
                'valid': False,
                'errors': [{'line': 0, 'column': '', 'error': 'Could not read file with any supported encoding', 'value': ''}],
                'warnings': [],
                'summary': {'total_rows': 0, 'total_columns': 0}
            }
        
        if df.empty:
            errors.append({'line': 0, 'column': '', 'error': 'CSV file is completely empty', 'value': ''})
        
        # Check for completely empty rows
        empty_rows = df.isnull().all(axis=1)
        for idx in empty_rows[empty_rows].index:
            if len(errors) >= 10:
                break
            errors.append({
                'line': int(idx + 2),  # Convert to Python int
                'column': 'all',
                'error': 'Completely empty row',
                'value': ''
            })
        
        # Check for duplicate column names
        if len(df.columns) != len(set(df.columns)):
            duplicated_cols = df.columns[df.columns.duplicated()]
            for col in duplicated_cols:
                errors.append({
                    'line': 1,
                    'column': str(col),
                    'error': f'Duplicate column name: {col}',
                    'value': str(col)
                })
        
        # Enhanced data type consistency validation
        for col in df.columns:
            non_null_data = df[col].dropna()
            if len(non_null_data) == 0:
                continue
                
            sample_data = non_null_data.head(min(100, len(non_null_data)))
            
            numeric_count = 0
            string_count = 0
            inconsistent_rows = []
            
            for idx, value in sample_data.items():
                str_value = str(value).strip()
                
                try:
                    float(str_value.replace(',', ''))
                    numeric_count += 1
                except (ValueError, TypeError):
                    string_count += 1
                    if len(inconsistent_rows) < 3:
                        inconsistent_rows.append({
                            'line': int(idx + 2),  # Convert to Python int
                            'column': str(col),
                            'error': f'Non-numeric value "{str_value}" in potentially numeric column',
                            'value': str_value
                        })
            
            if numeric_count > 0 and string_count > 0 and numeric_count > string_count:
                errors.extend(inconsistent_rows)
        
        # Check for suspicious null-like values
        suspicious_values = ['N/A', 'n/a', 'null', 'NULL', 'None', '#N/A', '#NULL!', 'undefined', '', ' ']
        
        for col in df.columns:
            non_null_data = df[col].dropna()
            problematic_suspicious = []
            
            for idx, value in non_null_data.items():
                if len(problematic_suspicious) >= 3:
                    break
                    
                if str(value).strip() in suspicious_values:
                    problematic_suspicious.append({
                        'line': int(idx + 2),  # Convert to Python int
                        'column': str(col),
                        'error': f'Suspicious null-like value: "{value}"',
                        'value': str(value)
                    })
            
            errors.extend(problematic_suspicious)
        
        # FIXED: Convert all numpy types to Python types
        summary = {
            'total_rows': int(len(df)),
            'total_columns': int(len(df.columns)),
            'missing_values': int(df.isnull().sum().sum()),
            'duplicate_rows': int(df.duplicated().sum())
        }
        
        return {
            'valid': len(errors) == 0,
            'errors': errors[:10],
            'warnings': warnings[:5],
            'summary': summary
        }
        
    except Exception as e:
        return {
            'valid': False,
            'errors': [{'line': 0, 'column': '', 'error': f'Failed to process CSV: {str(e)}', 'value': ''}],
            'warnings': [],
            'summary': {'total_rows': 0, 'total_columns': 0}
        }

def create_error_report(validation_result, filename):
    """Create detailed error report file"""
    report_lines = [
        f"CSV Validation Report for: {filename}",
        f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        "SUMMARY:",
        f"Total Rows: {validation_result['summary']['total_rows']}",
        f"Total Columns: {validation_result['summary']['total_columns']}",
        f"Validation Status: {'PASSED' if validation_result['valid'] else 'FAILED'}",
        f"Total Errors: {len(validation_result['errors'])}",
        f"Total Warnings: {len(validation_result['warnings'])}",
        ""
    ]
    
    if validation_result['errors']:
        report_lines.append("ERRORS:")
        report_lines.append("-" * 30)
        for i, error in enumerate(validation_result['errors'], 1):
            report_lines.append(f"{i}. Line {error['line']}, Column '{error['column']}': {error['error']}")
            if error['value']:
                report_lines.append(f"   Problematic value: '{error['value']}'")
        report_lines.append("")
    
    if validation_result['warnings']:
        report_lines.append("WARNINGS:")
        report_lines.append("-" * 30)
        for i, warning in enumerate(validation_result['warnings'], 1):
            report_lines.append(f"{i}. Line {warning['line']}, Column '{warning['column']}': {warning['error']}")
        report_lines.append("")
    
    report_lines.extend([
        "RECOMMENDATIONS:",
        "- Fix all errors before proceeding with data analysis",
        "- Review warnings for data quality improvements",
        "- Ensure consistent data types within columns",
        "- Remove or properly handle missing values",
        "- Consider data standardization for better analysis results"
    ])
    
    return "\n".join(report_lines)

# =============================================================================
# AUTHENTICATION ROUTES
# =============================================================================

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        
        if User.query.filter_by(email=data.get('email')).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            email=data.get('email'),
            name=data.get('name'),
            role=data.get('role', 'user')
        )
        user.set_password(data.get('password'))
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'message': 'User created successfully', 'user': user.to_dict()}), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify(user.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Get user error: {str(e)}")
        return jsonify({'error': 'Failed to get user info'}), 500

# =============================================================================
# DATASET ROUTES
# =============================================================================

@app.route('/api/datasets', methods=['GET'])
@jwt_required()
def get_datasets():
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        show_public = request.args.get('show_public', 'true').lower() == 'true'
        
        if show_public:
            # Show user's own datasets + public datasets from others
            query = Dataset.query.filter(
                db.or_(Dataset.user_id == user_id, Dataset.is_public == True)
            )
        else:
            # Show only user's own datasets
            query = Dataset.query.filter_by(user_id=user_id)
        
        paginated = query.order_by(Dataset.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        datasets = []
        for dataset in paginated.items:
            dataset_dict = dataset.to_dict()
            # Add owner name
            owner = User.query.get(dataset.user_id)
            dataset_dict['owner_name'] = owner.name if owner else 'Unknown'
            datasets.append(dataset_dict)
        
        return jsonify({
            'datasets': datasets,
            'pagination': {
                'page': page,
                'pages': paginated.pages,
                'per_page': per_page,
                'total': paginated.total
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get datasets error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/datasets/<int:dataset_id>', methods=['DELETE'])
@jwt_required()
def delete_dataset(dataset_id):
    try:
        user_id = int(get_jwt_identity())
        dataset = Dataset.query.filter_by(id=dataset_id, user_id=user_id).first()
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Delete file from filesystem
        if os.path.exists(dataset.filepath):
            os.remove(dataset.filepath)
        
        # Delete from database
        db.session.delete(dataset)
        db.session.commit()
        
        return jsonify({'message': 'Dataset deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Delete dataset error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# ANALYSIS ROUTES
# =============================================================================

@app.route('/api/analyses', methods=['GET'])
@jwt_required()
def get_analyses():
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        status = request.args.get('status', None)
        
        query = Analysis.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        paginated = query.order_by(Analysis.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        analyses = [analysis.to_dict() for analysis in paginated.items]
        
        return jsonify({
            'analyses': analyses,
            'pagination': {
                'page': page,
                'pages': paginated.pages,
                'per_page': per_page,
                'total': paginated.total
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get analyses error: {str(e)}")
        return jsonify({'error': 'Failed to fetch analyses'}), 500

@app.route('/api/analyses', methods=['POST'])
@jwt_required()
def create_analysis():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        dataset = Dataset.query.filter_by(id=data.get('dataset_id')).first()
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Check if user has access to dataset
        if dataset.user_id != user_id and not dataset.is_public:
            return jsonify({'error': 'Access denied to dataset'}), 403
        
        analysis = Analysis(
            dataset_id=dataset.id,
            user_id=user_id,
            mode=data.get('mode', 'eda'),
            params=data.get('params', {}),
            status='pending'
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # Simulate analysis completion (replace with actual analysis logic)
        analysis.status = 'done'
        analysis.started_at = datetime.utcnow()
        analysis.finished_at = datetime.utcnow()
        analysis.metrics = {
            'rows_processed': dataset.rows,
            'columns_processed': dataset.cols,
            'analysis_type': data.get('mode', 'eda')
        }
        
        db.session.commit()
        
        return jsonify({
            'message': 'Analysis created successfully',
            'analysis': analysis.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create analysis error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create analysis'}), 500

@app.route('/api/analyses/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    try:
        user_id = int(get_jwt_identity())
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify(analysis.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Get analysis error: {str(e)}")
        return jsonify({'error': 'Failed to fetch analysis'}), 500

@app.route('/api/analyses/<int:analysis_id>/viz', methods=['GET'])
@jwt_required()
def get_analysis_viz(analysis_id):
    try:
        user_id = int(get_jwt_identity())
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # FIXED: Convert numpy arrays to Python lists
        viz_data = {
            'charts': [
                {
                    'type': 'histogram',
                    'title': 'Distribution of Values',
                    'data': {
                        'bins': list(range(10)),
                        'counts': [10, 20, 30, 25, 15, 5, 8, 12, 6, 4]
                    }
                },
                {
                    'type': 'scatter',
                    'title': 'Feature Correlation',
                    'data': {
                        'points': [[i, float(i*2 + np.random.randn())] for i in range(50)]  # Convert to float
                    }
                }
            ]
        }
        
        return jsonify(viz_data), 200
        
    except Exception as e:
        logger.error(f"Get viz error: {str(e)}")
        return jsonify({'error': 'Failed to fetch visualization'}), 500

# =============================================================================
# MODEL ROUTES
# =============================================================================

@app.route('/api/models', methods=['GET'])
@jwt_required()
def get_models():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)
        
        # Sample models data (replace with actual model storage)
        sample_models = [
            {
                'id': 1,
                'name': 'Exoplanet Classifier v1',
                'version': '1.0',
                'description': 'Basic exoplanet detection model',
                'model_type': 'classification',
                'algorithm': 'RandomForest',
                'metrics': {'accuracy': 0.85, 'loss': 0.23},
                'is_published': True,
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 2,
                'name': 'Transit Depth Predictor',
                'version': '2.1',
                'description': 'Predicts transit depth from stellar parameters',
                'model_type': 'regression',
                'algorithm': 'XGBoost',
                'metrics': {'accuracy': 0.92, 'loss': 0.15},
                'is_published': True,
                'created_at': datetime.utcnow().isoformat()
            }
        ]
        
        return jsonify({
            'models': sample_models,
            'pagination': {
                'page': page,
                'pages': 1,
                'per_page': per_page,
                'total': len(sample_models)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get models error: {str(e)}")
        return jsonify({'error': 'Failed to fetch models'}), 500

@app.route('/api/models/train', methods=['POST'])
@jwt_required()
def train_model():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # FIXED: Convert numpy int to Python int
        model_data = {
            'id': int(np.random.randint(1000, 9999)),  # Convert to Python int
            'name': data.get('name', 'Untitled Model'),
            'version': data.get('version', '1.0'),
            'description': data.get('description', ''),
            'user_id': user_id,
            'dataset_id': data.get('dataset_id'),
            'status': 'training',
            'created_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'message': 'Model training started',
            'model': model_data
        }), 201
        
    except Exception as e:
        logger.error(f"Train model error: {str(e)}")
        return jsonify({'error': 'Failed to train model'}), 500

# =============================================================================
# LEADERBOARD ROUTES
# =============================================================================

@app.route('/api/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    try:
        metric = request.args.get('metric', 'accuracy')
        scope = request.args.get('scope', 'global')
        limit = min(request.args.get('limit', 100, type=int), 100)
        
        # Sample leaderboard data
        sample_entries = [
            {
                'id': 1,
                'run_id': 101,
                'user_id': 1,
                'dataset_id': 1,
                'metric': metric,
                'value': 0.95,
                'rank': 1,
                'user': {'id': 1, 'name': 'Dr. Sarah Chen', 'role': 'researcher'},
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 2,
                'run_id': 102,
                'user_id': 2,
                'dataset_id': 1,
                'metric': metric,
                'value': 0.92,
                'rank': 2,
                'user': {'id': 2, 'name': 'Alex Rodriguez', 'role': 'researcher'},
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 3,
                'run_id': 103,
                'user_id': 3,
                'dataset_id': 1,
                'metric': metric,
                'value': 0.89,
                'rank': 3,
                'user': {'id': 3, 'name': 'Maria Kowalski', 'role': 'user'},
                'created_at': datetime.utcnow().isoformat()
            }
        ]
        
        return jsonify({'entries': sample_entries}), 200
        
    except Exception as e:
        logger.error(f"Get leaderboard error: {str(e)}")
        return jsonify({'error': 'Failed to fetch leaderboard'}), 500

@app.route('/api/leaderboard/submit', methods=['POST'])
@jwt_required()
def submit_to_leaderboard():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()
        
        # Simulate leaderboard submission
        return jsonify({'message': 'Submission received'}), 201
        
    except Exception as e:
        logger.error(f"Submit error: {str(e)}")
        return jsonify({'error': 'Submission failed'}), 500

# =============================================================================
# HEALTH CHECK
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200

@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'Exoplanet AI Platform API',
        'version': '1.0.0',
        'status': 'running'
    }), 200

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# =============================================================================
# DATASET UPLOAD ROUTES
# =============================================================================

@app.route('/api/datasets/error-report/<filename>')
@jwt_required()
def download_error_report(filename):
    try:
        # Sanitize filename to prevent path traversal
        safe_filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
        
        if not os.path.exists(filepath) or not safe_filename.startswith('error_report_'):
            return jsonify({'error': 'Error report not found'}), 404

        return send_file(
            filepath,
            as_attachment=True,
            download_name='lines_errors.txt',
            mimetype='text/plain'
        )
    except Exception as e:
        logger.error(f"Error report download error: {str(e)}")
        return jsonify({'error': 'Failed to download error report'}), 500




# Add this route after the existing routes
@app.route('/api/graphs/template', methods=['GET'])
@jwt_required()
def get_graph_template():
    """Get graph template data"""
    try:
        # Path to your template.json file
        template_path = os.path.join(app.config.get('ARTIFACT_FOLDER', 'artifacts'), 'template.json')
        
        # If template.json doesn't exist, create it with your provided data
        if not os.path.exists(template_path):
            template_data = {
                "metadata": {
                    "timestamp": "2025-10-04T21:12:00Z",
                    "model_name": "RandomForestClassifier",
                    "framework": "scikit-learn",
                    "model_version": "1.0.0",
                    "train_dataset_size": 1050,
                    "test_dataset_size": 350,
                    "num_features": 42,
                    "num_classes": 3,
                    "target_names": ["Confirmed", "Candidate", "False Positive"]
                },
                "training_info": {
                    "fit_time_sec": 1.215,
                    "predict_time_sec": 0.042,
                    "cross_validation_folds": 5,
                    "cross_val_score_mean": 0.972,
                    "cross_val_score_std": 0.011
                },
                "cross_validation_results": {
                    "folds": [
                        {
                            "fold": 1,
                            "train_size": 840,
                            "val_size": 210,
                            "metrics": {
                                "accuracy": 0.971,
                                "precision": 0.970,
                                "recall": 0.971,
                                "f1": 0.971,
                                "roc_auc": 0.986,
                                "log_loss": 0.129
                            },
                            "fit_time_sec": 0.226,
                            "score_time_sec": 0.018
                        },
                        {
                            "fold": 2,
                            "train_size": 840,
                            "val_size": 210,
                            "metrics": {
                                "accuracy": 0.967,
                                "precision": 0.966,
                                "recall": 0.967,
                                "f1": 0.967,
                                "roc_auc": 0.983,
                                "log_loss": 0.132
                            },
                            "fit_time_sec": 0.242,
                            "score_time_sec": 0.019
                        },
                        {
                            "fold": 3,
                            "train_size": 840,
                            "val_size": 210,
                            "metrics": {
                                "accuracy": 0.975,
                                "precision": 0.975,
                                "recall": 0.975,
                                "f1": 0.975,
                                "roc_auc": 0.987,
                                "log_loss": 0.121
                            },
                            "fit_time_sec": 0.228,
                            "score_time_sec": 0.017
                        },
                        {
                            "fold": 4,
                            "train_size": 840,
                            "val_size": 210,
                            "metrics": {
                                "accuracy": 0.970,
                                "precision": 0.970,
                                "recall": 0.970,
                                "f1": 0.970,
                                "roc_auc": 0.985,
                                "log_loss": 0.128
                            },
                            "fit_time_sec": 0.237,
                            "score_time_sec": 0.020
                        },
                        {
                            "fold": 5,
                            "train_size": 840,
                            "val_size": 210,
                            "metrics": {
                                "accuracy": 0.978,
                                "precision": 0.978,
                                "recall": 0.978,
                                "f1": 0.978,
                                "roc_auc": 0.989,
                                "log_loss": 0.118
                            },
                            "fit_time_sec": 0.233,
                            "score_time_sec": 0.019
                        }
                    ],
                    "summary": {
                        "mean_accuracy": 0.9722,
                        "std_accuracy": 0.0039,
                        "mean_roc_auc": 0.986,
                        "std_roc_auc": 0.002,
                        "mean_fit_time": 0.233,
                        "mean_score_time": 0.019
                    }
                },
                "train_metrics": {
                    "accuracy": 0.999,
                    "precision": 0.999,
                    "recall": 0.999,
                    "f1": 0.999,
                    "roc_auc": 0.999
                },
                "test_metrics": {
                    "accuracy": 0.972,
                    "precision": 0.972,
                    "recall": 0.972,
                    "f1": 0.972,
                    "roc_auc": 0.986
                },
                "confusion_matrix": {
                    "matrix": [
                        [138, 2, 0],
                        [3, 122, 5],
                        [0, 4, 128]
                    ],
                    "labels": ["Confirmed", "Candidate", "False Positive"],
                    "normalized": [
                        [0.985, 0.014, 0.000],
                        [0.022, 0.902, 0.037],
                        [0.000, 0.030, 0.970]
                    ]
                },
                "roc_curve": {
                    "type": "micro",
                    "fpr": [0.0, 0.01, 0.04, 0.1, 0.3, 1.0],
                    "tpr": [0.0, 0.35, 0.67, 0.87, 0.96, 1.0],
                    "auc": 0.986
                },
                "learning_curve": {
                    "train_sizes": [50, 100, 200, 400, 600, 800, 1000],
                    "train_scores_mean": [0.996, 0.995, 0.994, 0.992, 0.991, 0.990, 0.989],
                    "train_scores_std": [0.003, 0.004, 0.003, 0.002, 0.002, 0.002, 0.001],
                    "test_scores_mean": [0.932, 0.944, 0.953, 0.961, 0.967, 0.971, 0.972],
                    "test_scores_std": [0.011, 0.010, 0.009, 0.008, 0.007, 0.006, 0.005]
                },
                "feature_importance": {
                    "top_features": [
                        {"name": "pl_orbper", "importance": 0.23},
                        {"name": "pl_trandep", "importance": 0.20},
                        {"name": "st_teff", "importance": 0.17},
                        {"name": "st_logg", "importance": 0.10},
                        {"name": "pl_rade", "importance": 0.09},
                        {"name": "st_rad", "importance": 0.06},
                        {"name": "pl_insol", "importance": 0.05},
                        {"name": "st_dist", "importance": 0.04},
                        {"name": "pl_eqt", "importance": 0.03},
                        {"name": "st_tmag", "importance": 0.03}
                    ],
                    "method": "Gini importance"
                }
            }
            
            # Ensure artifacts directory exists
            os.makedirs(os.path.dirname(template_path), exist_ok=True)
            
            # Write template data to file
            with open(template_path, 'w') as f:
                json.dump(template_data, f, indent=2)
                
        # Read and return the template data
        with open(template_path, 'r') as f:
            template_data = json.load(f)
            
        return jsonify(convert_numpy_types(template_data)), 200
        
    except Exception as e:
        logger.error(f"Get graph template error: {str(e)}")
        return jsonify({'error': 'Failed to load graph template'}), 500


# FIXED: Upload dataset function with proper type conversion
@app.route('/api/datasets/upload', methods=['POST'])
@jwt_required()
def upload_dataset():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        is_public = request.form.get('is_public', 'false').lower() == 'true'

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.lower().endswith(('.csv', '.json', '.jsonl')):
            return jsonify({'error': 'Only CSV, JSON, and JSONL files are supported'}), 400

        # Secure filename handling
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save file temporarily for validation
        file.save(filepath)

        # Enhanced CSV validation for CSV files
        validation_result = None
        if file.filename.lower().endswith('.csv'):
            validator = EnhancedCSVValidator()
            validation_result = validator.validate_csv_file(filepath, original_filename)
            
            if not validation_result.valid:
                # Create error report file
                error_report = validation_result.detailed_report
                error_filename = f"error_report_{uuid.uuid4()}.txt"
                error_filepath = os.path.join(app.config['UPLOAD_FOLDER'], error_filename)
                
                with open(error_filepath, 'w', encoding='utf-8') as f:
                    f.write(error_report)
                
                # Clean up the original file
                os.remove(filepath)
                
                # FIXED: Convert validation result to Python types
                return jsonify({
                    'error': 'CSV validation failed',
                    'validation': convert_numpy_types({
                        'valid': validation_result.valid,
                        'errors': validation_result.errors[:3],  # First 3 errors
                        'warnings': validation_result.warnings[:5],  # First 5 warnings
                        'summary': validation_result.summary
                    }),
                    'error_report_url': f'/api/datasets/error-report/{error_filename}'
                }), 422

        # Load and process data
        df = None
        try:
            if file.filename.lower().endswith('.csv'):
                df = pd.read_csv(filepath, low_memory=False)
            elif file.filename.lower().endswith('.json'):
                df = pd.read_json(filepath)
            elif file.filename.lower().endswith('.jsonl'):
                df = pd.read_json(filepath, lines=True)
        except Exception as e:
            os.remove(filepath)
            return jsonify({'error': f'Failed to process file: {str(e)}'}), 400

        if df is None or df.empty:
            os.remove(filepath)
            return jsonify({'error': 'File is empty or could not be processed'}), 400

        # Save to database
        user_id = int(get_jwt_identity())
        dataset = Dataset(
            user_id=user_id,
            filename=unique_filename,
            original_filename=original_filename,
            filepath=filepath,
            rows=int(len(df)),  # FIXED: Convert to Python int
            cols=int(len(df.columns)),  # FIXED: Convert to Python int
            size_bytes=int(os.path.getsize(filepath)),  # FIXED: Convert to Python int
            is_public=is_public
        )

        db.session.add(dataset)
        db.session.commit()

        logger.info(f"Dataset uploaded successfully: {original_filename} by user {user_id}")

        # FIXED: Convert all numpy types to Python types in response
        response_data = {
            'message': 'Dataset uploaded successfully',
            'dataset': {
                'id': dataset.id,
                'filename': original_filename,
                'rows': int(len(df)),  # FIXED: Convert to Python int
                'cols': int(len(df.columns)),  # FIXED: Convert to Python int
                'is_public': is_public,
                'size_bytes': int(os.path.getsize(filepath))  # FIXED: Convert to Python int
            }
        }

        if validation_result:
            response_data['validation'] = convert_numpy_types({
                'valid': validation_result.valid,
                'warnings': validation_result.warnings[:5],
                'summary': validation_result.summary
            })

        return jsonify(response_data), 201

    except Exception as e:
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        logger.error(f"Upload error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config.get('ARTIFACT_FOLDER', 'artifacts'), exist_ok=True)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            admin = User(
                email='admin@example.com',
                name='Admin User',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Default admin user created: admin@example.com / admin123")
        
        print("✅ Database initialized successfully")
    
    print("🚀 Starting Exoplanet AI Platform...")
    print("📍 API Health Check: http://localhost:5000/api/health")
    print("📍 Frontend URL: http://localhost:5173")
    print("👤 Admin Login: admin@example.com / admin123")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
