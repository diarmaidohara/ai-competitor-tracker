# AI Competitive Intelligence Tracker

An enterprise-grade web scraping system that monitors the AI industry landscape and generates professional intelligence reports.

## Features

- **Multi-threaded web scraping** with intelligent rate limiting
- **Anti-detection systems** with user-agent rotation and session management
- **RSS feed support** with HTML fallback
- **Content deduplication** and quality validation
- **Professional reporting** in multiple formats (Markdown, JSON, HTML)
- **Real-time dashboard** for visual monitoring

## Monitored Sources

### Tier 1 - Primary Competitors
- OpenAI Blog (RSS)
- Anthropic News (RSS)
- Hugging Face Blog (RSS)
- Google AI Blog (RSS)

### Tier 2 - Market Intelligence
- MIT Technology Review AI (RSS)
- The Verge AI (RSS)

**Currently scraping 6 sources successfully!**

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. (Optional) For browser automation fallback:
```bash
playwright install
```

## Usage

### Quick Start (Recommended)

Run everything with one command:

```bash
./run.sh
```

This will:
1. Scrape all 6 sources
2. Generate reports
3. Launch dashboard automatically at http://localhost:8000

### Manual Usage

**Run scraper only:**
```bash
python3 scraper.py
```

**View dashboard:**
```bash
python3 run_dashboard.py
```

The system will:
1. Scrape all configured sources (6 sources)
2. Collect 50+ articles in under 2 seconds
3. Generate reports in `reports/` directory
4. Save raw data in `data/` directory

## Output

- **Markdown Report**: Executive summary with key developments
- **JSON Data**: Raw structured data for further analysis
- **HTML Dashboard**: Interactive visual dashboard

Open the HTML dashboard in your browser to see the results visually!

## Configuration

Edit `config.yaml` to:
- Add/remove sources
- Adjust rate limiting
- Configure output formats
- Customize CSS selectors

## Architecture

- **SessionManager**: Handles HTTP sessions with user-agent rotation
- **RateLimiter**: Implements respectful crawling delays
- **ContentProcessor**: Validates and deduplicates content
- **WebScraper**: Core scraping engine with RSS and HTML support
- **ReportGenerator**: Creates professional multi-format reports
- **CompetitorIntelligence**: Main orchestrator

## Success Metrics

- Monitor 6+ sources successfully
- Complete cycle in under 15 minutes
- Generate professional executive-ready reports

## License

MIT
