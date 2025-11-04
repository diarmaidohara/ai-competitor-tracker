"""
Simple HTTP server to view the AI Competitive Intelligence Dashboard
"""

import http.server
import socketserver
import os
from pathlib import Path
import webbrowser
import time

PORT = 8000
REPORTS_DIR = "reports"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=REPORTS_DIR, **kwargs)

def main():
    # Find the latest dashboard
    reports_path = Path(REPORTS_DIR)
    if not reports_path.exists():
        print(f"Error: {REPORTS_DIR} directory not found!")
        print("Please run scraper.py first to generate reports.")
        return

    dashboards = sorted(reports_path.glob("dashboard_*.html"))

    if not dashboards:
        print(f"No dashboards found in {REPORTS_DIR}/")
        print("Please run scraper.py first to generate reports.")
        return

    latest_dashboard = dashboards[-1]

    print("="*60)
    print("AI COMPETITIVE INTELLIGENCE DASHBOARD")
    print("="*60)
    print(f"\nStarting local server on http://localhost:{PORT}")
    print(f"Serving: {latest_dashboard}")
    print("\nPress Ctrl+C to stop the server")
    print("="*60)

    # Start server
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        # Open browser
        time.sleep(1)
        url = f"http://localhost:{PORT}/{latest_dashboard.name}"
        print(f"\nOpening browser to: {url}\n")
        webbrowser.open(url)

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\nShutting down server...")
            httpd.shutdown()

if __name__ == "__main__":
    main()
