from app.extensions import db
from datetime import datetime


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.String(10), nullable=False)  # Store as YYYY-MM-DD string
    end_date = db.Column(db.String(10), nullable=False)    # Store as YYYY-MM-DD string
    duration = db.Column(db.Integer, nullable=True)        # Duration in days
    budget = db.Column(db.Float, nullable=False)
    niche = db.Column(db.String(50), nullable=False)
    platform = db.Column(db.String(50), nullable=True, default="instagram")
    requirements = db.Column(db.Text, nullable=True)
    visibility = db.Column(db.String(20), default="public")
    status = db.Column(db.String(20), default="active")    # active, pending, inactive
    created_at = db.Column(db.String(30), default=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sponsor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    is_flagged = db.Column(db.Boolean, default=False)

    # Relationships
    sponsor = db.relationship("User", back_populates="campaigns")
    ad_requests = db.relationship("AdRequest", back_populates="campaign", cascade="all, delete-orphan")
