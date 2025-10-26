#!/usr/bin/env python3
"""
Mailchimp Newsletter CSV Generator
Creates a CSV with all newsletter data including subject, preheader, audience, performance metrics, and local file paths.
"""

import os
import csv
import re
from datetime import datetime
from pathlib import Path
import requests


class MailchimpCSVGenerator:
    def __init__(self, api_key):
        """Initialize the Mailchimp CSV generator with API credentials."""
        self.api_key = api_key
        # Extract server prefix from API key (e.g., 'us19' from 'xxxxx-us19')
        self.server_prefix = api_key.split('-')[-1]
        self.base_url = f"https://{self.server_prefix}.api.mailchimp.com/3.0"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
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
    
    def get_campaign_report(self, campaign_id):
        """Fetch performance metrics for a specific campaign."""
        url = f"{self.base_url}/reports/{campaign_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"  Warning: Could not fetch report for campaign {campaign_id}")
            return None
    
    def get_list_name(self, list_id):
        """Fetch the name of a list/audience."""
        url = f"{self.base_url}/lists/{list_id}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 200:
            return response.json().get('name', 'Unknown')
        else:
            return 'Unknown'
    
    def sanitize_filename(self, filename):
        """Convert a string into a safe filename (same as original script)."""
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.replace(' ', '_')
        if len(filename) > 200:
            filename = filename[:200]
        return filename
    
    def find_local_file(self, campaign, newsletters_dir):
        """Find the corresponding local markdown file for a campaign."""
        send_time = campaign.get('send_time', '')
        subject = campaign.get('settings', {}).get('subject_line', 'No Subject')
        
        # Parse send time to get date string
        if send_time:
            try:
                dt = datetime.strptime(send_time, '%Y-%m-%dT%H:%M:%S%z')
                date_str = dt.strftime('%Y-%m-%d')
            except:
                date_str = send_time[:10] if len(send_time) >= 10 else 'unknown'
        else:
            date_str = 'unknown'
        
        # Construct expected filename
        filename = f"{date_str}_{self.sanitize_filename(subject)}.md"
        filepath = newsletters_dir / filename
        
        if filepath.exists():
            return str(filepath.absolute())
        else:
            return "File not found"
    
    def generate_csv(self, newsletters_dir='mailchimp_newsletters', output_file='mailchimp_newsletters.csv'):
        """Main method to generate the CSV file."""
        newsletters_path = Path(newsletters_dir)
        
        # Check if newsletters directory exists
        if not newsletters_path.exists():
            print(f"\nWarning: Directory '{newsletters_dir}' not found.")
            print("File paths will be marked as 'Directory not found'")
            newsletters_path = None
        else:
            print(f"\nNewsletter directory found: {newsletters_path.absolute()}")
        
        # Get all campaigns
        campaigns = self.get_all_campaigns()
        
        if not campaigns:
            print("No campaigns found!")
            return
        
        print(f"\nProcessing {len(campaigns)} campaigns...\n")
        
        # Cache for list names to avoid repeated API calls
        list_cache = {}
        
        # Prepare CSV data
        csv_data = []
        
        for i, campaign in enumerate(campaigns, 1):
            campaign_id = campaign.get('id', 'N/A')
            settings = campaign.get('settings', {})
            
            # Basic info
            subject = settings.get('subject_line', 'No Subject')
            preheader = settings.get('preview_text', '')
            send_time = campaign.get('send_time', '')
            
            # Format send time
            if send_time:
                try:
                    dt = datetime.strptime(send_time, '%Y-%m-%dT%H:%M:%S%z')
                    formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
                except:
                    formatted_date = send_time
            else:
                formatted_date = 'Unknown'
            
            # Get list/audience name
            list_id = campaign.get('recipients', {}).get('list_id')
            if list_id:
                if list_id not in list_cache:
                    list_cache[list_id] = self.get_list_name(list_id)
                audience = list_cache[list_id]
            else:
                audience = 'Unknown'
            
            # Check for segment
            segment_opts = campaign.get('recipients', {}).get('segment_opts')
            if segment_opts:
                audience += " (Segmented)"
            
            # Get performance metrics
            report = self.get_campaign_report(campaign_id)
            
            if report:
                emails_sent = report.get('emails_sent', 0)
                
                opens = report.get('opens', {})
                unique_opens = opens.get('unique_opens', 0)
                open_rate = opens.get('open_rate', 0) * 100
                
                clicks = report.get('clicks', {})
                unique_clicks = clicks.get('unique_clicks', 0)
                click_rate = clicks.get('click_rate', 0) * 100
                
                bounces = report.get('bounces', {})
                hard_bounces = bounces.get('hard_bounces', 0)
                soft_bounces = bounces.get('soft_bounces', 0)
                
                unsubscribed = report.get('unsubscribed', 0)
            else:
                emails_sent = unique_opens = open_rate = 0
                unique_clicks = click_rate = 0
                hard_bounces = soft_bounces = unsubscribed = 0
            
            # Find local file
            if newsletters_path:
                local_file = self.find_local_file(campaign, newsletters_path)
            else:
                local_file = "Directory not found"
            
            # Add row to CSV data
            row = {
                'Campaign ID': campaign_id,
                'Subject Line': subject,
                'Preheader': preheader,
                'Audience/List': audience,
                'Send Date': formatted_date,
                'Emails Sent': emails_sent,
                'Unique Opens': unique_opens,
                'Open Rate (%)': f"{open_rate:.2f}",
                'Unique Clicks': unique_clicks,
                'Click Rate (%)': f"{click_rate:.2f}",
                'Hard Bounces': hard_bounces,
                'Soft Bounces': soft_bounces,
                'Unsubscribes': unsubscribed,
                'Local File Path': local_file
            }
            
            csv_data.append(row)
            print(f"[{i}/{len(campaigns)}] {subject}")
        
        # Write CSV file
        output_path = Path(output_file)
        fieldnames = [
            'Campaign ID',
            'Subject Line',
            'Preheader',
            'Audience/List',
            'Send Date',
            'Emails Sent',
            'Unique Opens',
            'Open Rate (%)',
            'Unique Clicks',
            'Click Rate (%)',
            'Hard Bounces',
            'Soft Bounces',
            'Unsubscribes',
            'Local File Path'
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"\n{'='*60}")
        print(f"CSV Generated Successfully!")
        print(f"{'='*60}")
        print(f"Total campaigns: {len(csv_data)}")
        print(f"Output file: {output_path.absolute()}")
        
        return output_path


def main():
    """Main entry point for the script."""
    print("="*60)
    print("Mailchimp Newsletter CSV Generator")
    print("="*60)
    
    # Get API key from user
    api_key = input("\nEnter your Mailchimp API key: ").strip()
    
    if not api_key or '-' not in api_key:
        print("Error: Invalid API key format. Should be like 'xxxxxxxxxx-us19'")
        return
    
    # Get newsletters directory
    newsletters_dir = input("\nEnter newsletters directory (or press Enter for 'mailchimp_newsletters'): ").strip()
    if not newsletters_dir:
        newsletters_dir = 'mailchimp_newsletters'
    
    # Get output file name
    output_file = input("\nEnter output CSV filename (or press Enter for 'mailchimp_newsletters.csv'): ").strip()
    if not output_file:
        output_file = 'mailchimp_newsletters.csv'
    
    # Add .csv extension if not provided
    if not output_file.endswith('.csv'):
        output_file += '.csv'
    
    # Create generator and run
    generator = MailchimpCSVGenerator(api_key)
    generator.generate_csv(newsletters_dir, output_file)
    
    print("\nAll done! 🎉")
    print("You can now open the CSV in Excel or upload to Google Sheets.")


if __name__ == "__main__":
    main()
