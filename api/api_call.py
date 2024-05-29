import threading
from ratelimiter import RateLimiter
import time
try:
    from api.batch_post import BatchPost
    from api.constituent import Constituent
except ModuleNotFoundError:
    from batch_post import BatchPost
    from constituent import Constituent

class API_Search:
    def __init__(self, batch: BatchPost, bb_session):
        self.constits = batch.constits
        self.bb_session = bb_session
        self.emails = []
        self.errors = []
        self.bad_responses = []

    def api_calls(self):
        # Create a list to hold the threads
        threads = []

        # Start a thread for each name in the list        
        rate_limiter = RateLimiter(max_calls=10, period=1)

        for constit in self.constits:
            with rate_limiter:
                thread = threading.Thread(target=self.search_constituent, args=(constit,))
                threads.append(thread)
                thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    def search_constituent(self, constit: Constituent):
        bb_session = self.bb_session

        id = constit.id
        name = constit.name

        while True:
            r = bb_session.get(f'https://api.sky.blackbaud.com/constituent/v1/constituents/{id}')
            # Process the response
            if r.status_code == 200:
                email = r.json()['email']['address'].strip()
                do_not_email = r.json()['email']['do_not_email']
                for i in self.constits:
                    if i.id == id:
                        i.add_email(email, do_not_email)
                        i.status('found')
                        break
                break

            elif r.status_code == 429:
                # wait for the specified retry-after time
                time.sleep(int(r.headers["Retry-After"]))
            else:
                i.status('error')
                break

    def return_data(self):
        # print(self.emails, self.errors)
        return self.emails, self.errors
