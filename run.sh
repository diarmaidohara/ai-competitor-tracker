#!/bin/bash

# AI Competitive Intelligence Tracker - Easy Launch Script

echo "========================================================"
echo "  AI COMPETITIVE INTELLIGENCE TRACKER"
echo "========================================================"
echo ""

# Run the scraper
echo "📡 Step 1: Scraping AI news sources..."
echo ""
python3 scraper.py
echo ""

# Check if scraping was successful
if [ $? -eq 0 ]; then
    echo "✅ Scraping completed successfully!"
    echo ""

    # Launch the dashboard
    echo "🚀 Step 2: Launching dashboard..."
    echo ""
    echo "Opening dashboard at http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "========================================================"
    echo ""

    python3 run_dashboard.py
else
    echo "❌ Scraping failed. Please check the error messages above."
    exit 1
fi
