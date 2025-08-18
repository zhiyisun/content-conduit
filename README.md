# RSS-LLM-WeChat

RSS-LLM-WeChat is an automated content aggregation and publishing system that fetches the latest content from RSS sources, generates customized articles using large language models (LLM), and automatically publishes them to platforms like WeChat Official Accounts.

## Features

- **RSS Content Fetching**: Automatically fetches latest articles from specified RSS sources
- **Intelligent Content Generation**: Uses large language models (Gemini) to generate customized content based on predefined prompts
- **Multi-platform Publishing**: Supports publishing generated content to WeChat Official Accounts, Xiaohongshu (Little Red Book), and other platforms
- **Automated Workflow**: One-click completion of the entire process from content fetching to publishing
- **Highly Configurable**: Customizable RSS sources, generation prompts, and publishing parameters through configuration files

## Workflow

1. Fetch latest articles from configured RSS sources
2. Extract article content and save locally
3. Generate customized content using Gemini based on predefined prompts
4. Publish generated content to platforms like WeChat Official Accounts

## Requirements

- Python 3.x
- requests
- beautifulsoup4

## Installation

1. Clone the project:
   ```
   git clone <repository-url>
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the `config.json` file:
   ```json
   {
       "APP_ID": "your-wechat-app-id",
       "APP_SECRET": "your-wechat-app-secret",
       "RSS_URL": "https://your-rss-source.com/rss.xml"
   }
   ```

4. Modify the prompt configurations in `content_map.json` as needed

## Usage

Run the main program:
```
python main.py
```

Force content regeneration (even without new articles):
```
python main.py --force-gen
```

## Configuration

### config.json
- `APP_ID`: WeChat Official Account App ID
- `APP_SECRET`: WeChat Official Account App Secret
- `RSS_URL`: RSS source URL

### content_map.json
Defines content generation rules and prompts for different platforms:
- `wechat`: WeChat Official Account content generation rules
- `xhs`: Xiaohongshu (Little Red Book) content generation rules

Each platform configuration includes:
- `folder`: Content storage directory
- `prompt`: Content generation prompt list

## License

MIT License