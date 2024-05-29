import json
from BbApiConnector import BbApiConnector
import os
import tempfile
try:
    from api.api_call import API_Search
    from api.batch_post import BatchPost
except ModuleNotFoundError:
    from api_call import API_Search
    from batch_post import BatchPost

def blackbaud(batch: BatchPost):

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
        bb_sec = os.environ['BB_CONFIG']
        bb_sec = json.loads(bb_sec)
        json.dump(bb_sec, tmp)
        tmp.close()
        api_conn = BbApiConnector(tmp.name)
        bb_session = api_conn.get_session()

        api = API_Search(batch, bb_session)
        api.api_calls()
    