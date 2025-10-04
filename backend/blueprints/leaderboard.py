from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db, logger
from models import LeaderboardEntry

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """Get leaderboard entries"""
    try:
        metric = request.args.get('metric', 'accuracy')
        limit = request.args.get('limit', 100, type=int)
        
        entries = LeaderboardEntry.query.filter_by(metric=metric)\
            .order_by(LeaderboardEntry.value.desc())\
            .limit(limit)\
            .all()
        
        results = []
        for i, entry in enumerate(entries, 1):
            result = entry.to_dict()
            result['rank'] = i
            results.append(result)
        
        return jsonify({'entries': results}), 200
        
    except Exception as e:
        logger.error(f"Get leaderboard error: {str(e)}")
        return jsonify({'error': 'Failed to fetch leaderboard'}), 500

@leaderboard_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_to_leaderboard():
    """Submit an analysis to the leaderboard"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # TODO: Validate analysis and calculate metrics
        
        return jsonify({'message': 'Submission received'}), 201
        
    except Exception as e:
        logger.error(f"Submit error: {str(e)}")
        return jsonify({'error': 'Submission failed'}), 500