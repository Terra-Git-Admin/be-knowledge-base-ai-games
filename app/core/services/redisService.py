# import redis.asyncio as redis
# from datetime import datetime, timezone
# import json


# class RedisService:
#     def __init__(self):
#         self.redis = redis.Redis(host="localhost", port=6379, db=0)
    
#     async def mark_pad_unsaved(self, pad_id: str, revision: int):
#         try:
#             key = f"pad:{pad_id}"
#             ts = int(datetime.now(timezone.utc).timestamp() * 1000)

#             # store latest state
#             await self.redis.hset(key, mapping={
#                 "unsaved": "true",
#                 "lastSavedRevision": str(revision),
#                 "lastSavedAt": str(ts)
#             })

#             # track activity (sorted set: most recent updates)
#             await self.redis.zadd("pad:activity", {
#                 pad_id: int(datetime.now(timezone.utc).timestamp())
#             })

#             # publish event (for websockets / subscribers)
#             await self.redis.publish("pad:events", json.dumps({
#                 "type": "pad_update",
#                 "padId": pad_id,
#                 "etherpad": {
#                     "unsaved": True,
#                     "lastSavedRevision": revision,
#                     "lastSavedAt": ts
#                 }
#             }))
#         except Exception as e:
#             print(e)
#             raise e
    
#     async def mark_pad_saved(self, pad_id: str, revision: int):
#         try:
#             key = f"pad:{pad_id}"
#             ts = int(datetime.now(timezone.utc).timestamp() * 1000)

#             # store latest state
#             await self.redis.hset(key, mapping={
#                 "unsaved": "false",
#                 "lastSavedRevision": str(revision),
#                 "lastSavedAt": ts
#             })

#             # publish event (for websockets / subscribers)
#             await self.redis.publish("pad:events", json.dumps({
#                 "type": "pad_update",
#                 "padId": pad_id,
#                 "etherpad": {
#                     "unsaved": False,
#                     "lastSavedRevision": revision,
#                     "lastSavedAt": ts
#                 }
#             }))
#         except Exception as e:
#             print(e)
#             raise e
