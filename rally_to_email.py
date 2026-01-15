
import requests
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
RALLY_API_KEY = os.getenv('RALLY_API_KEY')
RALLY_USERNAME = os.getenv('RALLY_USERNAME')
RALLY_BASE_URL = os.getenv('RALLY_BASE_URL', 'https://rally1.rallydev.com')
DAYS_BACK = int(os.getenv('DAYS_BACK', '30'))

# Email Configuration
YOUR_EMAIL = os.getenv('YOUR_EMAIL')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Rally Field Configuration
PAIRING_PARTNER_FIELD = 'c_PairingPartner'

# Validate required environment variables
required_vars = {
    'RALLY_API_KEY': RALLY_API_KEY,
    'RALLY_USERNAME': RALLY_USERNAME,
    'YOUR_EMAIL': YOUR_EMAIL,
    'EMAIL_PASSWORD': EMAIL_PASSWORD
}

missing_vars = [var for var, value in required_vars.items() if not value]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

def get_rally_headers():
    """Get headers for Rally API requests"""
    return {
        "ZSESSIONID": RALLY_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def get_user_object_id():
    """Get the current user's ObjectID"""
    url = f"{RALLY_BASE_URL}/slm/webservice/v2.0/user"
    response = requests.get(url, headers=get_rally_headers(), params={"fetch": "ObjectID,DisplayName"})
    user_data = response.json()
    return user_data["User"]["ObjectID"]

def get_accepted_stories():
    """Fetch accepted stories from Rally where you're primary or pairing partner"""
    
    print(f"Fetching all stories owned by {RALLY_USERNAME}...")
    
    user_object_id = get_user_object_id()
    
    # Fetch ALL stories you own (Rally API bug prevents combined queries)
    url = f"{RALLY_BASE_URL}/slm/webservice/v2.0/hierarchicalrequirement"
    
    params = {
        "query": f'(Owner.ObjectID = {user_object_id})',
        "fetch": f"FormattedID,Name,AcceptedDate,PlanEstimate,Owner,Project,ScheduleState,{PAIRING_PARTNER_FIELD}",
        "pagesize": 200,
        "order": "AcceptedDate DESC"
    }
    
    headers = get_rally_headers()
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        all_stories = data.get("QueryResult", {}).get("Results", [])
        print(f"Total stories you own: {len(all_stories)}")
        
        # Filter in Python (workaround for Rally API bug)
        cutoff_date = datetime.now() - timedelta(days=DAYS_BACK)
        accepted_stories = []
        
        for story in all_stories:
            # Check if Accepted
            if story.get("ScheduleState") != "Accepted":
                continue
            
            # Check if accepted within date range
            accepted_date_str = story.get("AcceptedDate")
            if accepted_date_str:
                try:
                    accepted_date = datetime.fromisoformat(accepted_date_str.replace("Z", "+00:00"))
                    if accepted_date.replace(tzinfo=None) < cutoff_date:
                        continue
                except:
                    continue
            
            accepted_stories.append(story)
        
        print(f"Accepted stories in last {DAYS_BACK} days: {len(accepted_stories)}")
        
        # Also check for stories where you're secondary owner or pairing partner
        print(f"\nChecking for stories where you're pairing partner...")
        
        # Query for stories where you're secondary owner
        params2 = {
            "query": f'({PAIRING_PARTNER_FIELD}.ObjectID = {user_object_id})',
            "fetch": f"FormattedID,Name,AcceptedDate,PlanEstimate,Owner,Project,ScheduleState,{PAIRING_PARTNER_FIELD}",
            "pagesize": 200,
            "order": "AcceptedDate DESC"
        }
        
        response2 = requests.get(url, params=params2, headers=headers)
        if response2.status_code == 200:
            data2 = response2.json()
            secondary_stories = data2.get("QueryResult", {}).get("Results", [])
            print(f"Stories where you're secondary/pairing: {len(secondary_stories)}")
            
            # Filter and merge
            for story in secondary_stories:
                if story.get("ScheduleState") != "Accepted":
                    continue
                    
                accepted_date_str = story.get("AcceptedDate")
                if accepted_date_str:
                    try:
                        accepted_date = datetime.fromisoformat(accepted_date_str.replace("Z", "+00:00"))
                        if accepted_date.replace(tzinfo=None) < cutoff_date:
                            continue
                    except:
                        continue
                
                # Avoid duplicates
                if story['FormattedID'] not in [s['FormattedID'] for s in accepted_stories]:
                    accepted_stories.append(story)
        
        # Sort by accepted date
        accepted_stories.sort(key=lambda x: x.get('AcceptedDate', ''), reverse=True)
        
        return accepted_stories
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching Rally stories: {e}")
        return []

def format_email_html(stories):
    """Format stories into an HTML email"""
    
    if not stories:
        return """
        <html>
            <body>
                <h2>Rally Accepted Stories</h2>
                <p>No newly accepted stories found.</p>
            </body>
        </html>
        """
    
    html = """
    <html>
        <head>
            <style>
                table {
                    border-collapse: collapse;
                    width: 100%;
                    font-family: Arial, sans-serif;
                }
                th {
                    background-color: #0078d4;
                    color: white;
                    padding: 12px;
                    text-align: left;
                    border: 1px solid #ddd;
                }
                td {
                    padding: 10px;
                    border: 1px solid #ddd;
                }
                tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
                h2 {
                    color: #0078d4;
                    font-family: Arial, sans-serif;
                }
                .story-id {
                    font-weight: bold;
                    color: #0078d4;
                }
                .summary {
                    margin-top: 20px;
                    padding: 10px;
                    background-color: #e8f4f8;
                    border-left: 4px solid #0078d4;
                }
            </style>
        </head>
        <body>
            <h2>Rally Accepted Stories</h2>
            <table>
                <thead>
                    <tr>
                        <th>Story ID</th>
                        <th>Title</th>
                        <th>Date Completed</th>
                        <th>Story Points</th>
                        <th>Role</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    total_points = 0
    
    for story in stories:
        story_id = story.get("FormattedID", "N/A")
        title = story.get("Name", "No title")
        accepted_date = story.get("AcceptedDate", "")
        story_points = story.get("PlanEstimate", 0) or 0
        
        owner_name = story.get("Owner", {}).get("_refObjectName", "") if story.get("Owner") else ""
        pairing_partner = story.get(PAIRING_PARTNER_FIELD, {})
        pairing_partner_name = pairing_partner.get("_refObjectName", "") if pairing_partner else ""
        
        # Determine role
        roles = []
        if RALLY_USERNAME in owner_name:
            roles.append("Primary")
        if RALLY_USERNAME in pairing_partner_name:
            roles.append("Pairing Partner")
        
        role = " & ".join(roles) if roles else "Primary"
        
        if accepted_date:
            try:
                date_obj = datetime.fromisoformat(accepted_date.replace("Z", "+00:00"))
                formatted_date = date_obj.strftime("%m/%d/%Y %I:%M %p")
            except:
                formatted_date = accepted_date
        else:
            formatted_date = "N/A"
        
        total_points += story_points
        
        html += f"""
                    <tr>
                        <td class="story-id">{story_id}</td>
                        <td>{title}</td>
                        <td>{formatted_date}</td>
                        <td>{story_points}</td>
                        <td>{role}</td>
                    </tr>
        """
    
    html += f"""
                </tbody>
            </table>
            <div class="summary">
                <strong>Summary:</strong> {len(stories)} story(ies) accepted | Total Story Points: {total_points}
            </div>
        </body>
    </html>
    """
    
    return html

def send_email(html_content, story_count):
    """Send email via Gmail SMTP"""
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Rally Accepted Stories - {story_count} Story(ies)'
    msg['From'] = YOUR_EMAIL
    msg['To'] = YOUR_EMAIL
    
    # Attach HTML content
    html_part = MIMEText(html_content, 'html')
    msg.attach(html_part)
    
    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(YOUR_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"\n✓ Email sent successfully to {YOUR_EMAIL} with {story_count} story(ies)")
    except Exception as e:
        print(f"\n✗ Error sending email: {e}")

def main():
    print("=" * 60)
    print("Rally to Gmail Script - Starting")
    print("=" * 60)
    
    stories = get_accepted_stories()
    
    print(f"\n{'=' * 60}")
    print(f"Found {len(stories)} accepted story(ies) for {RALLY_USERNAME}")
    print(f"{'=' * 60}")
    
    if len(stories) > 0:
        # Show preview
        print("\nStories found:")
        for story in stories[:10]:
            print(f"  - {story.get('FormattedID')}: {story.get('Name')[:60]}")
        if len(stories) > 10:
            print(f"  ... and {len(stories) - 10} more")
    
    html_content = format_email_html(stories)
    send_email(html_content, len(stories))

if __name__ == "__main__":
    main()