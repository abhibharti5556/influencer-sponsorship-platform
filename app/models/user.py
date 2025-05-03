from flask_login import UserMixin
from app.extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)
    niche = db.Column(db.String(50))
    category = db.Column(db.String(50))
    
    # Additional fields added to the database schema
    _name = db.Column('name', db.String(100))
    _profile_picture = db.Column('profile_picture', db.String(500))
    profile_picture_data = db.Column(db.LargeBinary)  # For storing the actual image data
    bio = db.Column(db.Text)
    company = db.Column(db.String(100))
    website = db.Column(db.String(500))
    instagram = db.Column(db.String(500))
    twitter = db.Column(db.String(500))
    youtube = db.Column(db.String(500))
    tiktok = db.Column(db.String(500))
    followers_count = db.Column(db.Integer)
    is_flagged = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    campaigns = db.relationship("Campaign", back_populates="sponsor")
    ad_requests = db.relationship("AdRequest", back_populates="influencer")

    # Properties with fallbacks to ensure backward compatibility
    @property
    def name(self):
        """Getter for name with fallback to username"""
        return self._name if self._name else self.username
        
    @name.setter
    def name(self, value):
        """Setter for name property"""
        self._name = value
    
    @property
    def profile_picture(self):
        """Returns profile picture URL or data URL from binary data"""
        if self.profile_picture_data:
            import base64
            return f"data:image/jpeg;base64,{base64.b64encode(self.profile_picture_data).decode('utf-8')}"
        elif self._profile_picture:
            return self._profile_picture
        return None
        
    @profile_picture.setter
    def profile_picture(self, value):
        """Setter for profile_picture property"""
        self._profile_picture = value
        
    def set_profile_picture_data(self, file_data):
        """Store the profile picture binary data"""
        if file_data:
            self.profile_picture_data = file_data
            
    def get_followers_count(self):
        """Get the follower count with fallback to calculated value"""
        if self.followers_count is not None:
            return self.followers_count
        return len(self.ad_requests) if self.ad_requests else 0

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user):
    return User.query.get(int(user))
