import requests
class EtherpadService:
    API_KEY = "6fccb695d3eadd1c7ce830f0eb82399f7fac17551f77e8df0ecda93fc6561f5d"
    BASE_URL = "https://etherpad-437522952831.asia-south1.run.app/api/1.2.15"
    def __init__(self):
        pass

    def openFileInEtherpad(self, pad_id: str, initialContent: str = ""):
        try:
            get_url = f"{self.BASE_URL}/getText"
            get_res = requests.get(get_url, params={
                "apikey": self.API_KEY,
                "padID": pad_id
            },
            timeout=20)
            get_data = get_res.json()
            if get_data.get("code") == 0:
                text = get_data["data"]["text"]
                if not text.strip() or "Welcome to Etherpad!" in text:
                    set_url = f"{self.BASE_URL}/setText"
                    set_res = requests.post(
                        set_url,
                        params={"apikey": self.API_KEY, "padID": pad_id},
                        data={"text": initialContent},
                        timeout=20
                    )
                    return {"setText": set_res.json()}
                return {
                    "exists": True,
                    "text": get_data["data"]["text"]
                }
            else:
                create_url = f"{self.BASE_URL}/createPad"
                create_res = requests.get(create_url, params={"apikey": self.API_KEY, "padID": pad_id}, timeout=20)
                create_data = create_res.json()
                set_url = f"{self.BASE_URL}/setText"
                set_res = requests.post(
                    set_url,
                    params={
                        "apikey":self.API_KEY,
                        "padID": pad_id
                    },
                    data = {
                        "text": initialContent
                    },
                    timeout=20
                )
                set_data = set_res.json()
                return {
                    "create": create_data,
                    "setText": set_data
                }
        except Exception as e:
            return {"error" : str(e)}
    
    def getPadContent(self, pad_id: str):
        try:
            create_url = f"{self.BASE_URL}/getText"
            create_res = requests.get(create_url, params={
                "apikey": self.API_KEY,
                "padID": pad_id
            }, timeout=20)
            create_data = create_res.json()
            return create_data.get("data", {}).get("text", "")
        except Exception as e:
            return {"error" : str(e)}
    
    def getRevisionCount(self, pad_id: str) -> dict:
        try:
            # total revisions
            url_total = f"{self.BASE_URL}/getRevisionsCount"
            res_total = requests.get(url_total, params={
                "apikey": self.API_KEY,
                "padID": pad_id
            }, timeout=10).json()

            # saved revisions
            url_saved = f"{self.BASE_URL}/getSavedRevisionsCount"
            res_saved = requests.get(url_saved, params={
                "apikey": self.API_KEY,
                "padID": pad_id
            }, timeout=10).json()

            if res_total.get("code") == 0 and res_saved.get("code") == 0:
                total = res_total["data"]["revisions"]
                saved = res_saved["data"]["savedRevisions"]

                return {
                    "padID": pad_id,
                    "etherpad": {
                        "lastSavedRevision": total,
                        "lastSavedAt": None,  # you could later store timestamp if needed
                        "unsaved": total > saved
                    }
                }
            elif res_total.get("code") == 1:
                # pad not found
                return {
                    "padID": pad_id,
                    "etherpad": {
                        "lastSavedRevision": 0,
                        "lastSavedAt": None,
                        "unsaved": False
                    }
                }
            else:
                return {
                    "padID": pad_id,
                    "error": res_total.get("message", "Unknown error")
                }

        except Exception as e:
            return {"padID": pad_id, "error": str(e)}
    
    def setPadText(self, pad_id: str, content: str):
        try:
            set_url = f"{self.BASE_URL}/setText"
            set_res = requests.post(
                set_url,
                params={"apikey": self.API_KEY, "padID": pad_id},
                data={"text": content},
                timeout=20
            )
            return set_res.json()
        except Exception as e:
            return {"error" : str(e)}



etherpadService = EtherpadService()