class NotificationGateway:
    def __init__(self):
        # mock HiKorea API interface
        pass

    def check_status(self, talent_id: str) -> str:
        # direct API interaction for sovereign status update
        return "PROCESSING"
