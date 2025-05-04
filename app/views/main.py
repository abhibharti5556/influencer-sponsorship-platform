from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user
from app.models.campaign import Campaign
from app.extensions import db

main = Blueprint("main", __name__)


@main.route("/")
def home():
    # Update campaign statuses daily when users visit the home page
    try:
        # Only query active and pending campaigns to save resources
        campaigns = Campaign.query.filter(
            Campaign.status.in_(["active", "pending"])
        ).all()
        
        # Track if any statuses were updated
        updated = False
        for campaign in campaigns:
            if campaign.update_status_based_on_date():
                updated = True
        
        # Only commit if changes were made
        if updated:
            db.session.commit()
    except Exception as e:
        # Log the error but don't interrupt user experience
        print(f"Error updating campaign statuses: {str(e)}")
    
    if current_user.is_authenticated and current_user.role == "admin":
        return redirect(
            url_for("admin.dashboard")
        )  # Redirect to admin dashboard if user is admin
    return render_template("index.html", user=current_user)
