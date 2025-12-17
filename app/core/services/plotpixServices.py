from google.cloud import firestore
import json

db = firestore.Client(project="aigameschat", database="school-game")
class PlotPixServices:
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection("PP_data")
    
    def deep_merge(self, original: dict, updates: dict) -> dict:
        result = dict(original)

        for key, value in updates.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value

        return result
    
    def get_homescreen_data(self):
        result = self.collection.document("HS_data").get()
        if result.exists:
            data = result.to_dict()
            hs_json = data.get("HS_JSON")
            if isinstance(hs_json, str):
                return json.loads(hs_json)
            return hs_json
        else:
            return None
    def get_stage_homescreen_data(self):
        result = self.collection.document("HS_Stage_data").get()
        if result.exists:
            data = result.to_dict()
            hs_json = data.get("HS_JSON")
            if isinstance(hs_json, str):
                return json.loads(hs_json)
            return hs_json
        else:
            return None
    
    def update_homescreen_data(self, data: dict):
        json_string = json.dumps(data, ensure_ascii=False)
        self.collection.document("HS_data").set({
            "HS_JSON": json_string
        })
    def update_stage_homescreen_data(self, data: dict):
        json_string = json.dumps(data, ensure_ascii=False)
        self.collection.document("HS_Stage_data").set({
            "HS_JSON": json_string
        })
    
    def update_given_parameters(self, data: dict, platform: str):
        doc_id = "HS_Stage_data" if platform == "stage" else "HS_data"
        doc_ref = self.collection.document(doc_id)

        snapshot = doc_ref.get()
        existing_root = {}

        if snapshot.exists:
            doc_data = snapshot.to_dict() or {}
            raw_json = doc_data.get("HS_JSON")

            if raw_json:
                existing_root = json.loads(raw_json)

        # 🔥 Deep merge at ROOT level
        updated_root = self.deep_merge(existing_root, data)

        doc_ref.set({
            "HS_JSON": json.dumps(updated_root, ensure_ascii=False)
        })
        return {
            "success": True
        }


plotPixServices = PlotPixServices(db)