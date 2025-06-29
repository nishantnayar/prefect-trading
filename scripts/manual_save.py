from src.data.sources.configurable_websocket import save_redis_data_to_postgres

if __name__ == "__main__":
    print("Saving Redis data to PostgreSQL...")
    try:
        save_redis_data_to_postgres()
        print("Manual save complete.")
    except Exception as e:
        print(f"Error: {e}") 