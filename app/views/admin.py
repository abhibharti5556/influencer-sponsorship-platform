from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models.user import User
from app.models.campaign import Campaign
from app.models.ad_request import AdRequest
from app.forms import AdminProfileForm, AdminCampaignSearchForm, AdminUserSearchForm
from app.extensions import db
from werkzeug.utils import secure_filename
from sqlalchemy import or_

admin = Blueprint("admin", __name__)


@admin.route("/admin/dashboard")
@login_required
def dashboard():
    if current_user.role != "admin":
        return {"message": "Not authorized"}, 403
    # Fetch statistics
    total_users = User.query.count()
    active_users = User.query.filter(User.is_active != None).count()
    total_campaigns = Campaign.query.count()
    public_campaigns = Campaign.query.filter_by(visibility="public").count()
    private_campaigns = Campaign.query.filter_by(visibility="private").count()
    total_ad_requests = AdRequest.query.count()
    pending_ad_requests = AdRequest.query.filter_by(status="pending").count()
    accepted_ad_requests = AdRequest.query.filter_by(status="accepted").count()
    rejected_ad_requests = AdRequest.query.filter_by(status="rejected").count()

    # Get flagged items count
    flagged_campaigns = Campaign.query.filter_by(is_flagged=True).count()
    flagged_users = User.query.filter_by(is_flagged=True).count()
    
    # Get recent flagged items for display
    recent_flagged_campaigns = Campaign.query.filter_by(is_flagged=True).order_by(Campaign.created_at.desc()).limit(5).all()
    recent_flagged_users = User.query.filter_by(is_flagged=True).order_by(User.id.desc()).limit(5).all()

    stats = {
        "total_users": total_users,
        "active_users": active_users,
        "total_campaigns": total_campaigns,
        "public_campaigns": public_campaigns,
        "private_campaigns": private_campaigns,
        "total_ad_requests": total_ad_requests,
        "pending_ad_requests": pending_ad_requests,
        "accepted_ad_requests": accepted_ad_requests,
        "rejected_ad_requests": rejected_ad_requests,
        "flagged_campaigns": flagged_campaigns,
        "flagged_users": flagged_users,
    }

    return render_template("admin/dashboard.html", stats=stats, user=current_user, 
                          flagged_campaigns=recent_flagged_campaigns, 
                          flagged_users=recent_flagged_users)


