from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
from werkzeug.utils import secure_filename
from extensions import db, logger
from models import Dataset
from datetime import datetime
import pandas as pd

datasets_bp = Blueprint('datasets', __name__)

ALLOWED_EXTENSIONS = {'csv', 'json', 'jsonl'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@datasets_bp.route('', methods=['GET'])
@jwt_required()
def get_datasets():
    """Get user's datasets"""
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Dataset.query.filter_by(user_id=user_id)
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        datasets = [d.to_dict() for d in paginated.items]
        
        return jsonify({
            'datasets': datasets,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get datasets error: {str(e)}")
        return jsonify({'error': 'Failed to fetch datasets'}), 500

@datasets_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_dataset():
    """Upload a new dataset"""
    try:
        user_id = int(get_jwt_identity())  # Convert string to int
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = str(int(datetime.utcnow().timestamp()))
            filename = f"{timestamp}_{filename}"
            
            filepath = os.path.join('uploads', filename)
            file.save(filepath)
            
            # Get file stats
            file_stats = os.stat(filepath)
            size_bytes = file_stats.st_size
            
            # Try to get rows and columns for CSV
            rows = 0
            cols = 0
            if filename.endswith('.csv'):
                try:
                    df = pd.read_csv(filepath)
                    rows = len(df)
                    cols = len(df.columns)
                except:
                    pass
            
            # Create dataset record
            dataset = Dataset(
                filename=filename,
                filepath=filepath,
                size_bytes=size_bytes,
                rows=rows,
                cols=cols,
                user_id=user_id
            )
            
            db.session.add(dataset)
            db.session.commit()
            
            return jsonify({
                'message': 'Dataset uploaded successfully',
                'dataset': dataset.to_dict()
            }), 201
            
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Upload failed'}), 500