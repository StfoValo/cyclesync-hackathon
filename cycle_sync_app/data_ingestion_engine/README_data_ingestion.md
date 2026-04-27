# Data Ingestion Engine

This directory contains the background ETL (Extract, Transform, Load) pipeline for CycleSync, responsible for gathering live real-world data to feed into the Recycler Hub.

## Components

*   **`ingestion_service.py`**: A background service (`QThread`) initialized at application startup that orchestrates the data scraping process silently in the background without blocking the main UI thread.
*   **`market_scraper.py`**: Uses `feedparser` to scrape live market data from various commodities and recycling RSS feeds (e.g., Recycling Today, Waste Management World, Google News). It parses the entries, categorizes them into material sectors using keyword matching, and triggers the database manager to cache the signals.
