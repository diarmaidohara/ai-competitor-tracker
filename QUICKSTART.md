# Quick Start Guide - AI Competitive Intelligence Tracker

## What You've Built

A professional web scraping system that monitors AI companies and generates intelligence reports!

## Project Files

```
ai-competitor-tracker/
├── scraper.py              # Main scraping engine
├── config.yaml             # Configuration (sources, delays, etc.)
├── requirements.txt        # Python dependencies
├── run_dashboard.py        # Localhost dashboard server
├── Claude.md               # Project specifications
├── README.md               # Full documentation
├── reports/                # Generated reports (Markdown & HTML)
└── data/                   # Raw JSON data
```

## How to Use

### 1. Run the Scraper

```bash
python3 scraper.py
```

This will:
- Scrape 6 AI industry sources (OpenAI, TechCrunch, etc.)
- Generate reports in `reports/` directory
- Save data in `data/` directory
- Complete in ~15-20 seconds

### 2. View the Dashboard

**Option A: Open HTML directly**
```bash
open reports/dashboard_*.html
```

**Option B: Run localhost server (recommended)**
```bash
python3 run_dashboard.py
```
This opens your browser to http://localhost:8000 automatically!

### 3. View Text Reports

```bash
cat reports/report_*.md
```

## What It Monitors

### Tier 1 Sources
- OpenAI Blog (RSS feed)
- Anthropic News
- Google AI Blog (RSS feed)

### Tier 2 Sources
- TechCrunch AI
- VentureBeat AI
- Hugging Face Blog

## Key Features

✅ **Enterprise-grade scraping** with rate limiting and retries
✅ **Anti-detection** with user-agent rotation
✅ **RSS + HTML fallback** for maximum reliability
✅ **Content deduplication** to avoid duplicates
✅ **Multi-format output**: Markdown, JSON, HTML
✅ **Beautiful dashboard** with visual stats

## Customization

Edit `config.yaml` to:
- Add more sources
- Change scraping delays
- Adjust CSS selectors
- Configure output formats

## Example: Add a New Source

```yaml
sources:
  tier2:
    - name: "Your Source"
      url: "https://example.com/blog"
      selectors:
        articles: "article"
        title: "h2"
        link: "a"
        date: "time"
```

## Troubleshooting

**If scraping fails:**
- Check internet connection
- Some sites may block requests (this is normal)
- The system uses RSS feeds as fallback when available

**If no articles found:**
- CSS selectors might have changed
- Update selectors in `config.yaml`
- Check the logs for specific errors

## Next Steps

1. **Schedule daily runs** with cron:
   ```bash
   crontab -e
   # Add: 0 9 * * * cd /path/to/project && python3 scraper.py
   ```

2. **Add more sources** in `config.yaml`

3. **Customize reports** by editing the `ReportGenerator` class

4. **Set up alerts** by integrating with email/Slack

## Success!

You've built a professional competitive intelligence system! 🎉

The system follows best practices:
- Respectful crawling with delays
- Error handling and retries
- Professional reporting
- Modular, maintainable code

Check the HTML dashboard at http://localhost:8000 to see your results!
