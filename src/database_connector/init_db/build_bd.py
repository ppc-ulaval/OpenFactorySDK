import os
import re

def main(connection, server: str = None):
    server = server or os.getenv("SQL_SERVER", "localhost")
    
    if connection:
        try:
            script_path = os.path.join(os.path.dirname(__file__), 'init_db.sql')
            if os.path.exists(script_path):
                with open(script_path, "r") as sql_file:
                    sql_script = sql_file.read()
                    sql_commands = sql_script.split(';')
                    
                    with connection.cursor() as cursor:
                        for command in sql_commands:
                            if command.strip():
                                print(f"Executing: {command.strip()}")
                                cursor.execute(command)
                        cursor.commit()
                        print("Database schema initialized successfully.") 
            
            script_path = os.path.join(os.path.dirname(__file__), 'cnc_insert_demo.sql')
            if os.path.exists(script_path):
                execute_sql_script(connection, script_path, "CNC insertion script")

            script_path = os.path.join(os.path.dirname(__file__), 'ivac_insert_demo.sql')
            if os.path.exists(script_path):
                execute_sql_script(connection, script_path, "iVAC insertion script")

            script_path = os.path.join(os.path.dirname(__file__), 'dust_trak_insert.sql')
            if os.path.exists(script_path):
                execute_sql_script(connection, script_path, "DUSTTRAK insertion script")

            script_path = os.path.join(os.path.dirname(__file__), 'test.sql')
            if os.path.exists(script_path):
                execute_sql_script(connection, script_path, "Test script")              
        except Exception as e:
            print(f"Error executing SQL script: {e}")
        
    else:
        print("Failed to connect to the database.")

def execute_sql_script(connection, script_path, script_name):
    """Execute a SQL script file, handling batches properly"""
    if not os.path.exists(script_path):
        print(f"SQL script file not found at: {script_path}")
        return False
    
    try:
        with open(script_path, "r") as sql_file:
            sql_script = sql_file.read()
        
        if 'GO' in sql_script.upper():
            batches = re.split(r'\bGO\b', sql_script, flags=re.IGNORECASE)
        else:
            batches = [sql_script]
        
        with connection.cursor() as cursor:
            for i, batch in enumerate(batches):
                batch = batch.strip()
                if batch:
                    print(f"Executing batch {i+1} from {script_name}")
                    
                    if batch.upper().strip().startswith('SELECT') and ';' in batch:
                        statements = [stmt.strip() for stmt in batch.split(';') if stmt.strip()]
                        for stmt in statements:
                            if stmt.upper().startswith('SELECT'):
                                print(f"\nQuery: {stmt}")
                                cursor.execute(stmt)
                                
                                rows = cursor.fetchall()
                                if rows:
                                    if cursor.description:
                                        columns = [desc[0] for desc in cursor.description]
                                        print(f"Columns: {', '.join(columns)}")
                                    
                                    print("Results:")
                                    for row in rows:
                                        print(row)
                                else:
                                    print("No data found.")
                                print("-" * 40)
                    else:
                        cursor.execute(batch)
                        cursor.commit()
        
        print(f"{script_name} executed successfully.")
        return True
        
    except Exception as e:
        print(f"Error executing {script_name}: {e}")
        return False