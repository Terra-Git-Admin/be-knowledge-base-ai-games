import requests
class EtherpadService:
    API_KEY = "6fccb695d3eadd1c7ce830f0eb82399f7fac17551f77e8df0ecda93fc6561f5d"
    BASE_URL = "https://etherpad-437522952831.asia-south1.run.app/api/1.2.15"
    def __init__(self):
        pass

    def openFileInEtherpad(self, pad_id: str, initialContent: str = ""):
        try:
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

etherpadService = EtherpadService()