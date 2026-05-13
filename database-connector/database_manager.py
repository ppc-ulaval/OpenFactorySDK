from typing import List
import pyodbc
import os
import time
from init_db.build_bd import main as init_db
from insert_type_strategy_factory import InsertTypeFactory
from dotenv import load_dotenv

class DatabaseManager:
    """Connects to and executes queries in database"""

    def __init__(self):
        load_dotenv()
        self.server = os.getenv("SERVER", "")
        self.database_name = os.getenv("DATABASE")
        self.user = os.getenv("USER")
        self.password = os.getenv("PASSWORD")
        self.max_retries = 5
        self.retry_delay = 5
        self.connection = None
        self.create_database_if_not_exists() ##Temporary fix to ensure database exists before connecting
        if not self.connect():
            raise ConnectionError("Failed to connect to the database after retries.")
        try:
            init_db(self.connection, self.server)
            print("Database schema initialized successfully")
        except Exception as e:
            print(f"Database schema initialization failed: {e}")
       
    
    def connect(self):
        """Connect to SQL Server with retry logic"""
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database_name};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"TrustServerCertificate=yes;"
            f"Connection Timeout=30;"
        )
        
        for attempt in range(self.max_retries):
            try:
                print(f"Attempting to connect to SQL Server (attempt {attempt + 1}/{self.max_retries})")
                print(f"Server: {self.server}")
                print(f"Database: {self.database_name}")
                print(f"User: {self.user}")
                
                self.connection = pyodbc.connect(connection_string)
                print("Database connection established successfully.")
                return True
                
            except pyodbc.Error as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("All connection attempts failed.")
                    return False
        
        return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
    
    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            master_connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE=master;"
                f"UID={self.user};"
                f"PWD={self.password};"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=30;"
            )
            
            master_conn = pyodbc.connect(master_connection_string, autocommit=True)
            cursor = master_conn.cursor()
            
            cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{self.database_name}'")
            if not cursor.fetchone():
                print(f"Creating database: {self.database_name}")
                cursor.execute(f"CREATE DATABASE [{self.database_name}]")
                cursor.commit()
                print(f"Database {self.database_name} created successfully.")
            else:
                print(f"Database {self.database_name} already exists.")
                
            cursor.close()
            master_conn.close()
            
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
        
        return True
    
    def insert_value(self, asset_uuid, dataitem_id, update_value, update_timestamp):
        """Insert new value into StrValue table"""
        variable_id = self.fetch_variable_id(asset_uuid, dataitem_id)
        var_type = self.fetch_type(variable_id)
        if variable_id and var_type:
            insertStrategy = InsertTypeFactory.create_strategy(var_type)
            insertStrategy.insert_value(self.connection, variable_id, update_value, update_timestamp)


    def fetch_all_assets(self) -> List[str]:
        """Fetch all assets from the database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT AssetUuid FROM OpenFactoryLink ")
            assets = []
            for row in cursor:
                assets += [elem for elem in row]
            cursor.close()
            return assets
        except Exception as e:
            print(f"Error fetching assets: {e}")
            return []
        
    def fetch_assets(self, included_assets:List[str]=[], excluded_assets:List[str]=[]):
        pass
    
    def fetch_variable_id(self, asset_uuid: str, dataitem_id: str) -> str:
        """Fetch VariableId from DataitemId"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT VariableId FROM OpenFactoryLink WHERE DataitemId = ? AND AssetUuid = ?", (dataitem_id, asset_uuid))
            result = cursor.fetchone()
            cursor.close()

            if result:
                return result[0]
            else:
                print(f"No VariableId found for AssetUuid={asset_uuid} and DataitemId={dataitem_id}")
                return ''
        except Exception as e:
            print(f"Error fetching variable_id: {e}")
            return ''
        
    def fetch_type(self, variable_id: str) -> str:
        """Fetch data Type from VariableId"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT Nom FROM Type WHERE Id = (SELECT TypeId FROM Variable WHERE Id = ?)", (variable_id))
            result = cursor.fetchone()
            cursor.close()

            if result:
                return result[0]
            else:
                print(f"No type found for this VariableId")
                return ''
        except Exception as e:
            print(f"Error fetching type: {e}")
            return ''