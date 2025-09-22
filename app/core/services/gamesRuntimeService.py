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

    def get_game_by_id(self, game_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific game by its document ID
        """
        try:
            doc = self.collection.document(game_id).get()
            if doc.exists:
                game_data = doc.to_dict()
                game_data['id'] = doc.id
                return game_data
            else:
                return None
        except Exception as e:
            raise Exception(f"Error fetching game with ID {game_id}: {str(e)}")

    def create_game(self, game_name: str) -> Dict[str, Any]:
        """
        Create a new game in the games-runtime collection
        """
        try:
            game_data = {
                'gameName': game_name,
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            
            doc_ref = self.collection.add(game_data)
            game_data['id'] = doc_ref[1].id
            
            return game_data
        except Exception as e:
            raise Exception(f"Error creating game: {str(e)}")


# Create a singleton instance
games_runtime_service = GamesRuntimeService(db)
