import requests

class API:
   
    base_url = "https://stark-beach-45459.herokuapp.com"
    
    def __init__(self):
        pass
    
    def get_order(self):
        url = self.base_url + "/order"
        r = requests.get(url)
        return r
