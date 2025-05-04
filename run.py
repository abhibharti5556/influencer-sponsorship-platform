from app import create_app, db
from datetime import datetime
import threading
import time
from app.models.campaign import Campaign

app = create_app()

def update_campaign_statuses():
    """
    Background thread that periodically updates campaign statuses based on their dates.
    This ensures campaigns are automatically marked as inactive when their end date passes.
    """
    with app.app_context():
        while True:
            try:
                # Get all active and pending campaigns
                campaigns = Campaign.query.filter(
                    Campaign.status.in_(["active", "pending"])
                ).all()
                
                today = datetime.now().date()
                updated = 0
                
                for campaign in campaigns:
                    try:
                        start_date = datetime.strptime(campaign.start_date, '%Y-%m-%d').date()
                        end_date = datetime.strptime(campaign.end_date, '%Y-%m-%d').date()
                        
                        old_status = campaign.status
                        
                        # Update status based on dates
                        if start_date > today:
                            new_status = "pending"  # Future campaign
                        elif end_date < today:
                            new_status = "inactive"  # Past campaign
                        else:
                            new_status = "active"  # Current campaign
                            
                        if old_status != new_status:
                            campaign.status = new_status
                            updated += 1
                            print(f"Campaign #{campaign.id} status changed from {old_status} to {new_status}")
                    except Exception as e:
                        print(f"Error updating campaign {campaign.id} status: {str(e)}")
                
                if updated > 0:
                    db.session.commit()
                    print(f"Updated status for {updated} campaigns")
            except Exception as e:
                print(f"Error in campaign status update thread: {str(e)}")
                
            # Sleep for 1 hour before checking again
            time.sleep(3600)

if __name__ == "__main__":
    # Start the background thread for campaign status updates
    status_updater = threading.Thread(target=update_campaign_statuses, daemon=True)
    status_updater.start()
    
    app.run(debug=True)
