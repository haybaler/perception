from flask import Blueprint, request, jsonify
from functools import wraps
import re

from src.models.client import Client, db

client_bp = Blueprint('client', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_domain(domain):
    """Validate domain format"""
    pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, domain) is not None

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('Authorization')
        if api_key and api_key.startswith('Bearer '):
            api_key = api_key[7:]  # Remove 'Bearer ' prefix
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        client = Client.find_by_api_key(api_key)
        if not client:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Add client to request context
        request.client = client
        return f(*args, **kwargs)
    
    return decorated_function

@client_bp.route('/clients/register', methods=['POST'])
def register_client():
    """Register a new client and generate API key"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        domain = data.get('domain')
        email = data.get('email')
        organization = data.get('organization', '')
        
        # Validate required fields
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Validate formats
        if not validate_domain(domain):
            return jsonify({'error': 'Invalid domain format'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if domain already exists
        existing_client = Client.find_by_domain(domain)
        if existing_client:
            return jsonify({'error': 'Domain already registered'}), 409
        
        # Create new client
        client = Client(
            domain=domain,
            email=email,
            organization=organization
        )
        
        # Generate API key
        api_key = client.generate_api_key()
        
        # Save to database
        db.session.add(client)
        db.session.commit()
        
        return jsonify({
            'client_id': client.id,
            'domain': client.domain,
            'email': client.email,
            'organization': client.organization,
            'api_key': api_key,
            'created_at': client.created_at.isoformat(),
            'message': 'Client registered successfully. Please save your API key securely.'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients/profile', methods=['GET'])
@require_api_key
def get_client_profile():
    """Get client profile information"""
    try:
        return jsonify({
            'client_id': request.client.id,
            'domain': request.client.domain,
            'email': request.client.email,
            'organization': request.client.organization,
            'created_at': request.client.created_at.isoformat(),
            'updated_at': request.client.updated_at.isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients/profile', methods=['PUT'])
@require_api_key
def update_client_profile():
    """Update client profile information"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        # Update allowed fields
        if 'email' in data:
            email = data['email']
            if not validate_email(email):
                return jsonify({'error': 'Invalid email format'}), 400
            request.client.email = email
        
        if 'organization' in data:
            request.client.organization = data['organization']
        
        # Note: Domain cannot be updated as it's the primary identifier
        
        db.session.commit()
        
        return jsonify({
            'client_id': request.client.id,
            'domain': request.client.domain,
            'email': request.client.email,
            'organization': request.client.organization,
            'updated_at': request.client.updated_at.isoformat(),
            'message': 'Profile updated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients/regenerate-key', methods=['POST'])
@require_api_key
def regenerate_api_key():
    """Regenerate API key for the client"""
    try:
        # Generate new API key
        new_api_key = request.client.generate_api_key()
        
        db.session.commit()
        
        return jsonify({
            'client_id': request.client.id,
            'new_api_key': new_api_key,
            'message': 'API key regenerated successfully. Please update your applications with the new key.',
            'warning': 'The old API key is now invalid and will stop working immediately.'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients/usage', methods=['GET'])
@require_api_key
def get_client_usage():
    """Get usage statistics for the client"""
    try:
        from src.models.url_analysis import UrlAnalysis
        from datetime import datetime, timedelta
        
        # Get usage statistics
        total_analyses = UrlAnalysis.query.filter_by(client_id=request.client.id).count()
        
        # Last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_analyses = UrlAnalysis.query.filter(
            UrlAnalysis.client_id == request.client.id,
            UrlAnalysis.created_at > thirty_days_ago
        ).count()
        
        # Completed analyses
        completed_analyses = UrlAnalysis.query.filter(
            UrlAnalysis.client_id == request.client.id,
            UrlAnalysis.status == 'completed'
        ).count()
        
        # Failed analyses
        failed_analyses = UrlAnalysis.query.filter(
            UrlAnalysis.client_id == request.client.id,
            UrlAnalysis.status == 'failed'
        ).count()
        
        return jsonify({
            'client_id': request.client.id,
            'usage_statistics': {
                'total_analyses': total_analyses,
                'analyses_last_30_days': recent_analyses,
                'completed_analyses': completed_analyses,
                'failed_analyses': failed_analyses,
                'success_rate': (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0
            },
            'account_info': {
                'domain': request.client.domain,
                'member_since': request.client.created_at.isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients/delete', methods=['DELETE'])
@require_api_key
def delete_client():
    """Delete client account and all associated data"""
    try:
        # This will cascade delete all analyses and results
        client_id = request.client.id
        domain = request.client.domain
        
        db.session.delete(request.client)
        db.session.commit()
        
        return jsonify({
            'message': f'Client account for domain {domain} has been deleted successfully',
            'deleted_client_id': client_id,
            'warning': 'All analysis data has been permanently removed'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients/validate-key', methods=['POST'])
def validate_api_key():
    """Validate an API key (public endpoint for testing)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        api_key = data.get('api_key')
        if not api_key:
            return jsonify({'error': 'API key is required'}), 400
        
        client = Client.find_by_api_key(api_key)
        
        if client:
            return jsonify({
                'valid': True,
                'client_id': client.id,
                'domain': client.domain,
                'organization': client.organization
            })
        else:
            return jsonify({
                'valid': False,
                'message': 'Invalid API key'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@client_bp.route('/clients/check-domain', methods=['POST'])
def check_domain_availability():
    """Check if a domain is available for registration"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        domain = data.get('domain')
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        if not validate_domain(domain):
            return jsonify({'error': 'Invalid domain format'}), 400
        
        existing_client = Client.find_by_domain(domain)
        
        return jsonify({
            'domain': domain,
            'available': existing_client is None,
            'message': 'Domain is available' if existing_client is None else 'Domain is already registered'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

