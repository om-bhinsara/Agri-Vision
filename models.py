"""
Database models for batch processing
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()


class BatchJob(db.Model):
    """Model for batch analysis jobs"""
    __tablename__ = 'batch_jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    total_images = db.Column(db.Integer, default=0)
    completed_images = db.Column(db.Integer, default=0)
    failed_images = db.Column(db.Integer, default=0)
    task_ids = db.Column(db.JSON, default=list)  # List of Celery task IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # Relationships
    results = db.relationship('AnalysisResult', backref='batch_job', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'total_images': self.total_images,
            'completed_images': self.completed_images,
            'failed_images': self.failed_images,
            'progress': self.progress_percentage(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message
        }
    
    def progress_percentage(self):
        if self.total_images == 0:
            return 0
        return int((self.completed_images + self.failed_images) / self.total_images * 100)


class AnalysisResult(db.Model):
    """Model for individual analysis results"""
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_job_id = db.Column(db.String(36), db.ForeignKey('batch_jobs.id'), nullable=False)
    image_name = db.Column(db.String(255), nullable=False)
    image_index = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, complete, error
    
    # Disease results
    disease_class = db.Column(db.String(100), nullable=True)
    disease_confidence = db.Column(db.Float, nullable=True)
    health_score = db.Column(db.Float, nullable=True)
    
    # Growth results
    growth_class = db.Column(db.String(100), nullable=True)
    growth_confidence = db.Column(db.Float, nullable=True)
    
    # Full results as JSON
    results_json = db.Column(db.JSON, nullable=True)
    
    # Error handling
    error_message = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'batch_job_id': self.batch_job_id,
            'image_name': self.image_name,
            'image_index': self.image_index,
            'status': self.status,
            'disease_class': self.disease_class,
            'disease_confidence': self.disease_confidence,
            'health_score': self.health_score,
            'growth_class': self.growth_class,
            'growth_confidence': self.growth_confidence,
            'results': self.results_json,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
