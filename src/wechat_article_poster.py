# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
import requests
import json
import time
import os
import random

# ==============================================================================
#                 CONFIGURATION - REPLACE WITH YOUR OWN VALUES
# ==============================================================================
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.json")
# Load APP_ID and APP_SECRET from environment variables
APP_ID = os.environ.get("APP_ID")
APP_SECRET = os.environ.get("APP_SECRET")
if not APP_ID or not APP_SECRET:
    logging.error("Environment variables APP_ID and/or APP_SECRET are not set. Please set them before running the script.")
    exit(1)

# ==============================================================================
#                           API ENDPOINT DEFINITIONS
# ==============================================================================
BASE_URL = "https://api.weixin.qq.com/cgi-bin"
GET_TOKEN_URL = f"{BASE_URL}/token"
ADD_DRAFT_URL = f"{BASE_URL}/draft/add"


class WeChatArticlePoster:
    BASE_URL = "https://api.weixin.qq.com/cgi-bin"
    GET_TOKEN_URL = f"{BASE_URL}/token"
    UPLOAD_MATERIAL_URL = f"{BASE_URL}/material/add_material"
    ADD_DRAFT_URL = f"{BASE_URL}/draft/add"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None

    def get_random_image_media_id(self) -> str:
        """
        Fetches a list of image media from WeChat and returns a random media_id.
        """
        if not self.access_token:
            self.get_access_token()
        logging.info("Fetching list of image media from WeChat...")
        url = f"https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token={self.access_token}"
        payload = {
            "type": "image",
            "offset": 0,
            "count": 20
        }
        try:
            response = requests.post(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
            response.raise_for_status()
            data = response.json()
            if "item" in data and data["item"]:
                items = data["item"]
                chosen = random.choice(items)
                media_id = chosen["media_id"]
                logging.info(f"Selected media_id: {media_id}")
                return media_id
            else:
                raise Exception(f"No image media found: {data}")
        except Exception as e:
            raise Exception(f"Error fetching image media list: {e}")

    def get_access_token(self) -> str:
        params = {
            "grant_type": "client_credential",
            "appid": self.app_id,
            "secret": self.app_secret
        }
        logging.info("Fetching access token...")
        try:
            response = requests.get(self.GET_TOKEN_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if "access_token" in data:
                logging.info("Access token fetched successfully.")
                self.access_token = data["access_token"]
                return self.access_token
            else:
                raise Exception(f"Failed to get access token: {data}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching access token: {e}")

    def upload_image(self, image_path: str) -> str:
        if not self.access_token:
            self.get_access_token()
        logging.info(f"Uploading image from: {image_path}")
        url = f"{self.UPLOAD_MATERIAL_URL}?access_token={self.access_token}&type=image"
        try:
            with open(image_path, 'rb') as f:
                files = {'media': f}
                response = requests.post(url, files=files)
                response.raise_for_status()
                data = response.json()
                if "media_id" in data:
                    logging.info(f"Image uploaded successfully. media_id: {data['media_id']}")
                    return data["media_id"]
                else:
                    raise Exception(f"Failed to upload image: {data}")
        except Exception as e:
            raise Exception(f"Error uploading image: {e}")

    def create_article_draft(self, title: str, author: str, digest: str, content_html: str, thumb_media_id: str) -> str:
        if not self.access_token:
            self.get_access_token()
        logging.info("Creating article draft...")
        url = f"{self.ADD_DRAFT_URL}?access_token={self.access_token}"
        article = {
            "title": title,
            "thumb_media_id": thumb_media_id,
            "author": author,
            "digest": digest,
            "show_cover_pic": 1,
            "content": content_html
        }
        payload = {"articles": [article]}
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'), headers=headers)
            response.raise_for_status()
            data = response.json()
            if "media_id" in data:
                logging.info(f"Draft created successfully. Draft media_id: {data['media_id']}")
                return data["media_id"]
            else:
                raise Exception(f"Failed to create article draft: {data}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error creating article draft: {e}")

    def create_draft(self, title: str, author: str, digest: str, content_html: str) -> str:
        """
        External API: Create a draft article using a random existing image media_id.
        Returns the draft media_id.
        """
        self.get_access_token()
        time.sleep(1)
        thumb_media_id = self.get_random_image_media_id()
        time.sleep(1)
        draft_media_id = self.create_article_draft(title, author, digest, content_html, thumb_media_id)
        return draft_media_id

# Example usage
if __name__ == "__main__":
    import sys
    from bs4 import BeautifulSoup

    if len(sys.argv) < 2:
        logging.info("Usage: python wechat_article_poster.py <path_to_html_file>")
        sys.exit(1)

    html_path = sys.argv[1]
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract title from HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    title_tag = soup.find('title')
    article_title = title_tag.text.strip() if title_tag else "Untitled"

    article_author = "Gemini"
    article_digest = f"Auto-generated digest for: {article_title}"
    article_content_html = html_content

    poster = WeChatArticlePoster(APP_ID, APP_SECRET)
    try:
        draft_media_id = poster.create_draft(
            article_title,
            article_author,
            article_digest,
            article_content_html
        )
        logging.info(f"Draft created. media_id: {draft_media_id}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
