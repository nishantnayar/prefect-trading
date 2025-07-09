-- =====================================================
-- CONSOLIDATED INITIAL SCHEMA MIGRATION
-- Combines migrations 001-007 into a single script
-- =====================================================

-- =====================================================
-- 1. CREATE LOGS TABLE
-- =====================================================
-- Drop existing table if it exists
DROP TABLE IF EXISTS logs;

-- Create logs table
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    level VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    module VARCHAR(100) NOT NULL,
    function VARCHAR(100) NOT NULL,
    line_number INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_logs_timestamp ON logs(timestamp);
CREATE INDEX idx_logs_level ON logs(level);
CREATE INDEX idx_logs_module ON logs(module);

-- Add comment to table
COMMENT ON TABLE logs IS 'Application logs storage table';

-- Add comments to columns
COMMENT ON COLUMN logs.id IS 'Primary key';
COMMENT ON COLUMN logs.timestamp IS 'Timestamp of the log entry';
COMMENT ON COLUMN logs.level IS 'Log level (INFO, ERROR, etc.)';
COMMENT ON COLUMN logs.message IS 'Log message content';
COMMENT ON COLUMN logs.module IS 'Module name where log was generated';
COMMENT ON COLUMN logs.function IS 'Function name where log was generated';
COMMENT ON COLUMN logs.line_number IS 'Line number where log was generated';
COMMENT ON COLUMN logs.created_at IS 'Timestamp when log was stored in database';

-- =====================================================
-- 2. CREATE MARKET DATA TABLE
-- =====================================================
-- Create market_data table
CREATE TABLE IF NOT EXISTS market_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume INTEGER NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_market_data_symbol ON market_data(symbol);
CREATE INDEX IF NOT EXISTS idx_market_data_timestamp ON market_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data(symbol, timestamp);

