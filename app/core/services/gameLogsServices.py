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
    
    # def get_logs_for_user_and_game(
    #     self, username: str, game_name: str, limit: int = 1000
    # ) -> Dict[str, Any]:
    #     """
    #     Fetch all logs for a specific user and game.
    #     Uses collection_group to query across all logs, then filters by path.
    #     """
    #     try:
    #         print(f"\n🔍 DEBUG: Starting query for username='{username}', game_name='{game_name}'")
            
    #         # Input validation
    #         if not username or not username.strip():
    #             print("❌ Username is empty")
    #             return {
    #                 "error": "Username is required",
    #                 "username": username,
    #                 "gameName": game_name,
    #                 "count": 0,
    #                 "logs": []
    #             }
            
    #         if not game_name or not game_name.strip():
    #             print("❌ Game name is empty")
    #             return {
    #                 "error": "Game name is required",
    #                 "username": username,
    #                 "gameName": game_name,
    #                 "count": 0,
    #                 "logs": []
    #             }

    #         username = username.strip()
    #         game_name = game_name.strip()
    #         print(f"✓ Cleaned username: '{username}'")
    #         print(f"✓ Cleaned game_name: '{game_name}'")

    #         # Use collection_group to query all "logs" collections across the database
    #         print("📋 Using collection_group to query all logs...")
    #         logs_ref = self.db.collection_group("logs")
            
    #         # Try ordering by timestamp
    #         try:
    #             query = logs_ref.order_by("timestamp", direction=firestore.Query.DESCENDING)
    #             print("✓ Query ordered by timestamp (descending)")
    #         except Exception as order_error:
    #             print(f"⚠️ Order by failed: {str(order_error)}")
    #             print("📋 Falling back to unordered query...")
    #             query = logs_ref

    #         stream = query.stream()
    #         logs: List[Dict] = []
    #         count_checked = 0
    #         count_matched = 0

    #         for log in stream:
    #             count_checked += 1
    #             path = log.reference.path
    #             print(f"\n📍 Checking log #{count_checked}: {path}")
                
    #             # Parse the path: players/{username}/games/{game_name}/logs/{log_id}
    #             path_parts = path.split("/")
    #             print(f"   Path parts: {path_parts}")
                
    #             if len(path_parts) < 6:
    #                 print(f"   ⏭️ Skipping - invalid path structure")
    #                 continue
                
    #             path_username = path_parts[1]
    #             path_game_name = path_parts[3]
                
    #             print(f"   Path username: '{path_username}' vs '{username}' - Match: {path_username == username}")
    #             print(f"   Path game: '{path_game_name}' vs '{game_name}' - Match: {path_game_name == game_name}")
                
    #             # Check if this log belongs to the requested user and game
    #             if path_username != username:
    #                 print(f"   ❌ Username mismatch, skipping")
    #                 continue
                    
    #             if path_game_name != game_name:
    #                 print(f"   ❌ Game name mismatch, skipping")
    #                 continue

    #             count_matched += 1
    #             print(f"   ✅ MATCH FOUND! Processing...")
                
    #             log_data = log.to_dict() or {}
    #             print(f"   Fields in document: {list(log_data.keys())}")

    #             # Convert timestamp safely
    #             ts = log_data.get("timestamp")
    #             if isinstance(ts, datetime):
    #                 date_str = ts.isoformat()
    #             elif isinstance(ts, dict) and "seconds" in ts:
    #                 date_str = datetime.utcfromtimestamp(ts["seconds"]).isoformat()
    #             else:
    #                 date_str = str(ts) if ts else None

    #             # Extract structured prompt/response data
    #             prompt_data = log_data.get("prompt", {}) or {}
    #             response_content = log_data.get("response", "")

    #             logs.append({
    #                 "logId": log.id,
    #                 "logPath": path,
    #                 "date": date_str,
    #                 "username": path_username,
    #                 "gameName": path_game_name,
    #                 "chat": {
    #                     "prompt": {
    #                         "systemPrompt": prompt_data.get("systemPrompt"),
    #                         "prompt": prompt_data.get("prompt"),
    #                         "files": prompt_data.get("files", []),
    #                         "temperature": prompt_data.get("temperature"),
    #                         "thinking": prompt_data.get("thinking"),
    #                         "thinkingBudget": prompt_data.get("thinkingBudget"),
    #                         "referencedAssets": prompt_data.get("referencedAssets", []),
    #                         "isImgUploadPresent": prompt_data.get("isImgUploadPresent", False),
    #                     },
    #                     "response": response_content,
    #                 },
    #             })

    #             if len(logs) >= limit:
    #                 print(f"\n✅ Reached limit of {limit} logs")
    #                 break

    #         print(f"\n{'='*60}")
    #         print(f"✅ Query complete!")
    #         print(f"   Checked: {count_checked} documents")
    #         print(f"   Matched: {count_matched} documents")
    #         print(f"   Returned: {len(logs)} logs")
    #         print(f"{'='*60}\n")

    #         # Sort in memory by timestamp if needed (ascending = oldest first)
    #         try:
    #             logs.sort(key=lambda x: x.get("date") or "", reverse=False)
    #             print("✓ Logs sorted by date (oldest first)")
    #         except Exception as sort_error:
    #             print(f"⚠️ Could not sort logs: {sort_error}")

    #         return {
    #             "username": username,
    #             "gameName": game_name,
    #             "count": len(logs),
    #             "logs": logs,
    #         }

    #     except Exception as e:
    #         print(f"❌ Error fetching logs: {str(e)}")
    #         import traceback
    #         traceback.print_exc()
    #         return {
    #             "error": f"Error fetching logs: {str(e)}",
    #             "username": username,
    #             "gameName": game_name,
    #             "count": 0,
    #             "logs": []
    #         }
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

gameLogsServices = GameLogsServices()