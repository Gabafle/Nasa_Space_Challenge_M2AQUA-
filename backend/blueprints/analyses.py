from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, logger
from models import Analysis, Dataset, Status
from datetime import datetime

analyses_bp = Blueprint('analyses', __name__)

@analyses_bp.route('', methods=['GET'])
@jwt_required()
def get_analyses():
    """Get user's analyses"""
    try:
        user_id = get_jwt_identity()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status = request.args.get('status', None)
        
        query = Analysis.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=Status[status])
        
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        
        analyses = [a.to_dict() for a in paginated.items]
        
        return jsonify({
            'analyses': analyses,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get analyses error: {str(e)}")
        return jsonify({'error': 'Failed to fetch analyses'}), 500

@analyses_bp.route('', methods=['POST'])
@jwt_required()
def create_analysis():
    """Create a new analysis"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Verify dataset exists and belongs to user
        dataset = Dataset.query.filter_by(
            id=data.get('dataset_id'),
            user_id=user_id
        ).first()
        
        if not dataset:
            return jsonify({'error': 'Dataset not found'}), 404
        
        # Create analysis
        analysis = Analysis(
            dataset_id=dataset.id,
            user_id=user_id,
            mode=data.get('mode', 'eda'),
            params=data.get('params', {}),
            status=Status.pending
        )
        
        db.session.add(analysis)
        db.session.commit()
        
        # TODO: Trigger actual analysis task here
        # For now, just mark as done after creation
        analysis.status = Status.done
        analysis.started_at = datetime.utcnow()
        analysis.finished_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Analysis created successfully',
            'analysis': analysis.to_dict()
        }), 201
        
    except Exception as e:
        logger.error(f"Create analysis error: {str(e)}")
        db.session.rollback()
        return jsonify({'error': 'Failed to create analysis'}), 500

@analyses_bp.route('/<int:analysis_id>', methods=['GET'])
@jwt_required()
def get_analysis(analysis_id):
    """Get a specific analysis"""
    try:
        user_id = get_jwt_identity()
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        return jsonify(analysis.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Get analysis error: {str(e)}")
        return jsonify({'error': 'Failed to fetch analysis'}), 500

@analyses_bp.route('/<int:analysis_id>/viz', methods=['GET'])
@jwt_required()
def get_analysis_viz(analysis_id):
    """Get visualization data for an analysis"""
    try:
        user_id = get_jwt_identity()
        analysis = Analysis.query.filter_by(id=analysis_id, user_id=user_id).first()
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # TODO: Load actual visualization data
        # For now, return mock data
        viz_data = {
            'charts': [
                {
                    'type': 'histogram',
                    'title': 'Distribution of Values',
                    'data': {
                        'bins': [0, 1, 2, 3, 4, 5],
                        'counts': [10, 20, 30, 25, 15, 5]
                    }
                }
            ]
        }
        
        return jsonify(viz_data), 200
        
    except Exception as e:
        logger.error(f"Get viz error: {str(e)}")
        return jsonify({'error': 'Failed to fetch visualization'}), 500