-- =====================================================
-- 3. CREATE SYMBOLS TABLE
-- =====================================================
-- Create symbols table
CREATE TABLE IF NOT EXISTS symbols (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL UNIQUE,
    name VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_symbols_symbol ON symbols(symbol);
CREATE INDEX IF NOT EXISTS idx_symbols_is_active ON symbols(is_active);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_symbols_updated_at
    BEFORE UPDATE ON symbols
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- 4. ADD CONSTRAINTS TO MARKET DATA
-- =====================================================
-- Add unique constraint to market_data table
ALTER TABLE market_data
ADD CONSTRAINT uix_market_data_symbol_timestamp 
UNIQUE (symbol, timestamp);

-- Create index to support the unique constraint
CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp 
ON market_data (symbol, timestamp);

-- =====================================================
-- 5. CREATE YAHOO COMPANY INFO TABLE
-- =====================================================
-- Create yahoo_company_info table
CREATE TABLE IF NOT EXISTS yahoo_company_info (
    symbol VARCHAR(10) PRIMARY KEY,
    address1 TEXT,
    address2 TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip VARCHAR(20),
    country VARCHAR(100),
    phone VARCHAR(50),
    fax VARCHAR(50),
    website TEXT,
    industry VARCHAR(100),
    "industryKey" VARCHAR(100),
    "industryDisp" VARCHAR(100),
    "industrySymbol" VARCHAR(50),
    sector VARCHAR(100),
    "sectorKey" VARCHAR(100),
    "sectorDisp" VARCHAR(100),
    "longBusinessSummary" TEXT,
    "fullTimeEmployees" INTEGER,
    "auditRisk" INTEGER,
    "boardRisk" INTEGER,
    "compensationRisk" INTEGER,
    "shareHolderRightsRisk" INTEGER,
    "overallRisk" INTEGER,
    "governanceEpochDate" BIGINT,
    "compensationAsOfEpochDate" BIGINT,
    "irWebsite" TEXT,
    "executiveTeam" TEXT,
    "maxAge" INTEGER,
    "priceHint" INTEGER,
    "previousClose" FLOAT,
    open FLOAT,
    "dayLow" FLOAT,
    "dayHigh" FLOAT,
    "regularMarketPreviousClose" FLOAT,
    "regularMarketOpen" FLOAT,
    "regularMarketDayLow" FLOAT,
    "regularMarketDayHigh" FLOAT,
    "dividendRate" FLOAT,
    "dividendYield" FLOAT,
    "exDividendDate" BIGINT,
    "payoutRatio" FLOAT,
    "fiveYearAvgDividendYield" FLOAT,
    beta FLOAT,
    "trailingPE" FLOAT,
    "forwardPE" FLOAT,
    volume BIGINT,
    "regularMarketVolume" BIGINT,
    "averageVolume" BIGINT,
    "averageVolume10days" BIGINT,
    "averageDailyVolume10Day" BIGINT,
    bid FLOAT,
    ask FLOAT,
    "bidSize" INTEGER,
    "askSize" INTEGER,
    "marketCap" BIGINT,
    "fiftyTwoWeekLow" FLOAT,
    "fiftyTwoWeekHigh" FLOAT,
    "priceToSalesTrailing12Months" FLOAT,
    "fiftyDayAverage" FLOAT,
    "twoHundredDayAverage" FLOAT,
    "trailingAnnualDividendRate" FLOAT,
    "trailingAnnualDividendYield" FLOAT,
    currency VARCHAR(10),
    tradeable BOOLEAN,
    "enterpriseValue" BIGINT,
    "profitMargins" FLOAT,
    "floatShares" BIGINT,
    "sharesOutstanding" BIGINT,
    "sharesShort" BIGINT,
    "sharesShortPriorMonth" BIGINT,
    "sharesShortPreviousMonthDate" BIGINT,
    "dateShortInterest" BIGINT,
    "sharesPercentSharesOut" FLOAT,
    "heldPercentInsiders" FLOAT,
    "heldPercentInstitutions" FLOAT,
    "shortRatio" FLOAT,
    "shortPercentOfFloat" FLOAT,
    "impliedSharesOutstanding" BIGINT,
    "bookValue" FLOAT,
    "priceToBook" FLOAT,
    "lastFiscalYearEnd" BIGINT,
    "nextFiscalYearEnd" BIGINT,
    "mostRecentQuarter" BIGINT,
    "earningsQuarterlyGrowth" FLOAT,
    "netIncomeToCommon" BIGINT,
    "trailingEps" FLOAT,
    "forwardEps" FLOAT,
    "lastSplitFactor" VARCHAR(50),
    "lastSplitDate" BIGINT,
    "enterpriseToRevenue" FLOAT,
    "enterpriseToEbitda" FLOAT,
    "52WeekChange" FLOAT,
    "SandP52WeekChange" FLOAT,
    "lastDividendValue" FLOAT,
    "lastDividendDate" BIGINT,
    "quoteType" VARCHAR(50),
    "currentPrice" FLOAT,
    "targetHighPrice" FLOAT,
    "targetLowPrice" FLOAT,
    "targetMeanPrice" FLOAT,
    "targetMedianPrice" FLOAT,
    "recommendationMean" FLOAT,
    "recommendationKey" VARCHAR(50),
    "numberOfAnalystOpinions" INTEGER,
    "totalCash" BIGINT,
    "totalCashPerShare" FLOAT,
    ebitda BIGINT,
    "totalDebt" BIGINT,
    "quickRatio" FLOAT,
    "currentRatio" FLOAT,
    "totalRevenue" BIGINT,
    "debtToEquity" FLOAT,
    "revenuePerShare" FLOAT,
    "returnOnAssets" FLOAT,
    "returnOnEquity" FLOAT,
    "grossProfits" BIGINT,
    "freeCashflow" BIGINT,
    "operatingCashflow" BIGINT,
    "earningsGrowth" FLOAT,
    "revenueGrowth" FLOAT,
    "grossMargins" FLOAT,
    "ebitdaMargins" FLOAT,
    "operatingMargins" FLOAT,
    "financialCurrency" VARCHAR(10),
    language VARCHAR(10),
    region VARCHAR(50),
    "typeDisp" VARCHAR(50),
    "quoteSourceName" VARCHAR(50),
    triggerable BOOLEAN,
    "customPriceAlertConfidence" VARCHAR(50),
    exchange VARCHAR(50),
    "messageBoardId" VARCHAR(50),
    "exchangeTimezoneName" VARCHAR(100),
    "exchangeTimezoneShortName" VARCHAR(10),
    "gmtOffSetMilliseconds" BIGINT,
    market VARCHAR(50),
    "esgPopulated" BOOLEAN,
    "regularMarketChangePercent" FLOAT,
    "regularMarketPrice" FLOAT,
    "marketState" VARCHAR(50),
    "shortName" VARCHAR(100),
    "longName" VARCHAR(100),
    "corporateActions" TEXT,
    "postMarketTime" BIGINT,
    "regularMarketTime" BIGINT,
    "hasPrePostMarketData" BOOLEAN,
    "firstTradeDateMilliseconds" BIGINT,
    "postMarketChangePercent" FLOAT,
    "postMarketPrice" FLOAT,
    "postMarketChange" FLOAT,
    "regularMarketChange" FLOAT,
    "regularMarketDayRange" VARCHAR(50),
    "fullExchangeName" VARCHAR(50),
    "averageDailyVolume3Month" BIGINT,
    "fiftyTwoWeekLowChange" FLOAT,
    "fiftyTwoWeekLowChangePercent" FLOAT,
    "fiftyTwoWeekRange" VARCHAR(50),
    "fiftyTwoWeekHighChange" FLOAT,
    "fiftyTwoWeekHighChangePercent" FLOAT,
    "fiftyTwoWeekChangePercent" FLOAT,
    "dividendDate" BIGINT,
    "earningsTimestamp" BIGINT,
    "earningsTimestampStart" BIGINT,
    "earningsTimestampEnd" BIGINT,
    "earningsCallTimestampStart" BIGINT,
    "earningsCallTimestampEnd" BIGINT,
    "isEarningsDateEstimate" BOOLEAN,
    "epsTrailingTwelveMonths" FLOAT,
    "epsForward" FLOAT,
    "epsCurrentYear" FLOAT,
    "priceEpsCurrentYear" FLOAT,
    "fiftyDayAverageChange" FLOAT,
    "fiftyDayAverageChangePercent" FLOAT,
    "twoHundredDayAverageChange" FLOAT,
    "twoHundredDayAverageChangePercent" FLOAT,
    "sourceInterval" INTEGER,
    "exchangeDataDelayedBy" INTEGER,
    "averageAnalystRating" VARCHAR(50),
    "cryptoTradeable" BOOLEAN,
    "displayName" VARCHAR(100),
    "trailingPegRatio" FLOAT,
    "ipoExpectedDate" DATE,
    "prevName" VARCHAR(100),
    "nameChangeDate" DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_symbol FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_yahoo_company_info_symbol ON yahoo_company_info(symbol);
CREATE INDEX IF NOT EXISTS idx_yahoo_company_info_industry ON yahoo_company_info(industry);
CREATE INDEX IF NOT EXISTS idx_yahoo_company_info_sector ON yahoo_company_info(sector);
CREATE INDEX IF NOT EXISTS idx_yahoo_company_info_market_cap ON yahoo_company_info("marketCap");
CREATE INDEX IF NOT EXISTS idx_yahoo_company_info_updated_at ON yahoo_company_info(updated_at);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_yahoo_company_info_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_yahoo_company_info_updated_at
    BEFORE UPDATE ON yahoo_company_info
    FOR EACH ROW
    EXECUTE FUNCTION update_yahoo_company_info_updated_at();

-- Add comments
COMMENT ON TABLE yahoo_company_info IS 'Stores company information from Yahoo Finance';
COMMENT ON COLUMN yahoo_company_info.symbol IS 'Stock symbol (foreign key to symbols table)';
COMMENT ON COLUMN yahoo_company_info.industry IS 'Company industry';
COMMENT ON COLUMN yahoo_company_info.sector IS 'Company sector';
COMMENT ON COLUMN yahoo_company_info."longName" IS 'Full company name';
COMMENT ON COLUMN yahoo_company_info."industrySymbol" IS 'Industry symbol identifier';
COMMENT ON COLUMN yahoo_company_info.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN yahoo_company_info.updated_at IS 'Timestamp when record was last updated';

-- =====================================================
-- 6. CREATE YAHOO COMPANY OFFICERS TABLE
-- =====================================================
-- Create yahoo_company_officers table
CREATE TABLE IF NOT EXISTS yahoo_company_officers (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    name VARCHAR(200),
    title VARCHAR(200),
    age INTEGER,
    year_born INTEGER,
    fiscal_year INTEGER,
    total_pay BIGINT,
    exercised_value BIGINT,
    unexercised_value BIGINT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_symbol FOREIGN KEY (symbol) REFERENCES symbols(symbol) ON DELETE CASCADE
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_yahoo_company_officers_symbol ON yahoo_company_officers(symbol);
CREATE INDEX IF NOT EXISTS idx_yahoo_company_officers_name ON yahoo_company_officers(name);
CREATE INDEX IF NOT EXISTS idx_yahoo_company_officers_title ON yahoo_company_officers(title);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_yahoo_company_officers_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_yahoo_company_officers_updated_at
    BEFORE UPDATE ON yahoo_company_officers
    FOR EACH ROW
    EXECUTE FUNCTION update_yahoo_company_officers_updated_at();

-- Add comments
COMMENT ON TABLE yahoo_company_officers IS 'Stores company officers information from Yahoo Finance';
COMMENT ON COLUMN yahoo_company_officers.id IS 'Primary key';
COMMENT ON COLUMN yahoo_company_officers.symbol IS 'Stock symbol (foreign key to symbols table)';
COMMENT ON COLUMN yahoo_company_officers.name IS 'Officer name';
COMMENT ON COLUMN yahoo_company_officers.title IS 'Officer title/position';
COMMENT ON COLUMN yahoo_company_officers.age IS 'Officer age';
COMMENT ON COLUMN yahoo_company_officers.year_born IS 'Year the officer was born';
COMMENT ON COLUMN yahoo_company_officers.fiscal_year IS 'Fiscal year of the compensation data';
COMMENT ON COLUMN yahoo_company_officers.total_pay IS 'Total compensation';
COMMENT ON COLUMN yahoo_company_officers.exercised_value IS 'Value of exercised stock options';
COMMENT ON COLUMN yahoo_company_officers.unexercised_value IS 'Value of unexercised stock options';
COMMENT ON COLUMN yahoo_company_officers.created_at IS 'Timestamp when record was created';
COMMENT ON COLUMN yahoo_company_officers.updated_at IS 'Timestamp when record was last updated';

-- =====================================================
-- 7. CREATE NEWS ARTICLES TABLE
-- =====================================================
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