from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, logger
from models import Label

labels_bp = Blueprint('labels', __name__)

@labels_bp.route('', methods=['GET'])
@jwt_required()
def get_labels():
    """Get labels"""
    try:
        user_id = get_jwt_identity()
        dataset_id = request.args.get('dataset_id')
        
        query = Label.query.filter_by(user_id=user_id)
        
        if dataset_id:
            query = query.filter_by(dataset_id=dataset_id)
        
        labels = [l.to_dict() for l in query.all()]
        
        return jsonify({'labels': labels}), 200
        
    except Exception as e:
        logger.error(f"Get labels error: {str(e)}")
        return jsonify({'error': 'Failed to fetch labels'}), 500

@labels_bp.route('/batch', methods=['POST'])
@jwt_required()
def create_labels_batch():
    """Create multiple labels"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        dataset_id = data.get('dataset_id')
        items = data.get('items', [])
        
        for item in items:
            label = Label(
                dataset_id=dataset_id,
                user_id=user_id,
                row_id=item.get('row_id'),
                label=item.get('label'),
                confidence=item.get('confidence', 1.0),
                notes=item.get('notes')
            )
            db.session.add(label)
        
        db.session.commit()
        
        return jsonify({'message': f'{len(items)} labels created'}), 201
        
    except Exception as e:
        logger.error(f"Create labels error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create labels'}), 500