from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import secrets
import hashlib

from .user import db

class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), nullable=False)
    organization = db.Column(db.String(255), nullable=True)
    api_key_hash = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('UrlAnalysis', backref='client', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Client {self.domain}>'
    
    def generate_api_key(self):
        """Generate a new API key for this client"""
        api_key = secrets.token_urlsafe(32)
        self.api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return api_key
    
    def verify_api_key(self, api_key):
        """Verify an API key against the stored hash"""
        if not self.api_key_hash:
            return False
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return key_hash == self.api_key_hash
    
    @classmethod
    def find_by_domain(cls, domain):
        """Find a client by domain"""
        return cls.query.filter_by(domain=domain).first()
    
    @classmethod
    def find_by_api_key(cls, api_key):
        """Find a client by API key"""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        return cls.query.filter_by(api_key_hash=key_hash, is_active=True).first()
    
    def to_dict(self):
        return {
            'id': self.id,
            'domain': self.domain,
            'email': self.email,
            'organization': self.organization,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_usage_stats(self):
        """Get usage statistics for this client"""
        from .url_analysis import UrlAnalysis
        
        total_analyses = UrlAnalysis.query.filter_by(client_id=self.id).count()
        recent_analyses = UrlAnalysis.query.filter_by(client_id=self.id).filter(
            UrlAnalysis.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        return {
            'total_analyses': total_analyses,
            'recent_analyses': recent_analyses
        }
