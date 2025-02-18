#!/usr/bin/env python
import os
import sys
import time
import socket
import psycopg2
from urllib.parse import urlparse

def check_port(host, port, timeout=5):
    """Check if a TCP port is open on a host."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.close()
        return True
    except Exception as e:
        print(f"Port check error: {e}")
        return False

def create_database(db_uri):
    # Parse the DATABASE_URL URI.
    url = urlparse(db_uri)
    user = url.username
    password = url.password
    host = url.hostname or 'localhost'
    port = url.port or 5432
    dbname = url.path.lstrip('/')  # remove leading '/'

    print(f"Attempting to create database: '{dbname}' using user '{user}' password '{password}' on {host}:{port}")

    # Connect to the default database (commonly "postgres")
    max_attempts = 10
    attempt = 0
    connected = False
    conn = None

    while attempt < max_attempts and not connected:
        try:
            conn = psycopg2.connect(
                dbname='postgres',  # connect to the default database
                user=user,
                password=password,
                host=host,
                port=port
            )
            connected = True
        except Exception as e:
            print(f"Attempt {attempt+1}/{max_attempts}: PostgreSQL not ready yet, waiting... ({e})")
            time.sleep(3)
            attempt += 1

    if not connected:
        print("Could not connect to PostgreSQL after several attempts.")
        sys.exit(1)
    else:
        conn.autocommit = True

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

    # Re-check that the database now exists
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
    exists_after = cur.fetchone()
    if exists_after:
        print(f"Verification: Database '{dbname}' exists.")
    else:
        print(f"Verification failed: Database '{dbname}' does not exist.")

    cur.close()
    conn.close()

if __name__ == "__main__":
    db_uri = os.environ.get(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost/my_author_website_db"
    )
    print("Using database URI:", db_uri)

    # Parse connection details
    url = urlparse(db_uri)
    host = url.hostname or 'localhost'
    port = url.port or 5432

    # Check if the port is accessible before trying to connect
    if check_port(host, port):
        print(f"Port {port} on {host} is open and accepting connections.")
    else:
        print(f"Port {port} on {host} is NOT accessible. Exiting.")
        sys.exit(1)

    # Proceed with database creation
    create_database(db_uri)

