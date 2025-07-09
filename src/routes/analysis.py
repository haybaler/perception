from flask import Blueprint, request, jsonify
from functools import wraps
import uuid
import os
from urllib.parse import urlparse

from src.models.client import Client, db
from src.models.url_analysis import UrlAnalysis
from src.models.analysis_result import AnalysisResult
from src.services.analysis_service import AnalysisService

analysis_bp = Blueprint('analysis', __name__)

# Initialize analysis service
analysis_service = AnalysisService(
    pagespeed_api_key=os.getenv('PAGESPEED_API_KEY')
)

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

def validate_url(url):
    """Validate URL format"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_default_client():
    """Get the default client for simplified usage"""
    return Client.find_by_domain('default.local')

@analysis_bp.route('/start', methods=['POST'])
def analyze_url():
    """Submit a URL for analysis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        if not validate_url(url):
            return jsonify({'error': 'Invalid URL format'}), 400
        
        # Get analysis parameters
        engines = data.get('engines', ['technical', 'performance', 'seo', 'mobile'])
        priority = data.get('priority', 'normal')
        use_cache = data.get('use_cache', True)
        
        # Validate engines
        valid_engines = ['technical', 'performance', 'seo', 'mobile']
        engines = [e for e in engines if e in valid_engines]
        
        if not engines:
            return jsonify({'error': 'At least one valid engine must be specified'}), 400
        
        # Use default client
        client = get_default_client()
        if not client:
            return jsonify({'error': 'System configuration error'}), 500
        
        # Check cache if requested
        cached_analysis_id = None
        if use_cache:
            cached_analysis_id = analysis_service.check_cache(
                client.id, url, max_age_hours=24
            )
        
        if cached_analysis_id:
            return jsonify({
                'analysis_id': cached_analysis_id,
                'status': 'completed',
                'cached': True,
                'message': 'Using cached analysis results'
            })
        
        # Create new analysis record
        analysis = UrlAnalysis(
            client_id=client.id,
            url=url,
            priority=priority
        )
        analysis.set_engines_requested(engines)
        
        db.session.add(analysis)
        db.session.commit()
        
        # Start analysis asynchronously (in a real implementation, this would use a task queue)
        try:
            # For now, run synchronously but this should be async in production
            analysis_results = analysis_service.analyze_url(
                analysis.id, url, engines, client.id
            )
            
            return jsonify({
                'analysis_id': analysis.id,
                'status': 'completed',
                'url': url,
                'engines': engines,
                'priority': priority,
                'estimated_completion': 'immediate',
                'message': 'Analysis completed successfully'
            })
            
        except Exception as e:
            analysis.mark_failed(str(e))
            db.session.commit()
            
            return jsonify({
                'analysis_id': analysis.id,
                'status': 'failed',
                'error': str(e)
            }), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analyze/batch', methods=['POST'])