@admin.route("/admin/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if current_user.role != "admin":
        flash("Access denied. You must be an admin to edit this profile.", "danger")
        return redirect(url_for("main.home"))
    
    form = AdminProfileForm()
    
    # Pre-populate form with user's data
    if request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
        form.bio.data = current_user.bio
        form.website.data = current_user.website
    
    if form.validate_on_submit():
        # Update user data in the database
        current_user.name = form.name.data
        current_user.email = form.email.data
        current_user.bio = form.bio.data
        current_user.website = form.website.data
        
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
        return redirect(url_for("admin.dashboard"))
    
    return render_template("admin/edit_profile.html", user=current_user, form=form)


@admin.route("/admin/search_campaigns")
@login_required
def admin_search_campaigns():
    if current_user.role != "admin":
        flash("Access denied. You must be an admin to access this page.", "danger")
        return redirect(url_for("main.home"))
    
    form = AdminCampaignSearchForm(request.args, meta={'csrf': False})
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of campaigns per page
    
    # Base query
    query = Campaign.query
    
    # Apply filters if provided
    if form.niche.data:
        query = query.filter_by(niche=form.niche.data)
    
    # Filter by flagged status if requested
    is_flagged = request.args.get('is_flagged')
    if is_flagged == 'true':
        query = query.filter_by(is_flagged=True)
    
    # Order by creation date (newest first)
    query = query.order_by(Campaign.created_at.desc())
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    campaigns = pagination.items
    
    # Check campaign model fields and add platform if missing
    campaign_list = []
    for campaign in campaigns:
        # For older campaign models that might not have the platform attribute
        if not hasattr(campaign, 'platform'):
            campaign.platform = 'Unknown'
        if not hasattr(campaign, 'title'):
            campaign.title = campaign.name if hasattr(campaign, 'name') else 'Untitled'
        if not hasattr(campaign, 'requirements'):
            campaign.requirements = ''
        if not hasattr(campaign, 'status'):
            campaign.status = campaign.visibility if hasattr(campaign, 'visibility') else 'unknown'
        campaign_list.append(campaign)
    
    return render_template("admin/search_campaigns.html", form=form, campaigns=campaign_list, pagination=pagination, user=current_user)


@admin.route("/admin/search_users")
@login_required
def search_users():
    if current_user.role != "admin":
        flash("Access denied. You must be an admin to access this page.", "danger")
        return redirect(url_for("main.home"))
    
    form = AdminUserSearchForm(request.args, meta={'csrf': False})
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Number of users per page
    
    # Base query
    query = User.query
    
    # Apply filter if provided
    if form.role.data:
        query = query.filter_by(role=form.role.data)
    
    # Filter by flagged status if requested
    is_flagged = request.args.get('is_flagged')
    if is_flagged == 'true':
        query = query.filter_by(is_flagged=True)
    
    # Order by username
    query = query.order_by(User.username)
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return render_template("admin/search_users.html", form=form, users=users, pagination=pagination, user=current_user)


@admin.route("/admin/view_campaign/<int:campaign_id>")
@login_required
def view_campaign(campaign_id):
    if current_user.role != "admin":
        flash("Access denied. You must be an admin to access this page.", "danger")
        return redirect(url_for("main.home"))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    sponsor_campaigns = Campaign.query.filter_by(sponsor_id=campaign.sponsor_id).all()
    
    return render_template("admin/view_campaign.html", campaign=campaign, ad_requests=ad_requests, sponsor_campaigns=sponsor_campaigns, user=current_user)


@admin.route("/admin/flag_campaign/<int:campaign_id>")
@login_required
def flag_campaign(campaign_id):
    if current_user.role != "admin":
        flash("Access denied. You must be an admin to perform this action.", "danger")
        return redirect(url_for("main.home"))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.is_flagged = True
    db.session.commit()
    
    flash(f"Campaign '{campaign.name}' has been flagged.", "success")
    
    # Redirect back to the previous page
    next_page = request.args.get('next') or request.referrer or url_for('admin.search_campaigns')
    return redirect(next_page)


@admin.route("/admin/unflag_campaign/<int:campaign_id>")
@login_required
def unflag_campaign(campaign_id):
    if current_user.role != "admin":
        flash("Access denied. You must be an admin to perform this action.", "danger")
        return redirect(url_for("main.home"))
    
    campaign = Campaign.query.get_or_404(campaign_id)
    campaign.is_flagged = False
    db.session.commit()
    
    flash(f"Campaign '{campaign.name}' has been unflagged.", "success")
    
    # Redirect back to the previous page
    next_page = request.args.get('next') or request.referrer or url_for('admin.search_campaigns')
    return redirect(next_page)


@admin.route('/view_campaigns')
@login_required
def view_campaigns():
    if current_user.role != 'admin':
        flash('Access denied: Admin account required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Get all campaigns and the details of their sponsors
        campaigns = db.session.query(
            Campaign, User
        ).join(
            User, Campaign.sponsor_id == User.id
        ).all()
        
        # Format the campaigns data for the template
        campaign_data = []
        for campaign, sponsor in campaigns:
            # Make a dictionary with campaign and sponsor info
            campaign_dict = {
                'id': campaign.id,
                'title': campaign.title if hasattr(campaign, 'title') else (campaign.name if hasattr(campaign, 'name') else 'Untitled'),
                'description': campaign.description,
                'budget': campaign.budget,
                'start_date': campaign.start_date,
                'end_date': campaign.end_date,
                'status': campaign.status if hasattr(campaign, 'status') else (campaign.visibility if hasattr(campaign, 'visibility') else 'unknown'),
                'sponsor_name': f"{sponsor.first_name} {sponsor.last_name}" if hasattr(sponsor, 'first_name') else sponsor.name,
                'sponsor_id': sponsor.id,
                'platform': campaign.platform if hasattr(campaign, 'platform') else 'Unknown',
                'requirements': campaign.requirements if hasattr(campaign, 'requirements') else '',
                'is_flagged': campaign.is_flagged if hasattr(campaign, 'is_flagged') else False
            }
            campaign_data.append(campaign_dict)
        
        return render_template('admin/view_campaigns.html', campaigns=campaign_data, user=current_user)
    except Exception as e:
        flash(f'Error loading campaigns: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin.route('/toggle_campaign_status/<int:campaign_id>', methods=['GET'])
@login_required
def toggle_campaign_status(campaign_id):
    if current_user.role != 'admin':
        flash('Access denied: Admin account required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Find the campaign
        campaign = Campaign.query.get_or_404(campaign_id)
        
        # Toggle the status
        if campaign.status == 'active':
            campaign.status = 'inactive'
            message = f"Campaign '{campaign.title}' has been deactivated."
        else:
            campaign.status = 'active'
            message = f"Campaign '{campaign.title}' has been activated."
        
        db.session.commit()
        flash(message, 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error toggling campaign status: {str(e)}', 'danger')
    
    # Redirect back to the campaigns page
    return redirect(url_for('admin.view_campaigns'))


@admin.route('/admin/analytics')
@login_required
def analytics():
    if current_user.role != 'admin':
        flash('Access denied: Admin account required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # User statistics
        total_users = User.query.count()
        influencer_count = User.query.filter_by(role='influencer').count()
        sponsor_count = User.query.filter_by(role='sponsor').count()
        admin_count = User.query.filter_by(role='admin').count()
        flagged_users = User.query.filter_by(is_flagged=True).count()
        
        # Campaign statistics
        total_campaigns = Campaign.query.count()
        active_campaigns = Campaign.query.filter_by(status='active').count()
        pending_campaigns = Campaign.query.filter_by(status='pending').count()
        inactive_campaigns = Campaign.query.filter_by(status='inactive').count()
        flagged_campaigns = Campaign.query.filter_by(is_flagged=True).count()
        
        # Ad request statistics
        total_ad_requests = AdRequest.query.count()
        pending_ad_requests = AdRequest.query.filter_by(status='pending').count()
        accepted_ad_requests = AdRequest.query.filter_by(status='accepted').count()
        rejected_ad_requests = AdRequest.query.filter_by(status='rejected').count()
        
        # Platform distribution
        platform_counts = db.session.query(
            Campaign.platform, db.func.count(Campaign.id)
        ).group_by(Campaign.platform).all()
        
        platform_labels = [platform[0] for platform in platform_counts]
        platform_data = [platform[1] for platform in platform_counts]
        
        # Budget ranges distribution
        # Create budget ranges
        budget_ranges = [
            (0, 500),
            (500, 1000),
            (1000, 5000),
            (5000, 10000),
            (10000, float('inf'))
        ]
        
        budget_data = []
        for low, high in budget_ranges:
            if high == float('inf'):
                count = Campaign.query.filter(Campaign.budget > low).count()
            else:
                count = Campaign.query.filter(Campaign.budget.between(low, high)).count()
            budget_data.append(count)
        
        stats = {
            'total_users': total_users,
            'influencer_count': influencer_count,
            'sponsor_count': sponsor_count,
            'admin_count': admin_count,
            'flagged_users': flagged_users,
            'total_campaigns': total_campaigns,
            'active_campaigns': active_campaigns,
            'pending_campaigns': pending_campaigns,
            'inactive_campaigns': inactive_campaigns,
            'flagged_campaigns': flagged_campaigns,
            'total_ad_requests': total_ad_requests,
            'pending_ad_requests': pending_ad_requests,
            'accepted_ad_requests': accepted_ad_requests,
            'rejected_ad_requests': rejected_ad_requests
        }
        
        return render_template('admin/analytics.html', 
                               stats=stats, 
                               platform_labels=platform_labels, 
                               platform_data=platform_data,
                               budget_data=budget_data,
                               user=current_user)
    except Exception as e:
        flash(f'Error loading analytics data: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin.route('/admin/export_users_data')
@login_required
def export_users_data():
    if current_user.role != 'admin':
        flash('Access denied: Admin account required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        import csv
        from io import StringIO
        from datetime import datetime
        from flask import make_response
        
        # Query all users
        users = User.query.all()
        
        # Create CSV file
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'Username', 'Email', 'Role', 'First Name', 'Last Name', 'Registered', 'Active', 'Flagged'])
        
        # Write data rows
        for user in users:
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.role,
                getattr(user, 'first_name', '') if hasattr(user, 'first_name') else '',
                getattr(user, 'last_name', '') if hasattr(user, 'last_name') else '',
                user.created_at if hasattr(user, 'created_at') else 'N/A',
                'Yes' if getattr(user, 'is_active', True) else 'No',
                'Yes' if getattr(user, 'is_flagged', False) else 'No'
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response.headers["Content-type"] = "text/csv"
        
        return response
    except Exception as e:
        flash(f'Error exporting users data: {str(e)}', 'danger')
        return redirect(url_for('admin.analytics'))


@admin.route('/admin/export_campaigns_data')
@login_required
def export_campaigns_data():
    if current_user.role != 'admin':
        flash('Access denied: Admin account required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        import csv
        from io import StringIO
        from datetime import datetime
        from flask import make_response
        
        # Query all campaigns with sponsor information
        campaigns = db.session.query(
            Campaign, User
        ).join(
            User, Campaign.sponsor_id == User.id
        ).all()
        
        # Create CSV file
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'ID', 'Title', 'Description', 'Budget', 'Start Date', 'End Date', 
            'Status', 'Platform', 'Created At', 'Sponsor ID', 'Sponsor Name', 
            'Flagged'
        ])
        
        # Write data rows
        for campaign, sponsor in campaigns:
            title = getattr(campaign, 'title', getattr(campaign, 'name', 'Untitled'))
            writer.writerow([
                campaign.id,
                title,
                getattr(campaign, 'description', ''),
                getattr(campaign, 'budget', 0),
                getattr(campaign, 'start_date', ''),
                getattr(campaign, 'end_date', ''),
                getattr(campaign, 'status', getattr(campaign, 'visibility', 'unknown')),
                getattr(campaign, 'platform', 'Unknown'),
                getattr(campaign, 'created_at', 'N/A'),
                sponsor.id,
                getattr(sponsor, 'name', sponsor.username),
                'Yes' if getattr(campaign, 'is_flagged', False) else 'No'
            ])
        
        # Create response
        response = make_response(output.getvalue())
        response.headers["Content-Disposition"] = f"attachment; filename=campaigns_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        response.headers["Content-type"] = "text/csv"
        
        return response
    except Exception as e:
        flash(f'Error exporting campaigns data: {str(e)}', 'danger')
        return redirect(url_for('admin.analytics'))


@admin.route('/search_campaigns')
@login_required
def search_campaigns():
    if current_user.role != 'admin':
        flash('Access denied: Admin account required.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    try:
        # Get search parameters from request
        query = request.args.get('query', '')
        platform = request.args.get('platform', '')
        status = request.args.get('status', '')
        
        # Build base query
        campaign_query = Campaign.query
        
        # Apply filters if provided
        if query:
            campaign_query = campaign_query.filter(
                or_(
                    Campaign.title.ilike(f'%{query}%') if hasattr(Campaign, 'title') else Campaign.name.ilike(f'%{query}%'),
                    Campaign.description.ilike(f'%{query}%')
                )
            )
        
        if platform and hasattr(Campaign, 'platform'):
            campaign_query = campaign_query.filter(Campaign.platform == platform)
            
        if status:
            if hasattr(Campaign, 'status'):
                campaign_query = campaign_query.filter(Campaign.status == status)
            elif hasattr(Campaign, 'visibility'):
                # Map status to visibility for older models
                visibility_map = {
                    'active': 'public',
                    'inactive': 'private',
                    'pending': 'pending'
                }
                if status in visibility_map:
                    campaign_query = campaign_query.filter(Campaign.visibility == visibility_map[status])
        
        # Execute query
        campaigns = campaign_query.all()
        
        # Process campaigns to ensure all necessary attributes
        processed_campaigns = []
        for campaign in campaigns:
            # For older campaign models that might not have the platform attribute
            if not hasattr(campaign, 'platform'):
                campaign.platform = 'Unknown'
            if not hasattr(campaign, 'title'):
                campaign.title = campaign.name if hasattr(campaign, 'name') else 'Untitled'
            if not hasattr(campaign, 'requirements'):
                campaign.requirements = ''
            if not hasattr(campaign, 'status'):
                campaign.status = campaign.visibility if hasattr(campaign, 'visibility') else 'unknown'
            processed_campaigns.append(campaign)
        
        # Get unique platforms for filter dropdown
        try:
            if hasattr(Campaign, 'platform'):
                platforms = db.session.query(Campaign.platform).distinct().all()
                platforms = [p[0] for p in platforms if p[0]]
            else:
                platforms = []
        except:
            platforms = []
        
        return render_template(
            'admin/search_campaigns.html',
            campaigns=processed_campaigns,
            query=query,
            platform=platform,
            status=status,
            platforms=platforms,
            user=current_user
        )
    except Exception as e:
        flash(f'Error searching campaigns: {str(e)}', 'danger')
        return redirect(url_for('admin.dashboard'))


@admin.route("/admin/flag_user/<int:user_id>", methods=["POST"])
@login_required
def flag_user(user_id):
    if current_user.role != "admin":
        return {"message": "Not authorized"}, 403
    
    user_to_flag = User.query.get_or_404(user_id)
    
    if user_to_flag.role == 'admin':
        return {"message": "Admin users cannot be flagged"}, 400
    else:
        user_to_flag.is_flagged = True
        db.session.commit()
        return {"message": "User flagged successfully", "is_flagged": True}


@admin.route("/admin/unflag_user/<int:user_id>", methods=["POST"])
@login_required
def unflag_user(user_id):
    if current_user.role != "admin":
        return {"message": "Not authorized"}, 403
    
    user_to_unflag = User.query.get_or_404(user_id)
    user_to_unflag.is_flagged = False
    db.session.commit()
    return {"message": "User unflagged successfully", "is_flagged": False}


@admin.route("/admin/view_user/<int:user_id>")
@login_required
def view_user_profile(user_id):
    if current_user.role != "admin":
        flash("Access denied. You must be an admin to access this page.", "danger")
        return redirect(url_for("main.home"))
    
    user = User.query.get_or_404(user_id)
    
    # Get user's campaigns if they are a sponsor
    campaigns = []
    if user.role == "sponsor":
        campaigns = Campaign.query.filter_by(sponsor_id=user.id).all()
    
    # Get user's ad requests if they are an influencer
    ad_requests = []
    if user.role == "influencer":
        ad_requests = AdRequest.query.filter_by(user_id=user.id).all()
    
    return render_template(
        "admin/view_user.html", 
        target_user=user, 
        campaigns=campaigns, 
        ad_requests=ad_requests, 
        user=current_user
    )


@admin.route("/admin/settings", methods=["GET", "POST"])
@login_required
def settings():
    if current_user.role != "admin":
        flash("Access denied. You must be an admin to access this page.", "danger")
        return redirect(url_for("main.home"))
    
    # If this is a POST request, we would process the form data here
    if request.method == "POST":
        # In a real application, you would save the settings to the database
        # For demo purposes, we'll just redirect back to the same page
        flash("Settings updated successfully!", "success")
        return redirect(url_for("admin.settings"))
    
    return render_template("admin/settings.html", user=current_user)
