from datetime import datetime
import uuid
import json

from .user import db

class UrlAnalysis(db.Model):
    __tablename__ = 'url_analyses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    client_id = db.Column(db.String(36), db.ForeignKey('clients.id'), nullable=False)
    url = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending')  # pending, running, completed, failed
    engines_requested = db.Column(db.Text)  # JSON array of requested engines
    priority = db.Column(db.String(20), default='normal')  # low, normal, high
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to analysis results
    results = db.relationship('AnalysisResult', backref='analysis', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<UrlAnalysis {self.url}>'

    def to_dict(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'url': self.url,
            'status': self.status,
            'engines_requested': json.loads(self.engines_requested) if self.engines_requested else [],
            'priority': self.priority,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'results_count': len(self.results) if self.results else 0
        }

    def set_engines_requested(self, engines):
        """Set the list of engines requested for analysis"""
        self.engines_requested = json.dumps(engines)

    def get_engines_requested(self):
        """Get the list of engines requested for analysis"""
        return json.loads(self.engines_requested) if self.engines_requested else []

    def mark_completed(self):
        """Mark the analysis as completed"""
        self.status = 'completed'
        self.completed_at = datetime.utcnow()

    def mark_failed(self, error_message):
        """Mark the analysis as failed with error message"""
        self.status = 'failed'
        self.completed_at = datetime.utcnow()
        self.error_message = error_message

    def mark_running(self):
        """Mark the analysis as running"""
        self.status = 'running'

    @staticmethod
    def find_by_client_and_url(client_id, url):
        """Find recent analysis for the same client and URL"""
        return UrlAnalysis.query.filter_by(
            client_id=client_id, 
            url=url
        ).order_by(UrlAnalysis.created_at.desc()).first()

    @staticmethod
    def get_client_analyses(client_id, limit=50):
        """Get recent analyses for a client"""
        return UrlAnalysis.query.filter_by(
            client_id=client_id
        ).order_by(UrlAnalysis.created_at.desc()).limit(limit).all()

