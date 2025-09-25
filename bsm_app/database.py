import sqlite3
import pandas as pd

# File to handle database and sql logic;

# Name of database file that will be created
DB_NAME = "options_analysis.db"


def get_db_connection():
    """Create and return a database connection to the SQLite database"""
    return sqlite3.connect(DB_NAME)


def create_tables():
    """ Function that creates the database and creates BSM "scenarios" table
    if it doesn't already exist; safe to run if the database already exists
    """
    con = get_db_connection()
    cursor = con.cursor()

    # Create the database table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bsm_scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME NOT NULL,
        spot_price REAL NOT NULL,
        strike_price REAL NOT NULL,
        time_to_maturity REAL NOT NULL,
        risk_free_rate REAL NOT NULL,
        volatility REAL NOT NULL,
        call_price REAL NOT NULL,
        put_price REAL NOT NULL,
        call_delta REAL,
        put_delta REAL,
        gamma REAL,
        vega REAL
        );
    """)
    # Commit changes and close connection
    con.commit()
    con.close()
    return


def save_scenario(data_dict):
    """Save new pricing scenario into database, given data in dictionary format """
    # Make connection and use cursor to interact with database
    con = get_db_connection()
    cursor = con.cursor()

    # Execute SQL command, saving new data entries using data dictionary
    # Use placeholders (templates for data) for safety
    cursor.execute("""
        INSERT INTO bsm_scenarios (timestamp, spot_price, strike_price, time_to_maturity,
        risk_free_rate, volatility, call_price, put_price, call_delta, put_delta, gamma, vega)
        VALUES (:timestamp, :S, :K, :T, :r, :sigma, :call_price, :put_price, :call_delta,
        :put_delta, :gamma, :vega)
    """, data_dict)

    # Commit changes and close connection
    con.commit()
    con.close()
    return


def load_scenarios():
    """Load all saved scenarios from the database into pandas dataframe format"""
    con = get_db_connection()

    # Get all scenarios from database and store into pandas dataframe
    df = pd.read_sql_query(
        "SELECT * from bsm_scenarios ORDER BY timestamp DESC", con)
    con.close()

    return df


# Create the database table when database.py is first imported into the app
create_tables()
