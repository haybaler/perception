from datetime import datetime
import uuid
import json

from .user import db

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    analysis_id = db.Column(db.String(36), db.ForeignKey('url_analyses.id'), nullable=False)
    engine = db.Column(db.String(50), nullable=False)  # technical, performance, seo, mobile
    results = db.Column(db.Text)  # JSON data with detailed results
    score = db.Column(db.Integer)  # Overall score for this engine (0-100)
    recommendations = db.Column(db.Text)  # JSON array of recommendations
    execution_time = db.Column(db.Float)  # Time taken to run this engine in seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AnalysisResult {self.engine} for {self.analysis_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'analysis_id': self.analysis_id,
            'engine': self.engine,
            'results': json.loads(self.results) if self.results else {},
            'score': self.score,
            'recommendations': json.loads(self.recommendations) if self.recommendations else [],
            'execution_time': self.execution_time,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def set_results(self, results_data):
        """Set the results data as JSON"""
        self.results = json.dumps(results_data)

    def get_results(self):
        """Get the results data from JSON"""
        return json.loads(self.results) if self.results else {}

    def set_recommendations(self, recommendations_list):
        """Set the recommendations as JSON array"""
        self.recommendations = json.dumps(recommendations_list)

    def get_recommendations(self):
        """Get the recommendations from JSON"""
        return json.loads(self.recommendations) if self.recommendations else []

    def calculate_score(self, metrics):
        """Calculate overall score based on engine-specific metrics"""
        if self.engine == 'performance':
            return self._calculate_performance_score(metrics)
        elif self.engine == 'technical':
            return self._calculate_technical_score(metrics)
        elif self.engine == 'seo':
            return self._calculate_seo_score(metrics)
        elif self.engine == 'mobile':
            return self._calculate_mobile_score(metrics)
        else:
            return 0

    def _calculate_performance_score(self, metrics):
        """Calculate performance score based on Core Web Vitals"""
        score = 100
        
        # LCP scoring (target: <= 2.5s)
        lcp = metrics.get('lcp', 0)
        if lcp > 4.0:
            score -= 40
        elif lcp > 2.5:
            score -= 20
        
        # INP scoring (target: <= 200ms)
        inp = metrics.get('inp', 0)
        if inp > 500:
            score -= 30
        elif inp > 200:
            score -= 15
        
        # CLS scoring (target: <= 0.1)
        cls = metrics.get('cls', 0)
        if cls > 0.25:
            score -= 30
        elif cls > 0.1:
            score -= 15
        
        return max(0, score)

    def _calculate_technical_score(self, metrics):
        """Calculate technical score based on accessibility factors"""
        score = 100
        
        if not metrics.get('http_status_ok', False):
            score -= 50
        if not metrics.get('robots_txt_ok', False):
            score -= 20
        if not metrics.get('sitemap_found', False):
            score -= 15
        if not metrics.get('css_accessible', False):
            score -= 10
        if not metrics.get('js_accessible', False):
            score -= 5
        
        return max(0, score)

    def _calculate_seo_score(self, metrics):
        """Calculate SEO score based on optimization factors"""
        score = 100
        
        if not metrics.get('title_optimized', False):
            score -= 25
        if not metrics.get('meta_description_ok', False):
            score -= 20
        if not metrics.get('headers_structured', False):
            score -= 15
        if not metrics.get('url_optimized', False):
            score -= 15
        if not metrics.get('content_quality_ok', False):
            score -= 25
        
        return max(0, score)

    def _calculate_mobile_score(self, metrics):
        """Calculate mobile score based on mobile-friendliness"""
        score = 100
        
        if not metrics.get('mobile_friendly', False):
            score -= 40
        if not metrics.get('responsive_design', False):
            score -= 30
        if not metrics.get('touch_targets_ok', False):
            score -= 20
        if not metrics.get('viewport_configured', False):
            score -= 10
        
        return max(0, score)

    @staticmethod
    def get_analysis_results(analysis_id):
        """Get all results for a specific analysis"""
        return AnalysisResult.query.filter_by(analysis_id=analysis_id).all()

    @staticmethod
    def get_engine_result(analysis_id, engine):
        """Get result for a specific engine in an analysis"""
        return AnalysisResult.query.filter_by(
            analysis_id=analysis_id, 
            engine=engine
        ).first()

