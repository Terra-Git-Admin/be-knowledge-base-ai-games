from google.cloud import firestore
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.core.schema.gamesLogsSchema import GameLogs

db = firestore.Client(project="aigameschat", database="school-game")

class GameLogsServices:
    COLLECTION_NAME = "players"

    def __init__(self):
        self.db = firestore.Client(project="aigameschat", database="school-game")
    
    def get_all_logs(
    self,
    game_name: Optional[str] = None,
    username: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> Dict:
        """
        Fetch a lightweight summary of logs grouped by (username, gameName, date).
        Only keeps one log per group for speed.
        """

        logs_ref = self.db.collection_group("logs")
        query = logs_ref.order_by("timestamp", direction=firestore.Query.DESCENDING)

        stream = query.stream()
        grouped: Dict[str, Dict] = {}

        for log in stream:
            path_parts = log.reference.path.split("/")
            if len(path_parts) < 6:
                continue

            username_in_path = path_parts[1].strip('"')
            game_id = path_parts[3]
            log_id = path_parts[5]

            # filters
            if game_name and game_id != game_name:
                continue
            if username and username_in_path.lower() != username.lower():
                continue

            log_data = log.to_dict()
            ts = log_data.get("timestamp")

            # Normalize timestamp
            if isinstance(ts, datetime):
                iso_ts = ts.isoformat()
                date_key = ts.date().isoformat()
            elif isinstance(ts, dict) and "seconds" in ts:
                dt = datetime.utcfromtimestamp(ts["seconds"])
                iso_ts = dt.isoformat()
                date_key = dt.date().isoformat()
            else:
                iso_ts = None
                date_key = "unknown"

            key = f"{username_in_path}|{game_id}|{date_key}"

            # Only add first log per group (skip rest)
            if key not in grouped:
                prompt_data = log_data.get("prompt", {}) or {}
                response_content = log_data.get("response", "")

                grouped[key] = {
                    "username": username_in_path,
                    "gameName": game_id,
                    "date": date_key,
                    "sampleLog": {
                        "logId": log_id,
                        "timestamp": iso_ts,
                        "prompt": prompt_data.get("prompt"),
                        "response": response_content[:200],  # short preview
                    },
                    "logsCount": 1,  # default count
                }

            # stop early once we have enough for pagination + buffer
            if len(grouped) >= offset + limit + 10:
                break

        # Convert to list + sort
        batches = list(grouped.values())
        batches.sort(key=lambda x: x["date"], reverse=True)

        total_groups = len(batches)
        paged_batches = batches[offset: offset + limit]

        return {
            "count": total_groups,
            "page": offset // limit + 1,
            "limit": limit,
            "batches": paged_batches,
            "note": f"Grouped by username + gameName + date; showing {len(paged_batches)} groups",
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

    def get_games_for_user(self, username: str) -> Dict[str, Any]:
        """
        Fetch all game names for a given username.
        Example path: players/{username}/games/{gameName}
        """
        try:
            user_ref = self.db.collection("players").document(username)
            games_ref = user_ref.collection("games")

            # List all game subcollections
            games = []
            for game_doc in games_ref.list_documents():
                games.append(game_doc.id)

            return {
                "username": username,
                "gamesCount": len(games),
                "games": games
            }
        except Exception as e:
            raise Exception(f"Error fetching games for user {username}: {e}")
    

    def get_logs_for_user_and_game(
        self, username: str, game_name: str, limit: int = 1000
    ) -> Dict[str, Any]:
        """
        Fetch all logs for a specific user and game using DIRECT PATH navigation.
        This is MUCH faster than collection_group queries.
        
        Path: players/{username}/games/{game_name}/logs/{log_id}
        """
        try:
            print(f"\n🔍 DEBUG: Starting DIRECT PATH query for username='{username}', game_name='{game_name}'")
            
            # Input validation
            if not username or not username.strip():
                print("❌ Username is empty")
                return {
                    "error": "Username is required",
                    "username": username,
                    "gameName": game_name,
                    "count": 0,
                    "logs": []
                }
            
            if not game_name or not game_name.strip():
                print("❌ Game name is empty")
                return {
                    "error": "Game name is required",
                    "username": username,
                    "gameName": game_name,
                    "count": 0,
                    "logs": []
                }

            username = username.strip()
            game_name = game_name.strip()
            print(f"✓ Cleaned username: '{username}'")
            print(f"✓ Cleaned game_name: '{game_name}'")

            # ============================================
            # DIRECT PATH NAVIGATION (NO collection_group!)
            # ============================================
            print("📍 Building direct path reference...")
            print(f"   players/{username}/games/{game_name}/logs")
            
            # Navigate directly to the logs collection
            logs_ref = (
                self.db.collection("players")
                .document(username)
                .collection("games")
                .document(game_name)
                .collection("logs")
            )
            
            print("✓ Direct path reference created")

            # Try ordering by timestamp
            try:
                print("📋 Attempting ordered query (by timestamp, descending)...")
                query = logs_ref.order_by("timestamp", direction=firestore.Query.DESCENDING)
                print("✓ Query ordered by timestamp (descending)")
            except Exception as order_error:
                print(f"⚠️ Order by failed: {str(order_error)}")
                print("📋 Falling back to unordered query...")
                query = logs_ref

            # Stream results
            print("🔄 Starting to fetch logs...")
            stream = query.stream()
            logs: List[Dict] = []
            count_fetched = 0

            for log in stream:
                count_fetched += 1
                log_id = log.id
                log_path = log.reference.path
                
                print(f"\n📌 Processing log #{count_fetched}")
                print(f"   Log ID: {log_id}")
                print(f"   Path: {log_path}")

                log_data = log.to_dict() or {}
                print(f"   Fields: {list(log_data.keys())}")

                # Convert timestamp safely
                ts = log_data.get("timestamp")
                if isinstance(ts, datetime):
                    date_str = ts.isoformat()
                    print(f"   Timestamp (datetime): {date_str}")
                elif isinstance(ts, dict) and "seconds" in ts:
                    date_str = datetime.utcfromtimestamp(ts["seconds"]).isoformat()
                    print(f"   Timestamp (dict): {date_str}")
                else:
                    date_str = str(ts) if ts else None
                    print(f"   Timestamp (other): {date_str}")

                # Extract structured prompt/response data
                prompt_data = log_data.get("prompt", {}) or {}
                response_content = log_data.get("response", "")
                
                prompt_preview = (prompt_data.get("prompt", "")[:100] + "...") if prompt_data.get("prompt") else "No prompt"
                response_preview = (response_content[:100] + "...") if response_content else "No response"
                print(f"   Prompt: {prompt_preview}")
                print(f"   Response: {response_preview}")

                logs.append({
                    "logId": log_id,
                    "logPath": log_path,
                    "date": date_str,
                    "username": username,
                    "gameName": game_name,
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

                if len(logs) >= limit:
                    print(f"\n✅ Reached limit of {limit} logs")
                    break

            print(f"\n{'='*60}")
            print(f"✅ QUERY COMPLETE!")
            print(f"   Total fetched: {count_fetched} documents")
            print(f"   Total returned: {len(logs)} logs")
            print(f"{'='*60}\n")

            # Sort in memory by timestamp (oldest first = ascending)
            try:
                logs.sort(key=lambda x: x.get("date") or "", reverse=False)
                print("✓ Logs sorted by date (oldest first)")
            except Exception as sort_error:
                print(f"⚠️ Could not sort logs: {sort_error}")

            return {
                "username": username,
                "gameName": game_name,
                "count": len(logs),
                "logs": logs,
            }

        except Exception as e:
            print(f"❌ Error fetching logs: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "error": f"Error fetching logs: {str(e)}",
                "username": username,
                "gameName": game_name,
                "count": 0,
                "logs": []
            }
    
    def get_all_games(self) -> List[str]:
        """
        Fetch all unique game names across all users.
        Returns a simple list of unique game names.
        """
        try:
            players_ref = self.db.collection("players")
            players = players_ref.list_documents()

            all_games = set()

            for player_doc in players:
                games_ref = player_doc.collection("games")
                for g in games_ref.list_documents():
                    all_games.add(g.id)

            return sorted(list(all_games))

        except Exception as e:
            raise Exception(f"Error fetching all games: {e}")
    
    def create_game_runtime_logs(self, gameLogData: GameLogs, username: str, gameName: str):
        try:
            doc_ref = (self.db.collection("players").document(username).collection("games").document(gameName).collection("logs").document())
            data = gameLogData.model_dump(exclude_none=True)
            data["timestamp"] = datetime.utcnow()
            doc_ref.set(data)
            return {"success": True}
        except Exception as e:
            raise Exception(f"Error creating game runtime logs: {e}")


gameLogsServices = GameLogsServices()