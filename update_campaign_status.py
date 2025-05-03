import sys
import os
from datetime import datetime
from app import create_app, db
from app.models.campaign import Campaign

def update_campaign_statuses():
    """
    Update campaign statuses based on current date:
    - If current date is before start_date: status = 'pending'
    - If current date is between start_date and end_date: status = 'active'
    - If current date is after end_date: status = 'inactive'
    """
    print("Starting campaign status update...")
    today = datetime.now().strftime('%Y-%m-%d')
    today_date = datetime.strptime(today, '%Y-%m-%d').date()
    
    # Get all campaigns
    campaigns = Campaign.query.all()
    updated_count = 0
    
    for campaign in campaigns:
        try:
            # Parse dates
            start_date = datetime.strptime(campaign.start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(campaign.end_date, '%Y-%m-%d').date()
            
            # Determine the correct status
            old_status = campaign.status
            new_status = old_status  # Default to not changing
            
            if today_date < start_date:
                new_status = 'pending'
            elif today_date <= end_date:
                new_status = 'active'
            else:
                new_status = 'inactive'
            
            # Update if status has changed
            if new_status != old_status:
                campaign.status = new_status
                updated_count += 1
                print(f"Campaign {campaign.id} ({campaign.name}): {old_status} -> {new_status}")
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Error processing campaign {campaign.id}: {str(e)}")
    
    if updated_count > 0:
        db.session.commit()
        print(f"Updated status for {updated_count} campaigns")
    else:
        print("No campaigns needed status updates")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        update_campaign_statuses() 