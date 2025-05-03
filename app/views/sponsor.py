from flask import Blueprint, flash, request, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.campaign import Campaign
from app.models.user import User
from app.models.ad_request import AdRequest
from app.extensions import db
from app.forms import CampaignForm, InfluencerSearchForm, AdRequestForm, SponsorProfileForm
from flask_wtf.csrf import generate_csrf
from sqlalchemy import func
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from app import to_datetime

sponsor = Blueprint("sponsor", __name__)


@sponsor.route("/campaigns")
@login_required
def campaigns():
    if current_user.role != "sponsor":
        flash("Access denied. You must be a sponsor to view campaigns.", "danger")
        return redirect(url_for("main.home"))
    
    # Get all campaigns for the current sponsor
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()
    
    # Update status for all campaigns based on current date
    today = datetime.now().date()
    for campaign in campaigns:
        try:
            start_date = datetime.strptime(campaign.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(campaign.end_date, '%Y-%m-%d').date()
            
            if start_date > today:
                campaign.status = "pending"  # Future campaign
            elif end_date < today:
                campaign.status = "inactive"  # Past campaign
            else:
                campaign.status = "active"  # Current campaign
        except Exception as e:
            print(f"Error updating campaign {campaign.id} status: {str(e)}")
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error committing campaign status updates: {str(e)}")
    
    return render_template(
        "sponsor/campaigns.html", 
        campaigns=campaigns, 
        user=current_user,
        now=datetime.now(),
        csrf_token=generate_csrf()
    )


@sponsor.route("/campaign/create", methods=["GET", "POST"])
@login_required
def create_campaign():
    if current_user.role != 'sponsor':
        flash('Access denied: Sponsor account required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = CampaignForm()
    if form.validate_on_submit():
        try:
            # Format dates as strings in YYYY-MM-DD format
            start_date_str = form.start_date.data.strftime('%Y-%m-%d')
            end_date_str = form.end_date.data.strftime('%Y-%m-%d')
            
            # Calculate duration if not provided
            duration = form.duration.data
            if not duration:
                # Calculate duration from start and end dates
                delta = form.end_date.data - form.start_date.data
                duration = delta.days + 1  # Add 1 to include both start and end days
            
            # Determine status based on dates
            status = "active"
            today = datetime.now().date()
            if form.start_date.data > today:
                status = "pending"  # Future campaign
            elif form.end_date.data < today:
                status = "inactive"  # Past campaign
            
            campaign = Campaign(
                title=form.title.data,
                name=form.name.data if form.name.data else form.title.data,  # Use title as name if not provided
                description=form.description.data,
                budget=form.budget.data,
                start_date=start_date_str,
                end_date=end_date_str,
                duration=duration,
                requirements=form.requirements.data,
                sponsor_id=current_user.id,
                status=status,
                platform=form.platform.data,
                niche=form.niche.data,
                visibility=form.visibility.data
            )
            db.session.add(campaign)
            db.session.commit()
            flash('Campaign created successfully!', 'success')
            return redirect(url_for('sponsor.campaigns'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating campaign: {str(e)}', 'danger')
            
    return render_template('sponsor/create_campaign.html', form=form, title="Create Campaign", user=current_user)


@sponsor.route("/campaign/<int:id>/update", methods=["GET", "POST"])
@login_required
def update_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    if campaign.sponsor_id != current_user.id:
        flash("You do not have permission to edit this campaign.", "danger")
        return redirect(url_for("sponsor.campaigns"))

    form = CampaignForm(obj=campaign)
    
    # Handle the date conversion for GET request
    if request.method == 'GET':
        try:
            # Convert string dates to datetime for form
            if hasattr(campaign, 'start_date') and isinstance(campaign.start_date, str):
                form.start_date.data = to_datetime(campaign.start_date)
            if hasattr(campaign, 'end_date') and isinstance(campaign.end_date, str):
                form.end_date.data = to_datetime(campaign.end_date)
        except Exception as e:
            flash(f"Warning: There was an issue with date conversion: {str(e)}", "warning")
    
    if form.validate_on_submit():
        try:
            # Format dates as strings in YYYY-MM-DD format
            if form.start_date.data:
                campaign.start_date = form.start_date.data.strftime('%Y-%m-%d')
            if form.end_date.data:
                campaign.end_date = form.end_date.data.strftime('%Y-%m-%d')
                
            # Update other fields
            campaign.name = form.name.data
            campaign.description = form.description.data
            campaign.budget = form.budget.data
            campaign.niche = form.niche.data
            campaign.visibility = form.visibility.data
            
            # Update status based on dates
            today = datetime.now().date()
            start_date = datetime.strptime(campaign.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(campaign.end_date, '%Y-%m-%d').date()
            
            if start_date > today:
                campaign.status = "pending"  # Future campaign
            elif end_date < today:
                campaign.status = "inactive"  # Past campaign
            else:
                campaign.status = "active"  # Current campaign
            
            db.session.commit()
            flash("Campaign updated successfully!", "success")
            return redirect(url_for("sponsor.campaigns"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating campaign: {str(e)}", "danger")
            
    return render_template(
        "sponsor/update_campaign.html", form=form, campaign=campaign, user=current_user
    )


@sponsor.route("/campaign/<int:id>/delete", methods=["POST"])
@login_required
def delete_campaign(id):
    campaign = Campaign.query.get_or_404(id)
    if campaign.sponsor_id != current_user.id:
        flash("You are not allowed to delete this.", "danger")
        return redirect(url_for("sponsor.campaigns"))

    db.session.delete(campaign)
    db.session.commit()
    flash("Campaign deleted successfully!", "success")
    return redirect(url_for("sponsor.campaigns"))


@sponsor.route("/search_influencers", methods=["GET", "POST"])
@login_required
def search_influencers():
    form = InfluencerSearchForm()

    influencers = []

    if form.validate_on_submit():
        niche = form.niche.data

        influencers = User.query.filter(
            User.role == "influencer", User.niche == niche
        ).all()

    return render_template(
        "sponsor/search_influencers.html",
        form=form,
        influencers=influencers,
        user=current_user,
    )


@sponsor.route(
    "/campaign/<int:campaign_id>/send_ad_request/<int:influencer_id>",
    methods=["GET", "POST"],
)
@login_required
def send_ad_request(campaign_id, influencer_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    influencer = User.query.get_or_404(influencer_id)

    if campaign.sponsor_id != current_user.id:
        flash(
            "You do not have permission to send ad requests for this campaign.",
            "danger",
        )
        return redirect(url_for("sponsor.campaigns"))

    form = AdRequestForm()

    sponsor_id = campaign.sponsor_id

    if form.validate_on_submit():
        ad_request = AdRequest(
            campaign_id=campaign_id,
            user_id=current_user.id,
            requirements=form.requirements.data,
            payment_amount=form.payment_amount.data,
            status="pending",
            applied_by="sponsor",
            applied_for=influencer.id
        )
        db.session.add(ad_request)
        db.session.commit()
        flash("Ad request sent successfully!", "success")
        return redirect(url_for("sponsor.campaigns"))

    return render_template(
        "sponsor/send_ad_request.html",
        form=form,
        campaign=campaign,
        influencer=influencer,
        user=current_user,
    )


@sponsor.route("/select_campaign/<int:influencer_id>", methods=["GET", "POST"])
@login_required
def select_campaign(influencer_id):
    influencer = User.query.get_or_404(influencer_id)
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()

    if request.method == "POST":
        campaign_id = request.form.get("campaign_id")
        if campaign_id:
            return redirect(
                url_for(
                    "sponsor.send_ad_request",
                    campaign_id=campaign_id,
                    influencer_id=influencer_id,
                )
            )
        else:
            flash("Please select a campaign", "warning")

    return render_template(
        "sponsor/select_campaign.html",
        influencer=influencer,
        campaigns=campaigns,
        user=current_user,
        csrf_token=generate_csrf(),
    )


@sponsor.route("/stats")
@login_required
def stats():
    # Get all campaigns for the current sponsor
    campaigns = Campaign.query.filter_by(sponsor_id=current_user.id).all()

    # Get total number of campaigns
    total_campaigns = len(campaigns)

    # Get total budget across all campaigns
    total_budget = sum(campaign.budget for campaign in campaigns)

    # Get total number of ad requests
    total_ad_requests = (
        AdRequest.query.join(Campaign)
        .filter(Campaign.sponsor_id == current_user.id)
        .count()
    )

    # Get ad requests by status
    ad_requests_by_status = (
        db.session.query(AdRequest.status, func.count(AdRequest.id))
        .join(Campaign)
        .filter(Campaign.sponsor_id == current_user.id)
        .group_by(AdRequest.status)
        .all()
    )

    # Get top 5 campaigns by number of ad requests
    top_campaigns = (
        db.session.query(Campaign.name, func.count(AdRequest.id).label("request_count"))
        .join(AdRequest)
        .filter(Campaign.sponsor_id == current_user.id)
        .group_by(Campaign.id)
        .order_by(func.count(AdRequest.id).desc())
        .limit(5)
        .all()
    )

    return render_template(
        "sponsor/stats.html",
        user=current_user,
        total_campaigns=total_campaigns,
        total_budget=total_budget,
        total_ad_requests=total_ad_requests,
        ad_requests_by_status=dict(ad_requests_by_status),
        top_campaigns=top_campaigns,
    )


@sponsor.route("/pending_requests")
@login_required
def view_pending_requests():
    if current_user.role != "sponsor":
        flash("Access restricted. Influencer status required.", "warning")
        return redirect(url_for("main.home"))

    pending_requests = (
        AdRequest.query.filter_by(
            applied_for=current_user.id, status="pending", applied_by="influencer"
        )
        .join(Campaign)
        .all()
    )

    return render_template(
        "sponsor/pending_requests.html",
        requests=pending_requests,
        user=current_user,
        csrf_token=generate_csrf(),
    )


@sponsor.route("/handle_request/<int:request_id>", methods=["POST"])
@login_required
def handle_request(request_id):
    if current_user.role != "sponsor":
        flash("Access restricted. Influencer status required.", "warning")
        return redirect(url_for("main.main"))

    ad_request = AdRequest.query.get_or_404(request_id)

    if ad_request.applied_for != current_user.id:
        flash("You don't have permission to modify this request.", "danger")
        return redirect(url_for("sponsor.view_pending_requests"))

    action = request.form.get("action")

    if action == "accept":
        ad_request.status = "accepted"
        ad_request.response_date = datetime.utcnow()
        flash("Ad request accepted successfully.", "success")
        db.session.commit()
    elif action == "reject":
        # Delete the request instead of just marking it as rejected
        db.session.delete(ad_request)
        db.session.commit()
        flash("Ad request rejected and deleted.", "info")
    else:
        flash("Invalid action specified.", "danger")

    return redirect(url_for("sponsor.view_pending_requests"))


@sponsor.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if current_user.role != "sponsor":
        flash("Access denied. You must be a sponsor to edit this profile.", "danger")
        return redirect(url_for("main.home"))
    
    form = SponsorProfileForm()
    
    # Pre-populate form with user's data
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.company.data = current_user.company
        form.bio.data = current_user.bio
        form.website.data = current_user.website
        form.instagram.data = current_user.instagram
        form.twitter.data = current_user.twitter
    
    if form.validate_on_submit():
        # Update user data in the database
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.company = form.company.data
        current_user.bio = form.bio.data
        current_user.website = form.website.data
        current_user.instagram = form.instagram.data
        current_user.twitter = form.twitter.data
        
        # Handle profile picture upload
        if form.profile_picture.data:
            # Read the uploaded file data
            file_data = form.profile_picture.data.read()
            if file_data:
                # Store the image data directly in the database
                current_user.profile_picture_data = file_data
                # Get secure filename for reference
                filename = secure_filename(form.profile_picture.data.filename)
                current_user.profile_picture = filename
                flash(f"Profile picture '{filename}' uploaded successfully.", "success")
        
        db.session.commit()
        flash("Your profile has been updated successfully.", "success")
        return redirect(url_for("sponsor.edit_profile"))
    
    return render_template("sponsor/edit_profile.html", user=current_user, form=form)


@sponsor.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def edit_campaign(campaign_id):
    if current_user.role != 'sponsor':
        flash('Access denied: Sponsor account required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.sponsor_id != current_user.id:
        flash('Access denied: You can only edit your own campaigns.', 'danger')
        return redirect(url_for('sponsor.campaigns'))
    
    form = CampaignForm(obj=campaign)
    
    # Convert string dates to datetime objects for the form
    if request.method == 'GET':
        try:
            if campaign.start_date:
                form.start_date.data = datetime.strptime(campaign.start_date, '%Y-%m-%d')
            if campaign.end_date:
                form.end_date.data = datetime.strptime(campaign.end_date, '%Y-%m-%d')
            
            # Set duration from campaign
            form.duration.data = campaign.duration
            
            # Set form fields from campaign properties
            form.title.data = campaign.title if hasattr(campaign, 'title') and campaign.title else campaign.name
            form.name.data = campaign.name
            form.platform.data = campaign.platform if hasattr(campaign, 'platform') and campaign.platform else 'instagram'
            form.requirements.data = campaign.requirements if hasattr(campaign, 'requirements') else ''
            form.status.data = campaign.status if hasattr(campaign, 'status') else 'active'
            
        except ValueError as e:
            flash(f'Warning: Error parsing date formats. Please check dates carefully: {str(e)}', 'warning')
    
    if form.validate_on_submit():
        try:
            # Format dates as strings in YYYY-MM-DD format
            start_date_str = form.start_date.data.strftime('%Y-%m-%d')
            end_date_str = form.end_date.data.strftime('%Y-%m-%d')
            
            # Calculate duration if not provided
            duration = form.duration.data
            if not duration:
                # Calculate duration from start and end dates
                delta = form.end_date.data - form.start_date.data
                duration = delta.days + 1  # Add 1 to include both start and end days
            
            # Determine status based on dates
            status = form.status.data
            today = datetime.now().date()
            # Auto-update status based on dates if not manually set
            if not status or status == "active":
                if form.start_date.data > today:
                    status = "pending"  # Future campaign
                elif form.end_date.data < today:
                    status = "inactive"  # Past campaign
                else:
                    status = "active"  # Current campaign
            
            # Update campaign fields
            campaign.title = form.title.data
            campaign.name = form.name.data if form.name.data else form.title.data
            campaign.description = form.description.data
            campaign.budget = form.budget.data
            campaign.start_date = start_date_str
            campaign.end_date = end_date_str
            campaign.duration = duration
            campaign.requirements = form.requirements.data
            campaign.platform = form.platform.data
            campaign.niche = form.niche.data
            campaign.visibility = form.visibility.data
            campaign.status = status
            
            db.session.commit()
            flash('Campaign updated successfully!', 'success')
            return redirect(url_for('sponsor.campaigns'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating campaign: {str(e)}', 'danger')
    
    return render_template('sponsor/edit_campaign.html', form=form, campaign=campaign, title="Edit Campaign", user=current_user)
