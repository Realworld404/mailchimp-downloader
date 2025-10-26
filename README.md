# Mailchimp Newsletter Downloader

Download all your historical newsletters from Mailchimp as markdown files with performance metrics.

## Features

- Downloads all sent campaigns from your Mailchimp account
- Converts HTML newsletters to clean markdown format
- Includes performance metrics (opens, clicks, bounces, unsubscribes)
- Organizes files by date and subject line
- Preserves all newsletter content and formatting

## Setup Instructions

### 1. Get Your Mailchimp API Key

1. Log in to your Mailchimp account
2. Go to **Account** → **Extras** → **API keys**
3. Click **Create A Key**
4. Copy your API key (it will look like: `xxxxxxxxxx-us19`)

### 2. Install Dependencies

Open Terminal and run:

```bash
pip3 install -r requirements.txt
```

Or install packages individually:

```bash
pip3 install requests html2text
```

### 3. Run the Script

```bash
python3 mailchimp_downloader.py
```

The script will:
1. Ask for your Mailchimp API key
2. Ask for an output directory (default: `mailchimp_newsletters`)
3. Download all your newsletters
4. Save them as markdown files

## Output Format

Each newsletter will be saved as a markdown file with:

- **Filename:** `YYYY-MM-DD_Subject_Line.md`
- **Content includes:**
  - Campaign metadata (ID, send date, list name)
  - Performance metrics (opens, clicks, bounces, unsubscribes)
  - Full newsletter content in markdown format

### Example Output

```
mailchimp_newsletters/
├── 2024-01-15_Weekly_Update_January.md
├── 2024-02-01_New_Product_Launch.md
├── 2024-03-10_Spring_Newsletter.md
└── ...
```

## Troubleshooting

### "Invalid API key format"
- Make sure your API key includes the server prefix (e.g., `-us19`)
- The format should be: `xxxxxxxxxx-us19`

### "Error fetching campaigns"
- Verify your API key is correct
- Check that your API key has the necessary permissions

### Missing newsletters
- The script only downloads campaigns with status "sent"
- Draft or scheduled campaigns are not included

## Performance

- The script handles rate limits automatically
- Downloads can take a few minutes for large accounts
- Typical download speed: ~10-20 newsletters per minute

## Notes

- The script uses the Mailchimp API v3.0
- All dates are preserved in their original timezone
- Images in newsletters are referenced by their original URLs
- Links are preserved in markdown format

## Security

- Your API key is only used during script execution
- No data is sent anywhere except to/from Mailchimp's API
- Consider deleting your API key from Mailchimp after use if you don't need it

## Support

If you encounter any issues, check:
1. Your API key is valid and active
2. You have network connectivity
3. The output directory has write permissions
