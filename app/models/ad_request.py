from app.extensions import db
from datetime import datetime


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey("campaign.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    requirements = db.Column(db.Text)
    payment_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")
    applied_by = db.Column(db.String(40))
    applied_for = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    campaign = db.relationship("Campaign", back_populates="ad_requests")
    influencer = db.relationship("User", foreign_keys=[user_id], back_populates="ad_requests")
