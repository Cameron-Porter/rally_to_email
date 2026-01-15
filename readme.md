# Rally to Email - Accepted Stories Report

Automatically fetch your accepted Rally stories and receive them via email. This script queries Rally for stories where you're either the primary owner or pairing partner, then sends a formatted HTML email with all the details.

## Features

- ✅ Fetches stories where you're the primary owner
- ✅ Includes stories where you're listed as pairing partner
- ✅ Configurable date range (default: last 30 days)
- ✅ Beautiful HTML email with story details and point totals
- ✅ Easy desktop shortcut execution via .bat file
- ✅ Secure credential management using environment variables

## Prerequisites

- Python 3.7 or higher
- Gmail account (or other SMTP email service)
- Rally account with API access
- Gmail App Password (if using Gmail)

## Installation

### 1. Install Python Dependencies

```bash
pip install requests python-dotenv
```

### 2. Create Environment Configuration

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

Then edit `.env` with your information:

```env
RALLY_API_KEY=REPLACE_ME_WITH_OWN_KEY
RALLY_USERNAME=John Doe  # Replace with your name
RALLY_BASE_URL=https://rally1.rallydev.com
DAYS_BACK=200  # Check stories accepted in the last N days

# Email Configuration - Uncomment either the Gmail or Compassion section

# Gmail
# YOUR_EMAIL=yourown@gmail.com
# SMTP_SERVER=smtp.gmail.com
# EMAIL_PASSWORD=abcdPassword123  # Use app-specific password from Gmail

# Compassion
# YOUR_EMAIL=your_own_email@us.ci.org
# SMTP_SERVER=smtp.office365.com
# EMAIL_PASSWORD=abcdPassword123  # Your computer/email password

SMTP_PORT=587
```

### 3. Get Your Rally API Key

1. Log into Rally
2. Click your profile icon (top right)
3. Select "API Keys"
4. Click "Create New API Key"
5. Copy the key and paste it into your `.env` file

### 4. Set Up Email Authentication

**For Gmail:**

1. Uncomment the Gmail section in `.env`
2. Go to your Google Account settings
3. Navigate to Security → 2-Step Verification
4. Scroll down to "App passwords"
5. Generate a new app password for "Mail"
6. Copy the 16-character password and paste it into your `.env` file as `EMAIL_PASSWORD`

**Note:** Regular Gmail passwords won't work - you must use an App Password.

**For Compassion (Office 365):**

1. Uncomment the Compassion section in `.env`
2. Use your regular computer/email password as `EMAIL_PASSWORD`
3. SMTP server is already configured for `smtp.office365.com`

## Usage

### Option 1: Run from Command Line

```bash
python rally_to_email.py
```

### Option 2: Desktop Shortcut (Recommended)

1. **Create a desktop shortcut:**

   - Right-click on `rally_report.bat`
   - Select "Create shortcut"
   - Move the shortcut to your Desktop
   - (Optional) Right-click the shortcut → Properties → Change Icon to customize

2. **Double-click the desktop icon** to run the report!

### Option 3: Schedule Automatically

**Windows Task Scheduler:**

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., Daily at 5:00 PM)
4. Action: Start a program
5. Program: `python.exe`
6. Arguments: `"C:\path\to\rally_to_email.py"`
7. Start in: `"C:\path\to\script\directory"`

**Mac/Linux (cron):**

```bash
crontab -e
# Add this line to run daily at 5 PM:
0 17 * * * cd /path/to/script && /usr/bin/python3 rally_to_email.py
```

## Configuration Options

### Date Range

Change `DAYS_BACK` in your `.env` file to adjust how far back to search:

- `DAYS_BACK=7` - Last week
- `DAYS_BACK=30` - Last month
- `DAYS_BACK=90` - Last quarter
- `DAYS_BACK=200` - Last ~6.5 months (example default)

### Custom SMTP Server

The script supports both Gmail and Office 365 (Compassion) SMTP servers out of the box. To switch between them, simply comment/uncomment the appropriate section in your `.env` file.

**Gmail:**

```env
YOUR_EMAIL=yourown@gmail.com
SMTP_SERVER=smtp.gmail.com
EMAIL_PASSWORD=your_app_password  # Must use App Password
```

**Compassion (Office 365):**

```env
YOUR_EMAIL=your_email@us.ci.org
SMTP_SERVER=smtp.office365.com
EMAIL_PASSWORD=your_regular_password
```

**Other SMTP servers:**

```env
SMTP_SERVER=smtp.yourserver.com
SMTP_PORT=587  # Or 465 for SSL
```

### Rally Custom Fields

If your Rally instance uses a different field name for pairing partner, update this line in the script:

```python
PAIRING_PARTNER_FIELD = 'c_PairingPartner'  # Change to your field name
```

## Email Output

The email includes:

- **Story ID**: Rally formatted ID (e.g., US12345)
- **Title**: Story name
- **Date Completed**: When the story was accepted
- **Story Points**: Point estimate
- **Role**: Whether you were Primary, Pairing Partner, or both
- **Summary**: Total stories and points

## Troubleshooting

### "Missing required environment variables"

- Make sure your `.env` file is in the same directory as the script
- Check that all required variables are set (no blank values)

### "Error fetching Rally stories"

- Verify your `RALLY_API_KEY` is correct and active
- Check that `RALLY_BASE_URL` matches your Rally instance
- Ensure your `RALLY_USERNAME` matches exactly as shown in Rally

### "Error sending email"

- **Gmail users**: Make sure you're using an App Password, not your regular password
- **Compassion/Office 365 users**: Use your regular computer/email password
- Verify `SMTP_SERVER` and `SMTP_PORT` are correct
- For Gmail: Check that 2-Step Verification is enabled (required for App Passwords)
- Ensure only ONE email configuration section is uncommented in `.env`
- Try testing with a simple email client first to verify credentials

### No stories found

- Verify `RALLY_USERNAME` matches your name exactly in Rally (case-sensitive)
- Check that you have accepted stories in the specified date range
- Increase `DAYS_BACK` to search further back

### Pairing partner stories not showing

- Confirm the field name in your Rally instance (might be `c_CoOwner`, `c_SecondaryOwner`, etc.)
- Update `PAIRING_PARTNER_FIELD` in the script to match your Rally configuration

## File Structure

```
rally-to-email/
├── rally_to_email.py         # Main script
├── rally_report.bat          # Windows batch file for easy execution
├── .env.example              # Example configuration template
└── README.md                 # This file
```

## Support

For issues or questions:

1. Check the Troubleshooting section above
2. Verify all configuration values in `.env`
3. Review Rally API documentation: https://rally1.rallydev.com/slm/doc/webservice
4. Check Gmail App Password setup: https://support.google.com/accounts/answer/185833

## License

This script is provided as-is for personal use.

---

**Last Updated:** January 2026
