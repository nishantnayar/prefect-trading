# Setup and Configuration Guide

## Environment Setup

### Prerequisites
1. Python 3.9 or higher
2. PostgreSQL 12 or higher
3. Git
4. Access to Alpaca API
5. Access to Yahoo Finance API

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone [repository-url]
   cd prefect-trading
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**
   Create a `.env` file in the project root:
   ```env
   # Database Configuration
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=trading_db
   DB_USER=your_username
   DB_PASSWORD=your_password

   # Alpaca Configuration
   ALPACA_API_KEY=your_api_key
   ALPACA_SECRET_KEY=your_secret_key
   ALPACA_BASE_URL=https://paper-api.alpaca.markets

   # Prefect Configuration
   PREFECT_API_URL=http://localhost:4200/api
   ```

## Prefect Setup

1. **Install Prefect**
   ```bash
   pip install prefect
   ```

2. **Start Prefect Server**
   ```bash
   prefect server start
   ```

3. **Configure Prefect**
   ```bash
   prefect config set PREFECT_API_URL=http://localhost:4200/api
   ```

4. **Create Prefect Blocks**
   ```python
   from prefect.blocks.system import String
   
   # Create database connection block
   db_connection = String(value="postgresql://user:password@localhost:5432/dbname")
   db_connection.save(name="database-connection")
   
   # Create Alpaca credentials block
   alpaca_key = String(value="your_api_key")
   alpaca_key.save(name="alpaca-api-key")
   ```

## Database Setup

1. **Create Database**
   ```sql
   CREATE DATABASE trading_db;
   ```

2. **Initialize Schema**
   ```bash
   python src/database/init_db.py
   ```

## Configuration Files

### 1. Prefect Configuration (`prefect.yaml`)
```yaml
name: trading-system
description: Trading system workflows
```

### 2. Database Configuration
Located in `config/database.yaml`:
```yaml
host: localhost
port: 5432
database: trading_db
user: your_username
password: your_password
```

### 3. API Configuration
Located in `config/api.yaml`:
```yaml
alpaca:
  api_key: your_api_key
  secret_key: your_secret_key
  base_url: https://paper-api.alpaca.markets
```

## Running the System

1. **Start Prefect Server**
   ```bash
   prefect server start
   ```

2. **Deploy Workflows**
   ```bash
   prefect deploy
   ```

3. **Start Workflows**
   ```bash
   prefect deployment run "Trading System/hourly-process"
   prefect deployment run "Trading System/eod-process"
   ```

## Monitoring

1. **Access Prefect UI**
   - Open `http://localhost:4200` in your browser
   - Monitor workflow runs and task execution

2. **View Logs**
   ```bash
   prefect logs
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database credentials
   - Ensure database exists

2. **API Connection Issues**
   - Verify API keys are correct
   - Check network connectivity
   - Validate API endpoints

3. **Prefect Server Issues**
   - Ensure Prefect server is running
   - Check Prefect configuration
   - Verify workflow deployments

### Support

For additional support:
1. Check the [GitHub Issues](https://github.com/your-repo/issues)
2. Review the [Prefect Documentation](https://docs.prefect.io/)
3. Contact the development team 