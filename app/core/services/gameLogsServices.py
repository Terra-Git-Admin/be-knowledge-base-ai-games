from google.cloud import firestore
from typing import List, Dict, Any, Optional
from datetime import datetime

db = firestore.Client(project="aigameschat", database="school-game")

class GameLogsServices:
    COLLECTION_NAME = "players"

    def __init__(self):
        self.db = firestore.Client(project="aigameschat", database="school-game")

    def get_all_logs(
        self,
        game_name: Optional[str] = None,
        username: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict:
        """
        Fetch logs efficiently with Firestore filters and pagination.
        """

        logs_ref = self.db.collection_group("logs")

        # ---- Filter handling ----
        # Firestore collection_group queries cannot directly filter on parent fields,
        # so username/game_name filtering is done manually but only when necessary.
        # However, timestamp filtering, ordering, and limiting are done on Firestore side.

        query = logs_ref.order_by("timestamp", direction=firestore.Query.DESCENDING)

        results: List[Dict] = []

        # Use a stream generator for efficiency
        stream = query.stream()

        # Pagination simulation (Firestore offset is expensive, so we simulate with skip)
        skipped = 0
        count = 0

        for log in stream:
            path_parts = log.reference.path.split("/")
            if len(path_parts) < 6:
                continue

            username_in_path = path_parts[1].strip('"')
            game_id = path_parts[3]
            log_id = path_parts[5]

            if game_name and game_id != game_name:
                continue
            if username and username_in_path.lower() != username.lower():
                continue

            if skipped < offset:
                skipped += 1
                continue

            log_data = log.to_dict()
            ts = log_data.get("timestamp")

            if isinstance(ts, datetime):
                date_str = ts.isoformat()
            elif isinstance(ts, dict) and "seconds" in ts:
                date_str = datetime.utcfromtimestamp(ts["seconds"]).isoformat()
            else:
                date_str = None

            prompt_data = log_data.get("prompt", {}) or {}
            response_content = log_data.get("response", "")

            results.append({
                "logId": log_id,
                "logPath": log.reference.path,
                "date": date_str,
                "username": username_in_path,
                "gameName": game_id,
                "chat": {
                    "prompt": {
                        "systemPrompt": prompt_data.get("systemPrompt"),
                        "prompt": prompt_data.get("prompt"),
                        "files": prompt_data.get("files", []),
                        "temperature": prompt_data.get("temperature"),
                        "thinking": prompt_data.get("thinking"),
                        "thinkingBudget": prompt_data.get("thinkingBudget"),
                        "referencedAssets": prompt_data.get("referencedAssets", []),
                        "isImgUploadPresent": prompt_data.get("isImgUploadPresent", False),
                    },
                    "response": response_content,
                },
            })

            count += 1
            if count >= limit:
                break

        return {
            "count": len(results),
            "page": offset // limit + 1,
            "limit": limit,
            "logs": results,
            "note": f"Showing logs {offset + 1}-{offset + len(results)} "
                    f"for game '{game_name or 'all'}' and user '{username or 'all'}'"
        }
    def get_log_by_path(self, log_path: str) -> Dict:
        """
        Fetch a single log document by its full Firestore path.
        Example log_path: players/Arpita/games/Yuki_V2/logs/kOPXuXRdfiDjx9uCLPXe
        """
        try:
            doc_ref = self.db.document(log_path)
            doc = doc_ref.get()

            if not doc.exists:
                return {"error": f"No log found for path: {log_path}"}

            log_data = doc.to_dict() or {}
            ts = log_data.get("timestamp")

            if isinstance(ts, datetime):
                date_str = ts.isoformat()
            elif isinstance(ts, dict) and "seconds" in ts:
                date_str = datetime.utcfromtimestamp(ts["seconds"]).isoformat()
            else:
                date_str = None

            prompt_data = log_data.get("prompt", {}) or {}
            response_content = log_data.get("response", "")

            # Extract username/gameName/logId from the path
            parts = log_path.split("/")
            username = parts[1] if len(parts) > 1 else None
            game_name = parts[3] if len(parts) > 3 else None
            log_id = parts[5] if len(parts) > 5 else None

            return {
                "logId": log_id,
                "logPath": log_path,
                "username": username,
                "gameName": game_name,
                "date": date_str,
                "chat": {
                    "prompt": {
                        "systemPrompt": prompt_data.get("systemPrompt"),
                        "prompt": prompt_data.get("prompt"),
                        "files": prompt_data.get("files", []),
                        "temperature": prompt_data.get("temperature"),
                        "thinking": prompt_data.get("thinking"),
                        "thinkingBudget": prompt_data.get("thinkingBudget"),
                        "referencedAssets": prompt_data.get("referencedAssets", []),
                        "isImgUploadPresent": prompt_data.get("isImgUploadPresent", False),
                    },
                    "response": response_content,
                },
            }
        except Exception as e:
            raise Exception(f"Error fetching log by path: {e}")

gameLogsServices = GameLogsServices()