-- Create news_articles table
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source_name VARCHAR(100) NOT NULL,
    url TEXT NOT NULL UNIQUE,
    published_at TIMESTAMP,
    description TEXT,
    content TEXT,
    author VARCHAR(200),
    category VARCHAR(50),
    language VARCHAR(10),
    country VARCHAR(10),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON news_articles(published_at);
CREATE INDEX IF NOT EXISTS idx_news_articles_source_name ON news_articles(source_name);
CREATE INDEX IF NOT EXISTS idx_news_articles_category ON news_articles(category);
CREATE INDEX IF NOT EXISTS idx_news_articles_language ON news_articles(language);
CREATE INDEX IF NOT EXISTS idx_news_articles_country ON news_articles(country);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_news_articles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_news_articles_updated_at
    BEFORE UPDATE ON news_articles
    FOR EACH ROW
    EXECUTE FUNCTION update_news_articles_updated_at();

-- Add comments
COMMENT ON TABLE news_articles IS 'Stores news articles from various sources';
COMMENT ON COLUMN news_articles.title IS 'Article title';
COMMENT ON COLUMN news_articles.source_name IS 'Name of the news source';
COMMENT ON COLUMN news_articles.url IS 'URL of the article (unique)';
COMMENT ON COLUMN news_articles.published_at IS 'When the article was published';
COMMENT ON COLUMN news_articles.description IS 'Article description/summary';
COMMENT ON COLUMN news_articles.content IS 'Full article content if available';
COMMENT ON COLUMN news_articles.author IS 'Article author';
COMMENT ON COLUMN news_articles.category IS 'Article category';
COMMENT ON COLUMN news_articles.language IS 'Article language';
COMMENT ON COLUMN news_articles.country IS 'Country of origin';
COMMENT ON COLUMN news_articles.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN news_articles.updated_at IS 'Timestamp when record was last updated'; 