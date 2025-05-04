from flask import Blueprint, flash, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models.campaign import Campaign
from app.models.ad_request import AdRequest
from app.models.user import User
from app.forms import CampaignSearchForm, InfluencerProfileForm
from app.extensions import db
from sqlalchemy import func
from datetime import datetime
from flask_wtf.csrf import generate_csrf
import os
from werkzeug.utils import secure_filename

influencer = Blueprint("influencer", __name__)


@influencer.route("/")
def home():
    return redirect(url_for("influencer.profile"))


@influencer.route("/search_campaigns", methods=["GET", "POST"])
@login_required
def search_campaigns():
    if current_user.role != "influencer":
        flash("Access denied. You must be an influencer to search campaigns.", "danger")
        return redirect(url_for("main.home"))

    form = CampaignSearchForm()
    campaigns = []

    if form.validate_on_submit():
        niche = form.niche.data

        campaigns = Campaign.query.filter(
            Campaign.visibility == "public", Campaign.niche == niche
        ).all()

    return render_template(
        "influencer/search_campaigns.html",
        form=form,
        campaigns=campaigns,
        user=current_user,
    )


@influencer.route("/apply_campaign/<int:campaign_id>", methods=["GET", "POST"])
@login_required
def apply_campaign(campaign_id):
    if current_user.role != "influencer":
        flash(
            "Access denied. You must be an influencer to apply for campaigns.", "danger"
        )
        return redirect(url_for("main.home"))

    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.visibility != "public":
        flash("This campaign is not public.", "danger")
        return redirect(url_for("influencer.search_campaigns"))

    # Check if the influencer has already applied
    existing_request = AdRequest.query.filter_by(
        campaign_id=campaign_id, user_id=current_user.id
    ).first()

    if existing_request:
        flash("You have already applied for this campaign.", "info")
        return redirect(url_for("influencer.search_campaigns"))

    # Create a new ad request
    ad_request = AdRequest(
        campaign_id=campaign_id,
        user_id=current_user.id,
        applied_for=campaign.sponsor_id,
        payment_amount=campaign.budget,
        status="pending",
        applied_by="influencer",
    )
    db.session.add(ad_request)
    db.session.commit()

    flash("Your application for the campaign has been submitted.", "success")
    return redirect(url_for("influencer.search_campaigns"))


@influencer.route("/profile")
@login_required
def view_profile():
    if current_user.role != "influencer":
        flash(
            "Access denied. You must be an influencer to view this profile.", "danger"
        )
        return redirect(url_for("main.home"))

    ad_requests = AdRequest.query.filter_by(user_id=current_user.id, status="accepted")

    active_campaigns = []
    for ad_request in ad_requests:
        campaign = Campaign.query.get(ad_request.campaign_id)
        active_campaigns.append(campaign)

    user = {
        "username": current_user.username,
        "niche": current_user.niche if hasattr(current_user, 'niche') else '',
        "followers": current_user.followers_count if hasattr(current_user, 'followers_count') else 0,
        "category": current_user.category if hasattr(current_user, 'category') else '',
    }

    return render_template(
        "influencer/profile.html",
        user_info=user,
        user=current_user,
        active_campaigns=active_campaigns,
    )


@influencer.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if current_user.role != "influencer":
        flash(
            "Access denied. You must be an influencer to edit this profile.", "danger"
        )
        return redirect(url_for("main.home"))

    form = InfluencerProfileForm(obj=current_user)

    user = {
        "username": current_user.username,
        "niche": current_user.niche if hasattr(current_user, 'niche') else '',
        "followers": current_user.followers_count if hasattr(current_user, 'followers_count') else 0,
        "category": current_user.category if hasattr(current_user, 'category') else '',
    }

    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.category = form.category.data
        current_user.niche = form.niche.data
        current_user.bio = form.bio.data
        current_user.instagram = form.instagram.data
        current_user.twitter = form.twitter.data
        current_user.youtube = form.youtube.data
        current_user.tiktok = form.tiktok.data
        current_user.website = form.website.data
        
        if form.followers_count.data:
            current_user.followers_count = form.followers_count.data
        
        # Handle profile picture upload
        if form.profile_picture.data:
            try:
                # Check if it's a FileStorage object (which has a 'read' method)
                if hasattr(form.profile_picture.data, 'read') and callable(form.profile_picture.data.read):
                    # It's a file upload
                    file_data = form.profile_picture.data.read()
                    if file_data:
                        # Store the image data directly in the database
                        current_user.profile_picture_data = file_data
                        # Get secure filename for reference
                        filename = secure_filename(form.profile_picture.data.filename)
                        current_user.profile_picture = filename
                        flash(f"Profile picture '{filename}' uploaded successfully.", "success")
                elif isinstance(form.profile_picture.data, str):
                    # If it's a string, it's already been processed or it's a path
                    # Just log and continue without trying to read it
                    flash("Profile picture information updated.", "info")
                else:
                    # Unknown type - log it for debugging
                    flash(f"Profile picture data of unexpected type: {type(form.profile_picture.data)}", "warning")
            except Exception as e:
                # Log the error but continue with the profile update
                flash(f"Could not process profile picture: {str(e)}. Other profile changes were saved.", "warning")

        db.session.commit()
        flash("Your profile has been updated.", "success")
        return redirect(url_for("influencer.view_profile"))

    return render_template(
        "influencer/edit_profile.html", form=form, user_info=user, user=current_user
    )


