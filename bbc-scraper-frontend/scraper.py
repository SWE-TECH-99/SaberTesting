import asyncio
from dotenv import load_dotenv
import os
import aiohttp
from bs4 import BeautifulSoup
import asyncpg
from urllib.parse import urljoin
import logging
import sys

# Load environment variables from .env.local file
load_dotenv('.env.local')

# Configure logging to display info level messages with timestamps
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('scraper.log')  # Log to a file for long-term tracking
    ]
)
logger = logging.getLogger(__name__)

# Retrieve PostgreSQL connection details from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logger.error("DATABASE_URL is not set in the environment variables.")
    sys.exit(1)

# Semaphore to control concurrency
sem = asyncio.Semaphore(10)  # Adjust concurrency here

# Asynchronous function to create the articles table
async def create_table():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id SERIAL PRIMARY KEY,
                headline TEXT NOT NULL,
                url TEXT NOT NULL,
                UNIQUE (headline, url)
            )
        ''')
        logger.info("Articles table ensured in the database.")
    except Exception as e:
        logger.error(f"Error creating articles table: {e}")
    finally:
        await conn.close()

# Asynchronous function to fetch HTML content from a URL with retries using exponential backoff
async def fetch(session, url, retries=3):
    async with sem:  # Control the number of concurrent requests
        for attempt in range(1, retries + 1):
            try:
                async with session.get(url, timeout=10) as response:
                    response.raise_for_status()
                    logger.debug(f"Successfully fetched URL: {url} - Status Code: {response.status}")
                    return await response.text()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                logger.warning(f"Attempt {attempt} - Error fetching {url}: {e}")
                if attempt < retries:
                    backoff = 2 ** attempt
                    logger.info(f"Retrying in {backoff} seconds...")
                    await asyncio.sleep(backoff)
                else:
                    logger.error(f"Failed to fetch {url} after {retries} attempts.")
                    return None

# Asynchronous function to scrape BBC News headlines
async def scrape_bbc_news(max_articles=50):
    base_url = 'https://www.bbc.co.uk/news'  # BBC News homepage
    articles = []

    async with aiohttp.ClientSession() as session:
        logger.info(f"Fetching BBC News homepage: {base_url}")
        html = await fetch(session, base_url)
        if not html:
            logger.error("Failed to retrieve BBC News homepage. Exiting scraper.")
            return

        # Error handling for HTML parsing
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            logger.error(f"Error parsing HTML content: {e}")
            return

        # Select only news-related articles (e.g., articles with '/news/' in their href)
        for article_tag in soup.select('a[href*="/news/"]'):
            href = article_tag.get('href')
            if not href:
                continue

            article_url = urljoin(base_url, href)
            headline = article_tag.get_text().strip()

            # Filter out irrelevant or short headlines
            if headline and len(headline) > 5 and 'news' in article_url:
                if headline not in ["More menu", "Search BBC", "Close menu"]:
                    articles.append((headline, article_url))
                    logger.info(f"Scraped headline: {headline} | {article_url}")

            # Limit the number of articles
            if len(articles) >= max_articles:
                logger.info(f"Reached max_articles limit: {max_articles}")
                break

    if articles:
        await save_articles(articles)
        logger.info(f"Total articles scraped and saved: {len(articles)}")
    else:
        logger.warning("No articles were scraped.")

# Asynchronous function to save the list of articles to the database
async def save_articles(articles):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        insert_query = '''
            INSERT INTO articles (headline, url)
            VALUES ($1, $2)
            ON CONFLICT (headline, url) DO NOTHING
        '''
        await conn.executemany(insert_query, articles)
        logger.info(f"Inserted {len(articles)} new articles into the database.")
    except Exception as e:
        logger.error(f"Error saving articles to the database: {e}")
    finally:
        await conn.close()

# Gracefully close the database connection pool on exit
async def close_db():
    try:
        await asyncpg.pool.close()
        logger.info("PostgreSQL connection pool closed.")
    except Exception as e:
        logger.error(f"Error closing PostgreSQL connection pool: {e}")

# Main entry point of the script
if __name__ == '__main__':
    try:
        asyncio.run(create_table())
        # You can set MAX_ARTICLES in your .env.local or default to 50
        MAX_ARTICLES = int(os.getenv("MAX_ARTICLES", 50))
        asyncio.run(scrape_bbc_news(max_articles=MAX_ARTICLES))
    except KeyboardInterrupt:
        logger.info("Script interrupted by user.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
    finally:
        asyncio.run(close_db())
