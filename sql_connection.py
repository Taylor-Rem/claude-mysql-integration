from typing import Any, Dict, List
import mysql.connector
from mysql.connector import Error
from fastmcp import FastMCP
from dotenv import load_dotenv
import sys
from config import DB_CONNECTION, DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD
from system_prompt import system_prompt


# Load environment variables from .env file
load_dotenv('/Users/taylorremund/path/to/your/.env')  # Update this path to your actual .env location

# Create an MCP server
mcp = FastMCP("SQL_Connection")
mcp.context.set_system_prompt(system_prompt)

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_DATABASE,
            user=DB_USERNAME,
            password=DB_PASSWORD
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}", file=sys.stderr)
        return None

# Tool to query the database
@mcp.tool()
async def query_database(query: str) -> str:
    """Execute a SQL query on the MySQL database and return results.

    Args:
        query: SQL query (e.g., 'SELECT * FROM users WHERE id = 1')
    
    Returns:
        String representation of query results or error message.
    """
    print(f"Executing query: {query}", file=sys.stderr)
    connection = get_db_connection()
    if not connection:
        return "Failed to connect to the database."

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()
        
        if not results:
            return "No results found."
        
        # Format results as a string
        output = "Query Results:\n"
        for row in results:
            output += str(row) + "\n"
        return output
    except Error as e:
        return f"Error executing query: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Tool to update the database
@mcp.tool()
async def update_database(query: str) -> str:
    """Execute a SQL update or insert query on the MySQL database.

    Args:
        query: SQL update/insert query (e.g., 'UPDATE users SET status = 'active' WHERE id = 1')
    
    Returns:
        Confirmation or error message.
    """
    print(f"Executing update: {query}", file=sys.stderr)
    connection = get_db_connection()
    if not connection:
        return "Failed to connect to the database."

    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        return f"Successfully executed update. Rows affected: {cursor.rowcount}"
    except Error as e:
        return f"Error executing update: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Tool to describe a table schema
@mcp.tool()
async def describe_table(table: str) -> str:
    """Describe the schema of a MySQL table.

    Args:
        table: Name of the table (e.g., 'users')
    
    Returns:
        String representation of the table schema or error message.
    """
    print(f"Describing table: {table}", file=sys.stderr)
    connection = get_db_connection()
    if not connection:
        return "Failed to connect to the database."

    try:
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE {table}")
        results = cursor.fetchall()
        
        if not results:
            return f"No schema found for table '{table}'."
        
        output = f"Schema for table '{table}':\n"
        for row in results:
            output += f"Field: {row[0]}, Type: {row[1]}, Null: {row[2]}, Key: {row[3]}, Default: {row[4]}, Extra: {row[5]}\n"
        return output
    except Error as e:
        return f"Error describing table: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("Starting SQL MCP server...", file=sys.stderr)
    mcp.run(transport='stdio')