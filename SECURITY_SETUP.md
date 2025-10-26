# Secure API Key Storage Setup

This guide shows you how to safely store your Mailchimp API key locally without hardcoding it in scripts or accidentally committing it to version control.

## Quick Setup (3 steps)

### 1. Install the required package

```bash
pip3 install python-dotenv
```

### 2. Create a `.env` file

In your project directory, create a file named `.env` (note the dot at the beginning):

```bash
touch .env
```

Then edit it and add your API key:

```
MAILCHIMP_API_KEY=your-actual-api-key-us19
```

**Example:**
```
MAILCHIMP_API_KEY=abc123def456789-us6
```

### 3. Verify it's in your .gitignore

The `.env` file should **never** be committed to git. Make sure your `.gitignore` includes:

```
.env
```

## How It Works

When you run the script, it will:
1. ✅ First check for `MAILCHIMP_API_KEY` in your `.env` file
2. ✅ If found, use it automatically (no typing needed!)
3. ✅ If not found, prompt you to enter it manually

## Security Benefits

✅ **No hardcoded secrets** - API keys aren't in your Python files  
✅ **Git-safe** - `.env` is in `.gitignore` so it won't be committed  
✅ **Easy rotation** - Change the key in one place if needed  
✅ **Shareable code** - You can share your scripts without exposing credentials  

## File Structure

Your project should look like this:

```
your-project/
├── .env                          # Your actual API key (NOT in git)
├── .env.example                  # Template (safe to commit)
├── .gitignore                    # Includes .env
├── mailchimp_csv_generator_robust.py
├── mailchimp_downloader.py
└── mailchimp_newsletters/        # Your downloaded files
```

## Alternative: System Environment Variables (Optional)

Instead of a `.env` file, you can also set it as a system environment variable:

### On macOS/Linux:
Add to your `~/.zshrc` or `~/.bash_profile`:
```bash
export MAILCHIMP_API_KEY="your-api-key-us19"
```

Then reload:
```bash
source ~/.zshrc
```

### On Windows:
```powershell
setx MAILCHIMP_API_KEY "your-api-key-us19"
```

## Verifying Your Setup

To check if your API key is loaded:

```bash
python3 -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✓ Found' if os.getenv('MAILCHIMP_API_KEY') else '✗ Not found')"
```

## Troubleshooting

### "No API key found in .env file"
- Make sure the file is named `.env` (with a dot)
- Make sure you're running the script from the same directory as `.env`
- Check there are no spaces around the `=` sign
- Make sure the format is: `MAILCHIMP_API_KEY=your-key-here`

### Script still asks for API key
- Make sure you've installed `python-dotenv`: `pip3 install python-dotenv`
- Verify `.env` is in the same directory where you run the script

### Can't find .env file in Finder (macOS)
- Hidden files (starting with `.`) are hidden by default
- Press `Cmd + Shift + .` in Finder to show hidden files
- Or use Terminal: `ls -la` to see all files

## Best Practices

1. **Never commit `.env`** - Always keep it in `.gitignore`
2. **Use `.env.example`** - Commit this template to show what variables are needed
3. **Rotate keys periodically** - Change your API key every few months
4. **Restrict key permissions** - In Mailchimp, only give keys the permissions they need
5. **Don't share your `.env`** - Each user/machine should have their own

## Sharing Your Project

When sharing your code:
1. ✅ Include `.env.example` 
2. ✅ Include `.gitignore`
3. ✅ Include README with setup instructions
4. ❌ Never include `.env`

Others can then:
1. Copy `.env.example` to `.env`
2. Add their own API key
3. Run the scripts

## Revoking Access

If you think your API key was exposed:
1. Log into Mailchimp
2. Go to Account → Extras → API keys
3. Delete the compromised key
4. Generate a new key
5. Update your `.env` file with the new key
