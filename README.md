
# Content Conduit

Content Conduit is an automated content aggregation and publishing system that fetches the latest content from RSS sources, generates customized articles using large language models (LLM, e.g., Gemini), and publishes them to platforms such as WeChat Official Accounts and Xiaohongshu.


## Features

- **RSS Content Fetching**: Automatically fetches latest articles from configured RSS sources (see `src/fetchers/rss_fetcher.py`)
- **Intelligent Content Generation**: Uses large language models (Gemini) to generate customized content based on prompts defined in `content_map.json`
- **Multi-platform Publishing**: Supports publishing generated content to WeChat Official Accounts and RedNote (XHS, Xiaohongshu)
- **Automated Workflow**: End-to-end automation from fetching to publishing with a single command
- **Configurable**: RSS sources, prompts, and publishing parameters are managed via `config.json` and `content_map.json`


## Directory Structure

```
config.json                # Main configuration (API keys, RSS URLs)
content_map.json           # Content generation rules and prompts
main.py                    # Entry point for running the workflow
requirements.txt           # Python dependencies
src/
   ai_reporter.py           # LLM-based content generation
   content_config.py        # Configuration loader
   content_map.py           # Content mapping logic
   wechat_article_poster.py # WeChat publishing logic
   fetchers/
      rss_fetcher.py         # RSS fetching logic
content/
   html/
      wechat/                # Generated WeChat HTML articles
      xhs/                   # Generated RedNote (XHS, Xiaohongshu) HTML articles
   rss/
      news_smol_ai__rss/     # Fetched RSS article text
```

## Workflow

1. Fetch latest articles from RSS sources (using `src/fetchers/rss_fetcher.py`)
2. Extract and save article content locally (in `content/rss/`)
3. Generate customized content using Gemini and prompts from `content_map.json`
4. Save generated articles to `content/html/` (by platform)
5. Publish generated content to WeChat Official Accounts (via `src/wechat_article_poster.py`).
6. For RedNote (XHS): Manually copy the generated content from the WeChat draft box to RedNote, as RedNote does not provide a public API for publishing articles.


## Requirements

- Python 3.10+
- requests
- beautifulsoup4


## Installation

1. Clone the project:
   ```zsh
   git clone <repository-url>
   cd content-conduit
   ```

2. Install dependencies:
   ```zsh
   pip install -r requirements.txt
   ```


3. Configure environment variables and `config.json`:

    Many sensitive or platform-specific settings are now managed via environment variables. Set these in your shell or `.env` file before running the project:

    - `APP_ID`: WeChat Official Account App ID
    - `APP_SECRET`: WeChat Official Account App Secret


    Example (Linux/zsh):
    ```zsh
    export APP_ID="your-wechat-app-id"
    export APP_SECRET="your-wechat-app-secret"
    ```

    The `config.json` now contains only non-sensitive, runtime configuration, e.g.:
    ```json
    {
       "RSS_URL": "https://news.smol.ai/rss.xml",
       "TOOL": "qwen",
       "USE_PROXY": false,
       "PROXY_HOST": "raspberrypi.local",
       "PROXY_PORT": 7893
    }
    ```

4. Edit `content_map.json` to customize prompts and platform settings as needed.


## Usage

Run the main workflow:
```zsh
python main.py
```

Force content regeneration (ignores new article check):
```zsh
python main.py --force-gen
```



## Configuration

### Environment Variables
- `APP_ID`: WeChat Official Account App ID
- `APP_SECRET`: WeChat Official Account App Secret

Set required variables in your shell or `.env` file before running the project.

### config.json
- `RSS_URL`: RSS source URL
- `TOOL`: LLM tool to use (e.g., "qwen", "gemini")
- `USE_PROXY`: Whether to use a proxy for requests
- `PROXY_HOST`: Proxy host address
- `PROXY_PORT`: Proxy port

### content_map.json
Defines content generation rules and prompts for each platform:
- `wechat`: WeChat Official Account rules
- `xhs`: RedNote (XHS, Xiaohongshu) rules

Each platform configuration includes:
- `folder`: Content storage directory
- `prompt`: List of prompts for LLM content generation


## License

MIT License