# Mailchimp Newsletter CSV Generator

Generate a comprehensive CSV file with all your Mailchimp newsletter data including subject lines, preheaders, audiences, performance metrics, and links to your local markdown files.

## What This Script Does

Creates a CSV file with the following columns:
- **Campaign ID** - Mailchimp's unique identifier
- **Subject Line** - Email subject
- **Preheader** - Preview text that appears in inbox
- **Audience/List** - Which list/audience it was sent to
- **Send Date** - When the email was sent
- **Emails Sent** - Total emails delivered
- **Unique Opens** - Number of unique recipients who opened
- **Open Rate (%)** - Percentage who opened
- **Unique Clicks** - Number of unique recipients who clicked
- **Click Rate (%)** - Percentage who clicked
- **Hard Bounces** - Permanent delivery failures
- **Soft Bounces** - Temporary delivery failures
- **Unsubscribes** - Number who unsubscribed
- **Local File Path** - Absolute path to the markdown file on your Mac

## Prerequisites

You should have already run `mailchimp_downloader.py` to download your newsletters as markdown files.

## Setup

### 1. Install Dependencies

```bash
pip3 install requests
```

(Note: `csv` and `pathlib` are built into Python)

### 2. Run the Script

```bash
python3 mailchimp_csv_generator.py
```

The script will ask you for:
1. Your Mailchimp API key (same one you used before)
2. The directory where your newsletters are stored (default: `mailchimp_newsletters`)
3. The output CSV filename (default: `mailchimp_newsletters.csv`)

## Example Usage

```
$ python3 mailchimp_csv_generator.py

============================================================
Mailchimp Newsletter CSV Generator
============================================================

Enter your Mailchimp API key: abc123def456-us19

Enter newsletters directory (or press Enter for 'mailchimp_newsletters'): 

Enter output CSV filename (or press Enter for 'mailchimp_newsletters.csv'): 

Fetching campaigns from Mailchimp...
  Fetched 150 campaigns so far...
Total campaigns found: 150

Newsletter directory found: /Users/you/mailchimp_newsletters

Processing 150 campaigns...

[1/150] Weekly Update - January 2024
[2/150] New Product Launch
...
```

## Output

The script creates a CSV file that you can:
- Open in Excel
- Upload to Google Sheets
- Import into any spreadsheet application
- Use for analysis in Python/R

## Features

- **Automatic list/audience lookup** - Fetches the actual list names from Mailchimp
- **Segment detection** - Indicates if a campaign was sent to a segment
- **Local file matching** - Automatically finds the corresponding markdown file
- **Performance metrics** - All key engagement metrics in one place
- **List caching** - Efficiently handles multiple campaigns sent to the same list

## Troubleshooting

### "Directory not found" in Local File Path column
- Make sure you run this script from the same directory where your `mailchimp_newsletters` folder is located
- Or provide the full path to the newsletters directory when prompted

### Missing preheaders
- Some campaigns might not have preheader text set - this is normal

### "File not found" for some campaigns
- This can happen if the original download failed for that campaign
- Or if the filename was too long and got truncated differently

## Tips

### For Google Sheets:
1. Open Google Sheets
2. Go to File → Import
3. Upload the CSV file
4. Choose "Replace spreadsheet" or "Insert new sheet"
5. The file paths will be text (not clickable), but you can copy/paste them

### For Excel:
1. Open Excel
2. Go to File → Import → CSV file
3. Make sure encoding is set to UTF-8
4. The file paths will be text that you can copy

### For Analysis:
The CSV format makes it easy to:
- Sort by open rate to find your best-performing campaigns
- Filter by audience to see performance by list
- Calculate average metrics across all campaigns
- Identify trends over time
