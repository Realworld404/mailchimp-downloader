#!/usr/bin/env python3
"""
Mailchimp Newsletter Downloader
Downloads all historical newsletters from Mailchimp and saves them as markdown files
with performance metrics.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
import requests
from html import unescape
import html2text


class MailchimpDownloader:
    def __init__(self, api_key):
        """Initialize the Mailchimp downloader with API credentials."""
        self.api_key = api_key
        # Extract server prefix from API key (e.g., 'us19' from 'xxxxx-us19')
        self.server_prefix = api_key.split('-')[-1]
        self.base_url = f"https://{self.server_prefix}.api.mailchimp.com/3.0"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.body_width = 0  # Don't wrap lines
        
    def get_all_campaigns(self):
        """Fetch all campaigns from Mailchimp."""
        campaigns = []
        offset = 0
        count = 1000  # Max per request
        
        print("Fetching campaigns from Mailchimp...")
        
        while True:
            url = f"{self.base_url}/campaigns"
            params = {
                'count': count,
                'offset': offset,
                'status': 'sent',  # Only get sent campaigns
                'sort_field': 'send_time',
                'sort_dir': 'DESC'
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"Error fetching campaigns: {response.status_code}")
                print(response.text)
                break
            
            data = response.json()
            batch_campaigns = data.get('campaigns', [])
            
            if not batch_campaigns:
                break
                
            campaigns.extend(batch_campaigns)
            print(f"  Fetched {len(campaigns)} campaigns so far...")
            
            # Check if we've got all campaigns
            if len(batch_campaigns) < count:
                break
                
            offset += count
        
        print(f"Total campaigns found: {len(campaigns)}")
        return campaigns
    
    def get_campaign_content(self, campaign_id):
        """Fetch the HTML content of a specific campaign."""
        url = f"{self.base_url}/campaigns/{campaign_id}/content"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Error fetching content for campaign {campaign_id}: {response.status_code}")
            return None
    
    def get_campaign_report(self, campaign_id):
        """Fetch performance metrics for a specific campaign."""
        url = f"{self.base_url}/reports/{campaign_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Error fetching report for campaign {campaign_id}: {response.status_code}")
            return None
    
    def sanitize_filename(self, filename):
        """Convert a string into a safe filename."""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Limit length
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    def html_to_markdown(self, html_content):
        """Convert HTML content to markdown."""
        if not html_content:
            return ""
        return self.html_converter.handle(html_content)
    
    def create_markdown_file(self, campaign, content, report, output_dir):
        """Create a markdown file for a campaign with metadata and content."""
        # Extract key information
        campaign_id = campaign.get('id', 'unknown')
        subject = campaign.get('settings', {}).get('subject_line', 'No Subject')
        send_time = campaign.get('send_time', '')
        
        # Parse send time
        if send_time:
            try:
                dt = datetime.strptime(send_time, '%Y-%m-%dT%H:%M:%S%z')
                date_str = dt.strftime('%Y-%m-%d')
                formatted_date = dt.strftime('%B %d, %Y at %I:%M %p')
            except:
                date_str = send_time[:10] if len(send_time) >= 10 else 'unknown'
                formatted_date = send_time
        else:
            date_str = 'unknown'
            formatted_date = 'Unknown'
        
        # Create filename
        filename = f"{date_str}_{self.sanitize_filename(subject)}.md"
        filepath = output_dir / filename
        
        # Get HTML content
        html_content = content.get('html', '') if content else ''
        markdown_content = self.html_to_markdown(html_content)
        
        # Build performance metrics
        metrics = []
        if report:
            metrics.append(f"**Emails Sent:** {report.get('emails_sent', 'N/A')}")
            
            opens = report.get('opens', {})
            metrics.append(f"**Opens:** {opens.get('unique_opens', 'N/A')} ({opens.get('open_rate', 0) * 100:.1f}%)")
            
            clicks = report.get('clicks', {})
            metrics.append(f"**Clicks:** {clicks.get('unique_clicks', 'N/A')} ({clicks.get('click_rate', 0) * 100:.1f}%)")
            
            metrics.append(f"**Bounces:** {report.get('bounces', {}).get('hard_bounces', 'N/A')}")
            metrics.append(f"**Unsubscribes:** {report.get('unsubscribed', 'N/A')}")
        
        # Build markdown document
        md_content = f"""# {subject}

---

**Campaign ID:** {campaign_id}  
**Sent:** {formatted_date}  
**List:** {campaign.get('settings', {}).get('title', 'N/A')}

## Performance Metrics

{chr(10).join(metrics) if metrics else 'No metrics available'}

---

## Content

{markdown_content}

---

*Downloaded from Mailchimp on {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"  ✓ Saved: {filename}")
        return filepath
    
    def download_all_newsletters(self, output_dir='mailchimp_newsletters'):
        """Main method to download all newsletters."""
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        print(f"\nOutput directory: {output_path.absolute()}\n")
        
        # Get all campaigns
        campaigns = self.get_all_campaigns()
        
        if not campaigns:
            print("No campaigns found!")
            return
        
        print(f"\nDownloading {len(campaigns)} newsletters...\n")
        
        successful = 0
        failed = 0
        
        # Process each campaign
        for i, campaign in enumerate(campaigns, 1):
            campaign_id = campaign.get('id')
            subject = campaign.get('settings', {}).get('subject_line', 'No Subject')
            
            print(f"[{i}/{len(campaigns)}] {subject}")
            
            # Get content and report
            content = self.get_campaign_content(campaign_id)
            report = self.get_campaign_report(campaign_id)
            
            if content:
                try:
                    self.create_markdown_file(campaign, content, report, output_path)
                    successful += 1
                except Exception as e:
                    print(f"  ✗ Error creating file: {e}")
                    failed += 1
            else:
                print(f"  ✗ Skipped (no content)")
                failed += 1
        
        print(f"\n{'='*60}")
        print(f"Download Complete!")
        print(f"{'='*60}")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Output directory: {output_path.absolute()}")


def main():
    """Main entry point for the script."""
    print("="*60)
    print("Mailchimp Newsletter Downloader")
    print("="*60)
    
    # Get API key from user
    api_key = input("\nEnter your Mailchimp API key: ").strip()
    
    if not api_key or '-' not in api_key:
        print("Error: Invalid API key format. Should be like 'xxxxxxxxxx-us19'")
        return
    
    # Optional: custom output directory
    output_dir = input("\nEnter output directory (or press Enter for 'mailchimp_newsletters'): ").strip()
    if not output_dir:
        output_dir = 'mailchimp_newsletters'
    
    # Create downloader and run
    downloader = MailchimpDownloader(api_key)
    downloader.download_all_newsletters(output_dir)
    
    print("\nAll done! 🎉")


if __name__ == "__main__":
    main()
