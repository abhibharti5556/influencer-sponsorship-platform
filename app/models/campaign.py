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
    
    def update_status_based_on_date(self):
        """
        Updates the campaign status based on the current date in relation
        to the campaign's start and end dates.
        
        Returns:
            bool: True if the status was changed, False otherwise
        """
        try:
            today = datetime.now().date()
            start_date = datetime.strptime(self.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(self.end_date, '%Y-%m-%d').date()
            
            old_status = self.status
            
            if start_date > today:
                new_status = "pending"  # Future campaign
            elif end_date < today:
                new_status = "inactive"  # Past campaign
            else:
                new_status = "active"  # Current campaign
                
            if old_status != new_status:
                self.status = new_status
                return True
            
            return False
        except Exception:
            return False
