import os
import sys
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import json
from src.fetchers.rss_fetcher import RssFetcher
from src.content_config import ContentConfig
from src.ai_reporter import AIReporter
from src.wechat_article_poster import WeChatArticlePoster, APP_ID, APP_SECRET

# Parse command-line arguments
import argparse
parser = argparse.ArgumentParser(description="Run news pipeline.")
parser.add_argument('-f', '--force-gen', action='store_true', help='Force generate article even if already generated, using already fetched news.')
args = parser.parse_args()


# Step 1: Fetch latest news (only once, not per logical_name)
config_path = os.path.join(os.path.dirname(__file__), 'content_map.json')
content_config = ContentConfig(config_path)

# Only RSS for now, can extend for other fetchers
base_dir = os.path.join(os.path.dirname(__file__), 'content/rss')
# Find RSS URL from config.json
with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r', encoding='utf-8') as f:
    rss_url = (json.load(f)).get('RSS_URL')
fetcher = RssFetcher(rss_url, base_dir)

# Always fetch latest news, do not remove .last_id for force_gen


news_file = fetcher.fetch_latest()
if news_file == "no new article" and not args.force_gen:
    logging.info("No new article found.")
    sys.exit(0)
elif news_file != "no new article":
    logging.info(f"Fetched latest news: {news_file}")
else:
    logging.info("No new article found, but force_gen is set. Will use last_id for content generation.")

# Step 2: Generate content for each logical_name defined in content_map.json

for logical_name, item in content_config.all_items():
    reporter = AIReporter(config_path)
    html_folder = os.path.join(os.path.dirname(__file__), 'content/html', logical_name)
    os.makedirs(html_folder, exist_ok=True)

    # Get folder from content_map.json
    content_folder = item['folder']
    last_id_path = os.path.join(os.path.dirname(__file__), content_folder, '.last_id')
    if not os.path.exists(last_id_path):
        logging.info(f"No .last_id file found for {logical_name}. Skipping.")
        continue
    with open(last_id_path, 'r', encoding='utf-8') as f:
        last_id = f.read().strip()
    # Find the latest .txt file matching last_id
    rss_folder = os.path.join(os.path.dirname(__file__), content_folder)
    txt_files = [f for f in os.listdir(rss_folder) if f.endswith('.txt')]
    found_file = None
    for txt_file in sorted(txt_files, reverse=True):
        txt_path = os.path.join(rss_folder, txt_file)
        with open(txt_path, 'r', encoding='utf-8') as tf:
            if last_id in tf.read():
                found_file = txt_path
                break
    if not found_file:
        logging.info(f"No matching article found for last_id in {logical_name}. Skipping.")
        continue

    # Generate unique HTML filename by appending logical_name before .html
    base_html_name = os.path.basename(found_file).replace('.txt', f'_{logical_name}.html')
    html_path = os.path.join(html_folder, base_html_name)

    # If not force_gen, skip content generation if HTML already exists
    if not args.force_gen and os.path.exists(html_path):
        logging.info(f"Content for {logical_name} already generated: {html_path}")
        continue

    # Use the new signature: (logical_name, article_filepath, html_filepath)
    try:
        result = reporter.generate_report(logical_name, found_file, html_path)
        if not result or (isinstance(result, str) and result.strip().lower().startswith("error")):
            logging.error(f"Failed to generate HTML for '{logical_name}' using {found_file}")
            logging.error(f"AI tool response: {result}")
            sys.exit(1)
        
        # Check if the HTML file was actually created
        if not os.path.exists(html_path):
            logging.error(f"AI tool claimed success but HTML file was not created: {html_path}")
            logging.error(f"AI tool response: {result}")
            sys.exit(1)
            
        logging.info(f"Generated HTML file: {html_path}")
    except Exception as e:
        logging.error(f"Exception during report generation for '{logical_name}': {e}")
        sys.exit(1)

    # Step 3: Publish to WeChat (only for 'wechat_news' logical_name)
    if logical_name in ['wechat', 'xhs']:
        poster = WeChatArticlePoster(APP_ID, APP_SECRET)
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        title_tag = soup.find('title')
        article_title = title_tag.text.strip() if title_tag else "Untitled"
        if title_tag:
            title_tag.decompose()  # Remove the <title> tag from soup
        html_content_no_title = str(soup)
        # Use the tool name from config.json for author
        with open(os.path.join(os.path.dirname(__file__), 'config.json'), 'r', encoding='utf-8') as cf:
            config_data = json.load(cf)
        article_author = config_data.get("TOOL", "AI")
        article_digest = f"Auto-generated digest for: {article_title}"
        try:
            draft_media_id = poster.create_draft(
                article_title,
                article_author,
                article_digest,
                html_content_no_title
            )
            logging.info(f"Draft created and published to WeChat. media_id: {draft_media_id}")
        except Exception as e:
            logging.error(f"Error publishing to WeChat: {e}")
