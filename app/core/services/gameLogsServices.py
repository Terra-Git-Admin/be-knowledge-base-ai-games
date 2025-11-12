from google.cloud import firestore
from typing import List, Dict, Any, Optional
from datetime import datetime

db = firestore.Client(project="aigameschat", database="school-game")

class GameLogsServices:
    COLLECTION_NAME = "players"

    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        # self.collection = self.db.collection(self.COLLECTION_NAME)
        self.root = self.db.collection("players")
    
    def list_collections(self):
        collections = list(self.db.collections())
        # logs_ref = self.db.collection_group("logs")
        # for log in logs_ref.limit(5).stream():
        #     print(log.reference.path)
        logs_ref = db.collection_group("logs")
        for log in logs_ref.stream():
            print("path:", log.reference.path)
            print("data:", log.to_dict())
        return {"collections": [c.id for c in collections]}
    def list_players(self, debug: bool = False):
        """List all unique players by querying the logs collection
        
        Since the players collection may be empty or have permission issues,
        we extract player_ids from the logs paths: /players/[player_id]/games/...
        """
        try:
            logs_ref = self.db.collection_group("logs")
            logs = list(logs_ref.stream())
            
            player_ids = set()
            
            for log in logs:
                path_parts = log.reference.path.split("/")
                # Expected structure: players/[player_id]/games/[game_id]/logs/[log_id]
                if len(path_parts) >= 2 and path_parts[0] == "players":
                    player_id = path_parts[1]
                    player_ids.add(player_id)
            
            sorted_player_ids = sorted(list(player_ids))
            
            result = {
                "count": len(sorted_player_ids),
                "player_ids": sorted_player_ids
            }
            
            if debug:
                result["debug_info"] = {
                    "project": self.db.project,
                    "method": "extracted_from_logs_collection_group",
                    "total_logs_queried": len(logs)
                }
            
            return result
        except Exception as e:
            return {"error": str(e), "count": 0, "player_ids": []}
    def get_all_logs(
        self,
        game_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict:
        """
        Fetch logs across all players/games in a UI-friendly format.
        Returns a flat list of logs with keys: date, username, gameName, chat.
        """

        db = firestore.Client(project="aigameschat", database="school-game")
        logs_ref = db.collection_group("logs")

        results: List[Dict] = []
        count = 0
        skipped = 0

        for log in logs_ref.stream():
            path_parts = log.reference.path.split("/")
            # Expected path: players/{username}/games/{game_name}/logs/{log_id}
            if len(path_parts) < 6:
                continue

            username = path_parts[1]
            game_id = path_parts[3]
            if game_name and game_id != game_name:
                continue

            if skipped < offset:
                skipped += 1
                continue

            log_data = log.to_dict()

            # Extract timestamp safely
            ts = log_data.get("timestamp")
            if isinstance(ts, datetime):
                date_str = ts.isoformat()
            elif isinstance(ts, dict) and "seconds" in ts:
                date_str = datetime.utcfromtimestamp(ts["seconds"]).isoformat()
            else:
                date_str = None

            # Extract user chat and AI response
            prompt_content = log_data.get("prompt", {}).get("prompt", "")
            response_content = log_data.get("response", "")

            # Build simplified entry
            results.append({
                "date": date_str,
                "username": username,
                "gameName": game_id,
                "chat": {
                    "prompt": prompt_content,
                    "response": response_content,
                }
            })

            count += 1
            if count >= limit:
                break

        return {
            "count": len(results),
            "page": offset // limit + 1,
            "limit": limit,
            "logs": results,
            "note": f"Showing logs {offset + 1}-{offset + len(results)} (paginated)"
        }


gameLogsServices = GameLogsServices(db)