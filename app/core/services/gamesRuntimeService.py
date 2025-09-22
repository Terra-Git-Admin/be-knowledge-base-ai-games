import os
from google.cloud import firestore
from typing import List, Dict, Any
from datetime import datetime

db = firestore.Client(project="aigameschat", database="school-game")


class GamesRuntimeService:
    COLLECTION_NAME = "games-runtime"

    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection(self.COLLECTION_NAME)

    def get_all_games(self) -> List[Dict[str, Any]]:
        """
        Retrieve all games from the games-runtime collection
        Returns a list of games with their gameName
        """
        try:
            docs = self.collection.stream()
            games = []
            
            for doc in docs:
                game_data = doc.to_dict()
                game_data['id'] = doc.id  # Include document ID
                games.append(game_data)
            
            return games
        except Exception as e:
            raise Exception(f"Error fetching games from games-runtime collection: {str(e)}")

    def create_game(self, game_name: str) -> Dict[str, Any]:
        """
        Create a new game in the games-runtime collection using gameName as document ID
        """
        try:
            game_data = {
                'gameName': game_name,
            }
            
            # Use gameName as the document ID
            self.collection.document(game_name).set(game_data)
            game_data['id'] = game_name
            
            return game_data
        except Exception as e:
            raise Exception(f"Error creating game: {str(e)}")


# Create a singleton instance
games_runtime_service = GamesRuntimeService(db)