@influencer.route("/profile/<int:user_id>")
def public_profile(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != "influencer":
        flash("This user is not an influencer.", "danger")
        return redirect(url_for("main.home"))

    return render_template("influencer/public_profile.html", influencer=user)


@influencer.route("/stats")
@login_required
def stats():
    if current_user.role != "influencer":
        flash("Access denied. You must be an influencer to view these stats.", "danger")
        return redirect(url_for("main.home"))

    # Force a refresh of the session to ensure we have the latest data
    db.session.expire_all()
    
    # Total number of ad requests
    total_requests = AdRequest.query.filter_by(user_id=current_user.id).count()

    # Ad requests by status
    requests_by_status = (
        db.session.query(AdRequest.status, func.count(AdRequest.id))
        .filter_by(user_id=current_user.id)
        .group_by(AdRequest.status)
        .all()
    )

    # Top 5 campaigns by payment amount
    top_campaigns = (
        db.session.query(Campaign.name, AdRequest.payment_amount)
        .join(AdRequest)
        .filter(AdRequest.user_id == current_user.id, AdRequest.status == "accepted")
        .order_by(AdRequest.payment_amount.desc())
        .limit(5)
        .all()
    )

    # Total earnings
    total_earnings = (
        db.session.query(func.sum(AdRequest.payment_amount))
        .filter_by(user_id=current_user.id, status="accepted")
        .scalar()
        or 0
    )

    # Average payment per accepted request
    avg_payment = (
        db.session.query(func.avg(AdRequest.payment_amount))
        .filter_by(user_id=current_user.id, status="accepted")
        .scalar()
        or 0
    )

    # Number of unique sponsors worked with
    unique_sponsors = (
        db.session.query(func.count(func.distinct(Campaign.sponsor_id)))
        .join(AdRequest)
        .filter(AdRequest.user_id == current_user.id, AdRequest.status == "accepted")
        .scalar()
        or 0
    )

    return render_template(
        "influencer/stats.html",
        user=current_user,
        total_requests=total_requests,
        requests_by_status=dict(requests_by_status),
        top_campaigns=top_campaigns,
        total_earnings=total_earnings,
        avg_payment=avg_payment,
        unique_sponsors=unique_sponsors,
    )


@influencer.route("/pending_requests")
@login_required
def view_pending_requests():
    if current_user.role != "influencer":
        flash("Access restricted. Influencer status required.", "warning")
        return redirect(url_for("main.home"))

    # Force a refresh of the session to ensure we have the latest data
    db.session.expire_all()
    
    # Get all pending requests for this influencer
    pending_requests = (
        AdRequest.query.filter_by(
            applied_for=current_user.id, status="pending", applied_by="sponsor"
        )
        .outerjoin(Campaign)  # Use outerjoin to include requests even if campaign is missing
        .all()
    )
    
    # Filter out any requests with missing campaigns to avoid errors
    valid_requests = []
    for req in pending_requests:
        # Make sure the campaign exists
        if hasattr(req, 'campaign') and req.campaign is not None:
            valid_requests.append(req)
        else:
            # Log invalid request
            print(f"Warning: Found pending request #{req.id} without a valid campaign")
    
    return render_template(
        "influencer/pending_requests.html",
        requests=valid_requests,
        user=current_user,
        csrf_token=generate_csrf(),
    )


@influencer.route("/handle_request/<int:request_id>", methods=["POST"])
@login_required
def handle_request(request_id):
    if current_user.role != "influencer":
        flash("Access restricted. Influencer status required.", "warning")
        return redirect(url_for("main.home"))

    ad_request = AdRequest.query.get_or_404(request_id)

    if ad_request.applied_for != current_user.id:
        flash("You don't have permission to modify this request.", "danger")
        return redirect(url_for("influencer.view_pending_requests"))

    action = request.form.get("action")

    if action == "accept":
        ad_request.status = "accepted"
        ad_request.response_date = datetime.utcnow()
        # Also set the user_id to ensure analytics work correctly
        ad_request.user_id = current_user.id
        db.session.commit()
        flash("Ad request accepted successfully.", "success")
    elif action == "reject":
        ad_request.status = "rejected"
        ad_request.response_date = datetime.utcnow()
        db.session.commit()
        flash("Ad request rejected.", "info")
    else:
        flash("Invalid action specified.", "danger")

    return redirect(url_for("influencer.view_pending_requests"))
