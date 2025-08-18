import os
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import requests
import xml.etree.ElementTree as ET
from datetime import datetime


class RssFetcher:
    def __init__(self, rss_url: str, base_dir: str):
        self.rss_url = rss_url
        self.base_dir = base_dir
        self.feed_name = self._get_feed_name_from_url(rss_url)
        self.save_dir = os.path.join(self.base_dir, self.feed_name)
        os.makedirs(self.save_dir, exist_ok=True)

    @staticmethod
    def _get_feed_name_from_url(rss_url: str) -> str:
        # Use domain and last path segment for uniqueness
        from urllib.parse import urlparse
        parsed = urlparse(rss_url)
        domain = parsed.netloc.replace('.', '_')
        path = parsed.path.rstrip('/').split('/')[-1]
        if path.endswith('.xml'):
            path = path[:-4]
        feed_name = f"{domain}__{path}" if path else domain
        return feed_name

    def fetch_latest(self):
        import bs4
        response = requests.get(self.rss_url)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        channel = root.find('channel')
        item = channel.find('item') if channel is not None else None
        if item is None:
            raise Exception('No news items found in RSS feed.')
        # Use guid if available, else link, else title
        guid = item.findtext('guid')
        link = item.findtext('link', default='')
        title = item.findtext('title', default='No Title')
        unique_id = guid or link or title

        # State file to track last fetched article
        state_file = os.path.join(self.save_dir, '.last_id')
        last_id = None
        if os.path.exists(state_file):
            with open(state_file, 'r', encoding='utf-8') as sf:
                last_id = sf.read().strip()

        if last_id == unique_id:
            return "no new article"

        pub_date = item.findtext('pubDate', default='')
        # Try to get full content from the web page
        content = None
        if link:
            try:
                page = requests.get(link)
                page.raise_for_status()
                soup = bs4.BeautifulSoup(page.content, 'html.parser')
                # Try to find the main article content
                # This may need to be customized for each site
                # For smol.ai, the main content is likely in <article> or <main>
                main = soup.find('article') or soup.find('main')
                if main:
                    content = str(main)
                else:
                    # Fallback: get all <p> tags
                    paragraphs = soup.find_all('p')
                    content = '\n'.join([str(p) for p in paragraphs])
            except Exception as e:
                # Fallback to RSS content if web fetch fails
                content = None

        if not content:
            # <content:encoded> is in a namespace, so use find with namespace
            content_encoded = item.find('{http://purl.org/rss/1.0/modules/content/}encoded')
            if content_encoded is not None and content_encoded.text:
                content = content_encoded.text.strip()
            else:
                # Try <summary>
                summary = item.findtext('summary')
                if summary:
                    content = summary.strip()
                else:
                    # Fallback to <description>
                    description = item.findtext('description', default='')
                    content = description.strip()

        # Save as file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(self.save_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Title: {title}\n")
            f.write(f"Link: {link}\n")
            f.write(f"Published: {pub_date}\n")
            f.write(f"Content: {content}\n")

        # Update state file
        with open(state_file, 'w', encoding='utf-8') as sf:
            sf.write(unique_id)

        logging.info(f"Saved latest news to {filepath}")
        return filepath

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Example usage
if __name__ == "__main__":
    import json
    config_path = os.path.join(os.path.dirname(__file__), '../config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    rss_url = config.get('RSS_URL')
    base_dir = os.path.join(os.path.dirname(__file__), '../content/rss')
    fetcher = RssFetcher(rss_url, base_dir)
    file_path = fetcher.fetch_latest()
    logging.info(f"Saved latest news to {file_path}")
