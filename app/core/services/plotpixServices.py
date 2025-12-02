from google.cloud import firestore
import json

db = firestore.Client(project="aigameschat", database="school-game")
class PlotPixServices:
    def __init__(self, db_client: firestore.Client):
        self.db = db_client
        self.collection = self.db.collection("PP_data")
    
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
    
    def update_homescreen_data(self, data: dict):
        json_string = json.dumps(data, ensure_ascii=False)
        self.collection.document("HS_data").set({
            "HS_JSON": json_string
        })

plotPixServices = PlotPixServices(db)