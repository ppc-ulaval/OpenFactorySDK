import json
import os
import asyncio
from message_router import MessageRouter
from websocket_client import OpenFactoryWebSocketClient
from database_manager import DatabaseManager

class DatabaseConnectorApp:
    def __init__(self):
        self.assets = []
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(curr_dir, 'config.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            config_data = json.load(file)
        self.websocket_client = OpenFactoryWebSocketClient(config_data["base_url"] if config_data else "")
        self.db_manager = DatabaseManager()
    
    async def run(self):
        """Run the application"""
        print("Application is running. Press Ctrl+C to stop.")
        try:
            message_handler = MessageRouter(self.db_manager)

            self.websocket_client.set_message_handler(message_handler.handle_message)

            self.assets = self.db_manager.fetch_all_assets()
            
            await self.websocket_client.start(self.assets)
        except KeyboardInterrupt:
            print("\nShutting down app...")
            await self.websocket_client.stop()
            self.db_manager.disconnect()

if __name__ == "__main__":
    try:
        app = DatabaseConnectorApp()
        asyncio.run(app.run())
    except Exception as e:
        print(f"Failed to start application: {e}")