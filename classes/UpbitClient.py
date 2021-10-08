class UpbitClient:
    def __init__(self, upbitClient: object):
        self.upbitClient = upbitClient
        
    def get(self):
        return self.upbitClient