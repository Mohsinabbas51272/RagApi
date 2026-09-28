import os
import json
import logging
import re
import time
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Set, Optional
import requests
from bs4 import BeautifulSoup

from app.config import WEBSITES_INVENTORY_PATH, RAW_DOCUMENTS_PATH, DATA_DIR

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

class MultiWebsiteCrawler:
    def __init__(self, max_pages_per_site: int = 5, request_timeout: int = 8):
        self.inventory_path = WEBSITES_INVENTORY_PATH
        self.raw_documents_path = RAW_DOCUMENTS_PATH
        self.crawled_dir = os.path.join(DATA_DIR, "crawled")
        self.max_pages_per_site = max_pages_per_site
        self.request_timeout = request_timeout
        os.makedirs(self.crawled_dir, exist_ok=True)

    def load_target_websites(self) -> List[Dict[str, Any]]:
        """Loads target website definitions from the inventory."""
        try:
            if os.path.exists(self.inventory_path):
                with open(self.inventory_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("websites", [])
        except Exception as e:
            logger.error(f"Error reading website inventory: {e}")
        return []

    def clean_html(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parses HTML, removes boilerplate, and extracts clean structured text."""
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Extract and sanitize title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)
        else:
            title = urlparse(url).path.strip("/").replace("-", " ").title() or "Home"

        # 2. Remove non-content elements
        for element in soup(["script", "style", "noscript", "nav", "footer", "header", "svg", "form", "iframe", "aside"]):
            element.extract()

        # 3. Remove common cookie/consent modals
        for modal in soup.find_all(attrs={"class": re.compile(r"cookie|consent|modal|popup|banner", re.I)}):
            modal.extract()

        # 4. Extract headings and paragraph blocks
        headings = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            text = h.get_text(strip=True)
            if text and len(text) > 3:
                headings.append(text)

        # 5. Extract structured text
        paragraphs = []
        for p in soup.find_all(["p", "li", "article", "section"]):
            text = p.get_text(separator=" ", strip=True)
            if text and len(text) > 20:
                paragraphs.append(text)

        # Deduplicate and join
        cleaned_text = "\n\n".join(paragraphs)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

        # Extract internal links
        internal_links = []
        base_domain = urlparse(url).netloc
        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            full_url = urljoin(url, href)
            parsed_href = urlparse(full_url)
            
            # Same domain filter, ignore anchors/assets
            if parsed_href.netloc == base_domain:
                clean_path = parsed_href.path
                if not re.search(r"\.(png|jpg|jpeg|gif|svg|pdf|css|js|zip)$", clean_path, re.I):
                    internal_links.append(f"{parsed_href.scheme}://{parsed_href.netloc}{clean_path}")

        return {
            "title": title,
            "content": cleaned_text,
            "headings": headings[:10],
            "internal_links": list(set(internal_links))
        }

    def determine_category(self, url: str, site_category: str) -> str:
        path = urlparse(url).path.lower()
        if "service" in path:
            return "Services"
        elif "solution" in path:
            return "Solutions"
        elif "product" in path:
            return "Products"
        elif "about" in path:
            return "About Us"
        elif "case-stud" in path or "project" in path:
            return "Case Studies"
        elif "blog" in path or "insight" in path or "news" in path:
            return "Blogs & Insights"
        elif "privacy" in path or "term" in path or "policy" in path:
            return "Legal & Policy"
        elif "contact" in path:
            return "Contact"
        return site_category or "General Information"

    def crawl_site(self, site: Dict[str, Any], max_pages: int = None) -> List[Dict[str, Any]]:
        """Crawls a single Brillanz website up to max_pages."""
        limit = max_pages or self.max_pages_per_site
        site_id = site["id"]
        site_name = site["name"]
        root_url = site["url"].rstrip("/")
        
        headers = {"User-Agent": USER_AGENT}
        visited_urls: Set[str] = set()
        to_visit: List[str] = [root_url]
        
        # Add priority paths from inventory
        for path in site.get("priority_paths", []):
            full = urljoin(root_url, path)
            if full not in to_visit:
                to_visit.append(full)

        site_documents = []
        logger.info(f"Starting crawl for {site_name} ({root_url}) - Queue: {len(to_visit)} initial targets")

        while to_visit and len(site_documents) < limit:
            current_url = to_visit.pop(0)
            if current_url in visited_urls:
                continue
            visited_urls.add(current_url)

            try:
                logger.info(f"[{site_name}] Fetching: {current_url}")
                resp = requests.get(current_url, headers=headers, timeout=self.request_timeout)
                
                if resp.status_code == 200 and "text/html" in resp.headers.get("Content-Type", ""):
                    parsed = self.clean_html(resp.text, current_url)
                    
                    # If page content is meaningful
                    if len(parsed["content"]) > 100:
                        doc = {
                            "id": f"doc-{site_id}-{len(site_documents)+1:02d}",
                            "website_id": site_id,
                            "website_name": site_name,
                            "url": current_url,
                            "title": parsed["title"],
                            "category": self.determine_category(current_url, site.get("category", "")),
                            "headings": parsed["headings"],
                            "content": parsed["content"],
                            "last_crawled": time.strftime("%Y-%m-%dT%H:%M:%SZ")
                        }
                        site_documents.append(doc)

                        # Queue discovered links
                        for link in parsed["internal_links"]:
                            if link not in visited_urls and link not in to_visit:
                                to_visit.append(link)

                # Polite crawling delay
                time.sleep(0.3)

            except Exception as e:
                logger.warning(f"[{site_name}] Failed to fetch {current_url}: {e}")

        # If live scraping fetched less content (e.g. timeout/SPA), ensure baseline seed exists
        if not site_documents:
            logger.info(f"[{site_name}] Generating fallback baseline entry.")
            site_documents.append({
                "id": f"doc-{site_id}-fallback",
                "website_id": site_id,
                "website_name": site_name,
                "url": root_url,
                "title": f"{site_name} - {site.get('category', 'Company Profile')}",
                "category": site.get("category", "General"),
                "headings": site.get("key_topics", []),
                "content": f"{site_name} is an operating entity of the Brillanz Group. Focus: {site.get('tagline', '')}. Core offerings include: {', '.join(site.get('key_topics', []))}.",
                "last_crawled": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            })

        # Save site specific JSON
        site_json_path = os.path.join(self.crawled_dir, f"{site_id}.json")
        with open(site_json_path, "w", encoding="utf-8") as f:
            json.dump(site_documents, f, indent=2)

        return site_documents

    def crawl_all(self, target_ids: List[str] = None, max_pages_per_site: int = 5) -> List[Dict[str, Any]]:
        """Crawls all or selected Brillanz websites and updates raw_documents.json."""
        websites = self.load_target_websites()
        if target_ids:
            websites = [w for w in websites if w["id"] in target_ids]

        all_documents = []
        for site in websites:
            docs = self.crawl_site(site, max_pages=max_pages_per_site)
            all_documents.extend(docs)

        # Merge with existing documents for other sites if partial ingest
        if target_ids and os.path.exists(self.raw_documents_path):
            try:
                with open(self.raw_documents_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
                    # Keep documents from non-targeted sites
                    preserved = [d for d in existing if d.get("website_id") not in target_ids]
                    all_documents = preserved + all_documents
            except Exception as e:
                logger.error(f"Error merging raw documents: {e}")

        # Save to main raw_documents.json
        with open(self.raw_documents_path, "w", encoding="utf-8") as f:
            json.dump(all_documents, f, indent=2)

        logger.info(f"Crawl complete. Total documents saved: {len(all_documents)}")
        return all_documents
