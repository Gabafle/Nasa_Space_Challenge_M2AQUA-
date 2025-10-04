from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, logger
from models import Model

models_bp = Blueprint('models', __name__)

@models_bp.route('', methods=['GET'])
@jwt_required()
def get_models():
    """Get available models"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        query = Model.query.filter_by(is_published=True)
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        models = [m.to_dict() for m in paginated.items]
        
        return jsonify({
            'models': models,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get models error: {str(e)}")
        return jsonify({'error': 'Failed to fetch models'}), 500

@models_bp.route('/train', methods=['POST'])
@jwt_required()
def train_model():
    """Train a new model"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        model = Model(
            name=data.get('name'),
            version=data.get('version', '1.0'),
            description=data.get('description'),
            user_id=user_id,
            dataset_id=data.get('dataset_id')
        )
        
        db.session.add(model)
        db.session.commit()
        
        return jsonify({
            'message': 'Model training started',
            'model': model.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Train model error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to train model'}), 500