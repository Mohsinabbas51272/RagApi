#!/usr/bin/env python3
"""
CLI Web Crawler for Brillanz Group Websites
Usage:
    python scripts/crawl_all.py
    python scripts/crawl_all.py --site softoo --limit 3
"""
import sys
import argparse
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.services.crawler import MultiWebsiteCrawler

def main():
    parser = argparse.ArgumentParser(description="Crawl Brillanz Group Websites")
    parser.add_argument("--site", type=str, help="Specific website ID to crawl (e.g. softoo, okoinsights)")
    parser.add_argument("--limit", type=int, default=3, help="Max pages to crawl per website (default: 3)")
    args = parser.parse_args()

    crawler = MultiWebsiteCrawler(max_pages_per_site=args.limit)
    target_ids = [args.site] if args.site else None
    
    print(f"🚀 Starting Brillanz Crawler (Limit: {args.limit} pages/site)...")
    docs = crawler.crawl_all(target_ids=target_ids, max_pages_per_site=args.limit)
    
    print("\n✅ Crawling Complete!")
    print(f"Total documents extracted: {len(docs)}")
    for d in docs:
        print(f"  • [{d['website_name']}] {d['title']} -> {d['url']} ({len(d['content'])} chars)")

if __name__ == "__main__":
    main()