@require_api_key
def analyze_batch():
    """Submit multiple URLs for batch analysis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        urls = data.get('urls', [])
        if not urls or not isinstance(urls, list):
            return jsonify({'error': 'URLs array is required'}), 400
        
        if len(urls) > 50:  # Limit batch size
            return jsonify({'error': 'Maximum 50 URLs per batch'}), 400
        
        # Validate all URLs
        invalid_urls = [url for url in urls if not validate_url(url)]
        if invalid_urls:
            return jsonify({
                'error': 'Invalid URLs found',
                'invalid_urls': invalid_urls
            }), 400
        
        engines = data.get('engines', ['technical', 'performance', 'seo', 'mobile'])
        priority = data.get('priority', 'normal')
        
        # Process each URL
        batch_results = []
        for url in urls:
            try:
                # Create analysis record
                analysis = UrlAnalysis(
                    client_id=request.client.id,
                    url=url,
                    priority=priority
                )
                analysis.set_engines_requested(engines)
                
                db.session.add(analysis)
                db.session.commit()
                
                batch_results.append({
                    'url': url,
                    'analysis_id': analysis.id,
                    'status': 'queued'
                })
                
            except Exception as e:
                batch_results.append({
                    'url': url,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return jsonify({
            'batch_id': str(uuid.uuid4()),
            'total_urls': len(urls),
            'queued': len([r for r in batch_results if r['status'] == 'queued']),
            'failed': len([r for r in batch_results if r['status'] == 'failed']),
            'results': batch_results
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analyze/status/<analysis_id>', methods=['GET'])
@require_api_key
def get_analysis_status(analysis_id):
    """Get the status of a specific analysis"""
    try:
        analysis = UrlAnalysis.query.get(analysis_id)
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Check client ownership
        if analysis.client_id != request.client.id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get analysis summary
        summary = analysis_service.get_analysis_summary(analysis_id)
        
        return jsonify(summary)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/results/<analysis_id>', methods=['GET'])
def get_analysis_results(analysis_id):
    """Get detailed results for a specific analysis"""
    try:
        analysis = UrlAnalysis.query.get(analysis_id)
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Use default client for simplified access
        client = get_default_client()
        if not client:
            return jsonify({'error': 'System configuration error'}), 500
        
        # Check if analysis is completed
        if analysis.status != 'completed':
            return jsonify({
                'error': 'Analysis not completed',
                'status': analysis.status
            }), 400
        
        # Get detailed results
        detailed_results = analysis_service.get_detailed_results(analysis_id)
        
        return jsonify(detailed_results)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analyze/history', methods=['GET'])
@require_api_key
def get_analysis_history():
    """Get analysis history for the authenticated client"""
    try:
        limit = request.args.get('limit', 50, type=int)
        limit = min(limit, 100)  # Cap at 100
        
        history = analysis_service.get_client_history(request.client.id, limit)
        
        return jsonify({
            'client_id': request.client.id,
            'total_results': len(history),
            'analyses': history
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analyze/delete/<analysis_id>', methods=['DELETE'])
@require_api_key
def delete_analysis(analysis_id):
    """Delete a specific analysis"""
    try:
        success = analysis_service.delete_analysis(analysis_id, request.client.id)
        
        if success:
            return jsonify({'message': 'Analysis deleted successfully'})
        else:
            return jsonify({'error': 'Analysis not found or access denied'}), 404
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/engines/status', methods=['GET'])
def get_engines_status():
    """Get status of all analysis engines (public endpoint)"""
    try:
        status = analysis_service.get_engine_status()
        return jsonify(status)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analyze/export/<analysis_id>/<format>', methods=['GET'])
@require_api_key
def export_analysis_results(analysis_id, format):
    """Export analysis results in various formats"""
    try:
        analysis = UrlAnalysis.query.get(analysis_id)
        
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404
        
        # Check client ownership
        if analysis.client_id != request.client.id:
            return jsonify({'error': 'Access denied'}), 403
        
        if format not in ['json', 'csv', 'pdf']:
            return jsonify({'error': 'Unsupported format. Use json, csv, or pdf'}), 400
        
        # Get detailed results
        detailed_results = analysis_service.get_detailed_results(analysis_id)
        
        if format == 'json':
            return jsonify(detailed_results)
        
        elif format == 'csv':
            # Convert to CSV format
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            writer.writerow(['Engine', 'Score', 'Issue', 'Priority', 'Recommendation'])
            
            # Write recommendations
            for rec in detailed_results.get('recommendations', []):
                writer.writerow([
                    rec.get('category', ''),
                    detailed_results['results'].get(rec.get('category', {}), {}).get('score', ''),
                    rec.get('issue', ''),
                    rec.get('priority', ''),
                    rec.get('recommendation', '')
                ])
            
            output.seek(0)
            return output.getvalue(), 200, {
                'Content-Type': 'text/csv',
                'Content-Disposition': f'attachment; filename=analysis_{analysis_id}.csv'
            }
        
        elif format == 'pdf':
            # For PDF export, return a message for now
            return jsonify({
                'message': 'PDF export not yet implemented',
                'alternative': f'/api/analyze/export/{analysis_id}/json'
            })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/analyze/compare', methods=['POST'])
@require_api_key
def compare_analyses():
    """Compare results from multiple analyses"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'JSON data required'}), 400
        
        analysis_ids = data.get('analysis_ids', [])
        if not analysis_ids or len(analysis_ids) < 2:
            return jsonify({'error': 'At least 2 analysis IDs required for comparison'}), 400
        
        if len(analysis_ids) > 5:
            return jsonify({'error': 'Maximum 5 analyses can be compared'}), 400
        
        # Get all analyses and verify ownership
        analyses = []
        for analysis_id in analysis_ids:
            analysis = UrlAnalysis.query.get(analysis_id)
            if not analysis:
                return jsonify({'error': f'Analysis {analysis_id} not found'}), 404
            
            if analysis.client_id != request.client.id:
                return jsonify({'error': f'Access denied for analysis {analysis_id}'}), 403
            
            analyses.append(analysis)
        
        # Build comparison data
        comparison = {
            'analyses': [],
            'score_comparison': {},
            'recommendation_summary': {}
        }
        
        for analysis in analyses:
            summary = analysis_service.get_analysis_summary(analysis.id)
            comparison['analyses'].append(summary)
        
        # Compare scores across engines
        engines = set()
        for analysis_summary in comparison['analyses']:
            engines.update(analysis_summary.get('category_scores', {}).keys())
        
        for engine in engines:
            comparison['score_comparison'][engine] = []
            for analysis_summary in comparison['analyses']:
                score = analysis_summary.get('category_scores', {}).get(engine)
                comparison['score_comparison'][engine].append({
                    'analysis_id': analysis_summary['analysis_id'],
                    'url': analysis_summary['url'],
                    'score': score
                })
        
        return jsonify(comparison)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/test', methods=['GET'])
def test_route():
    """Test route to verify blueprint registration"""
    return jsonify({'message': 'Analysis blueprint is working!'})

