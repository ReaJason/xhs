class XhsClient:

    def __init__(self, session_id):
        self._session_id = session_id

    def set_session_id(self, session_id):
        self._session_id = session_id

    def get_session_id(self):
        return self._session_id
