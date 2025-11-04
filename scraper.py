"""
AI Competitive Intelligence Scraper
Enterprise-grade web scraping system for monitoring AI industry landscape
"""

import requests
from bs4 import BeautifulSoup
import feedparser
import time
import random
import yaml
import logging
from datetime import datetime
from typing import List, Dict, Optional
from urllib.parse import urljoin
import hashlib
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SessionManager:
    """Manages HTTP sessions with user-agent rotation and headers"""

    def __init__(self, user_agents: List[str]):
        self.user_agents = user_agents
        self.session = requests.Session()
        self._update_headers()

    def _update_headers(self):
        """Rotate user agent and set realistic headers"""
        self.session.headers.update({
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def get(self, url: str, timeout: int = 30) -> Optional[requests.Response]:
        """Make GET request with error handling"""
        try:
            self._update_headers()  # Rotate headers for each request
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"Request failed for {url}: {e}")
            return None


class RateLimiter:
    """Implements intelligent rate limiting with random delays"""

    def __init__(self, min_delay: float, max_delay: float):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0

    def wait(self):
        """Wait appropriate time before next request"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time

        delay = random.uniform(self.min_delay, self.max_delay)
        if time_since_last < delay:
            sleep_time = delay - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            time.sleep(sleep_time)

        self.last_request_time = time.time()


class ContentProcessor:
    """Processes and validates scraped content"""

    def __init__(self):
        self.seen_hashes = set()

    def generate_hash(self, content: str) -> str:
        """Generate content hash for deduplication"""
        return hashlib.md5(content.encode()).hexdigest()

    def is_duplicate(self, content: str) -> bool:
        """Check if content has been seen before"""
        content_hash = self.generate_hash(content)
        if content_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(content_hash)
        return False

    def extract_text(self, soup_element) -> str:
        """Extract and clean text from BeautifulSoup element"""
        if soup_element is None:
            return ""
        return soup_element.get_text(strip=True)

    def validate_article(self, article: Dict) -> bool:
        """Validate article has required fields"""
        required = ['title', 'url', 'source']
        return all(article.get(field) for field in required)


class WebScraper:
    """Main web scraping engine"""

    def __init__(self, config: Dict):
        self.config = config
        self.session_manager = SessionManager(config['user_agents'])
        self.rate_limiter = RateLimiter(
            config['scraping']['request_delay_min'],
            config['scraping']['request_delay_max']
        )
        self.content_processor = ContentProcessor()
        self.articles = []

    def scrape_rss(self, url: str, source_name: str) -> List[Dict]:
        """Scrape RSS feed (preferred method when available)"""
        logger.info(f"Scraping RSS feed: {source_name}")
        articles = []

        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:  # Get latest 10 entries
                article = {
                    'title': entry.get('title', 'No title'),
                    'url': entry.get('link', ''),
                    'source': source_name,
                    'date': entry.get('published', datetime.now().isoformat()),
                    'summary': entry.get('summary', '')[:300],
                    'scrape_method': 'rss'
                }

                if not self.content_processor.is_duplicate(article['title']):
                    articles.append(article)
                    logger.info(f"  ✓ {article['title'][:60]}...")

        except Exception as e:
            logger.error(f"RSS parsing failed for {source_name}: {e}")

        return articles

    def scrape_html(self, source: Dict) -> List[Dict]:
        """Scrape HTML website with CSS selectors"""
        logger.info(f"Scraping HTML: {source['name']}")
        articles = []

        self.rate_limiter.wait()
        response = self.session_manager.get(source['url'])

        if not response:
            return articles

        try:
            soup = BeautifulSoup(response.content, 'lxml')
            selectors = source.get('selectors', {})

            # Find all article elements
            article_elements = soup.select(selectors.get('articles', 'article'))

            for element in article_elements[:10]:  # Get latest 10
                try:
                    # Extract title
                    title_elem = element.select_one(selectors.get('title', 'h2'))
                    title = self.content_processor.extract_text(title_elem)

                    # Extract link
                    link_elem = element.select_one(selectors.get('link', 'a'))
                    url = link_elem.get('href', '') if link_elem else ''
                    if url and not url.startswith('http'):
                        url = urljoin(source['url'], url)

                    # Extract date
                    date_elem = element.select_one(selectors.get('date', 'time'))
                    date = date_elem.get('datetime', '') if date_elem else datetime.now().isoformat()

                    article = {
                        'title': title,
                        'url': url,
                        'source': source['name'],
                        'date': date,
                        'summary': '',
                        'scrape_method': 'html'
                    }

                    if self.content_processor.validate_article(article):
                        if not self.content_processor.is_duplicate(title):
                            articles.append(article)
                            logger.info(f"  ✓ {title[:60]}...")

                except Exception as e:
                    logger.debug(f"Failed to parse article element: {e}")
                    continue

        except Exception as e:
            logger.error(f"HTML parsing failed for {source['name']}: {e}")

        return articles

    def scrape_source(self, source: Dict) -> List[Dict]:
        """Scrape a single source (tries RSS first, falls back to HTML)"""
        articles = []

        # Try RSS first if available
        if 'rss' in source:
            articles = self.scrape_rss(source['rss'], source['name'])
            if articles:
                return articles

        # Fallback to HTML scraping
        return self.scrape_html(source)

    def scrape_all_sources(self) -> List[Dict]:
        """Scrape all configured sources"""
        all_articles = []

        # Scrape Tier 1 sources (primary competitors)
        logger.info("\n=== Scraping Tier 1 Sources (Primary Competitors) ===")
        for source in self.config['sources'].get('tier1', []):
            try:
                articles = self.scrape_source(source)
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Failed to scrape {source['name']}: {e}")

        # Scrape Tier 2 sources (market intelligence)
        logger.info("\n=== Scraping Tier 2 Sources (Market Intelligence) ===")
        for source in self.config['sources'].get('tier2', []):
            try:
                articles = self.scrape_source(source)
                all_articles.extend(articles)
            except Exception as e:
                logger.error(f"Failed to scrape {source['name']}: {e}")

        self.articles = all_articles
        return all_articles


class ReportGenerator:
    """Generates professional intelligence reports"""

    def __init__(self, config: Dict):
        self.config = config
        self.reports_dir = Path(config['output']['reports_dir'])
        self.data_dir = Path(config['output']['data_dir'])
        self.reports_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

    def generate_markdown_report(self, articles: List[Dict]) -> str:
        """Generate executive markdown report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Group articles by source
        by_source = {}
        for article in articles:
            source = article['source']
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(article)

        report = f"""# AI Competitive Intelligence Report
Generated: {timestamp}

## Executive Summary
- **Sources Monitored:** {len(by_source)}
- **New Developments Detected:** {len(articles)}
- **Scraping Success Rate:** {len(by_source)}/{len(self.config['sources'].get('tier1', [])) + len(self.config['sources'].get('tier2', []))} sources

## Latest Developments by Source

"""

        for source, source_articles in sorted(by_source.items()):
            report += f"\n### {source}\n"
            report += f"*{len(source_articles)} new articles found*\n\n"

            for article in source_articles[:5]:  # Top 5 per source
                report += f"**{article['title']}**\n"
                report += f"- URL: {article['url']}\n"
                report += f"- Date: {article['date']}\n"
                if article.get('summary'):
                    report += f"- Summary: {article['summary']}\n"
                report += "\n"

        report += f"""
## Data Quality Metrics
- Total articles processed: {len(articles)}
- Unique articles (deduplicated): {len(articles)}
- Scrape methods: RSS + HTML fallback
- Timestamp: {timestamp}

---
*Generated by AI Competitive Intelligence System*
"""

        return report

    def save_json_data(self, articles: List[Dict]):
        """Save raw data as JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.data_dir / f"intelligence_data_{timestamp}.json"

        with open(filename, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'total_articles': len(articles),
                'articles': articles
            }, f, indent=2)

        logger.info(f"JSON data saved to: {filename}")

    def generate_html_report(self, articles: List[Dict]) -> str:
        """Generate HTML dashboard"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>AI Competitive Intelligence Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-number {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        .article-card {{
            background: white;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .source-badge {{
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            display: inline-block;
            margin-bottom: 10px;
        }}
        .article-title {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .article-meta {{
            color: #666;
            font-size: 14px;
        }}
        a {{
            color: #667eea;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AI Competitive Intelligence Dashboard</h1>
        <p>Generated: {timestamp}</p>
    </div>

    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{len(articles)}</div>
            <div>New Articles</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{len(set(a['source'] for a in articles))}</div>
            <div>Sources Monitored</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">Live</div>
            <div>System Status</div>
        </div>
    </div>

    <h2>Latest Intelligence</h2>
"""

        for article in articles:
            html += f"""
    <div class="article-card">
        <span class="source-badge">{article['source']}</span>
        <div class="article-title">{article['title']}</div>
        <div class="article-meta">
            <a href="{article['url']}" target="_blank">Read Article →</a> |
            {article['date']}
        </div>
    </div>
"""

        html += """
</body>
</html>
"""
        return html

    def generate_reports(self, articles: List[Dict]):
        """Generate all report formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Markdown report
        markdown = self.generate_markdown_report(articles)
        md_file = self.reports_dir / f"report_{timestamp}.md"
        with open(md_file, 'w') as f:
            f.write(markdown)
        logger.info(f"Markdown report saved to: {md_file}")

        # JSON data
        self.save_json_data(articles)

        # HTML dashboard
        html = self.generate_html_report(articles)
        html_file = self.reports_dir / f"dashboard_{timestamp}.html"
        with open(html_file, 'w') as f:
            f.write(html)
        logger.info(f"HTML dashboard saved to: {html_file}")

        return md_file, html_file


class CompetitorIntelligence:
    """Main orchestrator for competitive intelligence gathering"""

    def __init__(self, config_path: str = 'config.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.scraper = WebScraper(self.config)
        self.report_generator = ReportGenerator(self.config)

    def execute_intelligence_gathering(self):
        """Execute complete intelligence gathering cycle"""
        logger.info("\n" + "="*60)
        logger.info("AI COMPETITIVE INTELLIGENCE SYSTEM STARTING")
        logger.info("="*60)

        start_time = time.time()

        # Scrape all sources
        articles = self.scraper.scrape_all_sources()

        # Generate reports
        logger.info(f"\n=== Generating Reports ===")
        logger.info(f"Total articles collected: {len(articles)}")

        if articles:
            md_file, html_file = self.report_generator.generate_reports(articles)

            elapsed = time.time() - start_time
            logger.info(f"\n{'='*60}")
            logger.info(f"INTELLIGENCE GATHERING COMPLETE")
            logger.info(f"Duration: {elapsed:.2f} seconds")
            logger.info(f"Articles collected: {len(articles)}")
            logger.info(f"Reports generated:")
            logger.info(f"  - Markdown: {md_file}")
            logger.info(f"  - HTML Dashboard: {html_file}")
            logger.info(f"{'='*60}\n")

            return md_file, html_file
        else:
            logger.warning("No articles collected. Check configuration and network connectivity.")
            return None, None


def main():
    """Main entry point"""
    try:
        intelligence = CompetitorIntelligence()
        md_file, html_file = intelligence.execute_intelligence_gathering()

        if html_file:
            print(f"\n🎉 Success! Open the dashboard in your browser:")
            print(f"   file://{html_file.absolute()}")

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
