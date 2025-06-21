from newsapi import NewsApiClient
from datetime import datetime
from loguru import logger
from prefect.blocks.system import Secret
from src.database.database_connectivity import DatabaseConnectivity


class NewsLoader:
    def __init__(self):
        self.db = DatabaseConnectivity()
        try:
            # Load API key from Prefect secrets
            api_key = Secret.load("newsapi").get()
            self.newsapi = NewsApiClient(api_key=api_key)
            logger.info("Successfully initialized NewsAPI client")
        except Exception as e:
            logger.error(f"Failed to initialize NewsAPI client: {str(e)}")
            raise

    def fetch_and_store_news(self, query='stock market', category='business', language='en', country='us'):
        """
        Fetch news articles and store them in the database.
        
        Args:
            query (str): Search query for news articles
            category (str): News category
            language (str): Language of articles
            country (str): Country of origin
        """
        try:
            # Fetch top headlines
            headlines = self.newsapi.get_top_headlines(
                q=query,
                category=category,
                language=language,
                country=country
            )

            # Store articles in database
            with self.db.get_session() as cursor:
                for article in headlines['articles']:
                    # Convert publishedAt string to timestamp
                    published_at = None
                    if article.get('publishedAt'):
                        try:
                            published_at = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                        except ValueError:
                            logger.warning(f"Could not parse publishedAt date: {article['publishedAt']}")

                    # Insert article into database
                    insert_query = """
                        INSERT INTO news_articles 
                        (title, source_name, url, published_at, description, content, author, category, language, country)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (url) DO UPDATE SET
                        title = EXCLUDED.title,
                        source_name = EXCLUDED.source_name,
                        published_at = EXCLUDED.published_at,
                        description = EXCLUDED.description,
                        content = EXCLUDED.content,
                        author = EXCLUDED.author,
                        category = EXCLUDED.category,
                        language = EXCLUDED.language,
                        country = EXCLUDED.country
                    """

                    cursor.execute(insert_query, (
                        article.get('title'),
                        article.get('source', {}).get('name'),
                        article.get('url'),
                        published_at,
                        article.get('description'),
                        article.get('content'),
                        article.get('author'),
                        category,
                        language,
                        country
                    ))

            logger.info(f"Successfully stored {len(headlines['articles'])} news articles")
            return headlines['articles']

        except Exception as e:
            logger.error(f"Error fetching and storing news: {str(e)}")
            raise


def main():
    """Main function to run the news loader."""
    try:
        news_loader = NewsLoader()
        news_loader.fetch_and_store_news()
    except Exception as e:
        logger.error(f"Failed to run news loader: {str(e)}")
        raise


if __name__ == "__main__":
    main()
