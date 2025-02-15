#!/usr/bin/env python
import os
import sys
import psycopg2
from urllib.parse import urlparse

def create_database(db_uri):
    # Parse the DATABASE_URL URI.
    url = urlparse(db_uri)
    user = url.username
    password = url.password
    host = url.hostname or 'localhost'
    port = url.port or 5432
    dbname = url.path.lstrip('/')  # remove leading '/'

    # Connect to the default database (commonly "postgres")
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
    except Exception as e:
        print("Error connecting to PostgreSQL server:", e)
        sys.exit(1)

    cur = conn.cursor()
    # Check if the target database exists.
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    exists = cur.fetchone()
    if not exists:
        print(f"Database '{dbname}' does not exist. Creating...")
        try:
            cur.execute(f'CREATE DATABASE "{dbname}"')
            print(f"Database '{dbname}' created successfully.")
        except Exception as e:
            print("Error creating database:", e)
    else:
        print(f"Database '{dbname}' already exists.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    db_uri = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost/my_author_website_db"
    )
    print("Using database URI:", db_uri)
    create_database(db_uri)
