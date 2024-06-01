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

        # How many calls per second can your account make
        account_rate_limit_throttle = 10

        # Start a thread for each name in the list
        rate_limiter = RateLimiter(max_calls=account_rate_limit_throttle, period=1)

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
                email = r.json().get('email', None)
                do_not_email = False # This will be default value if there is no address, allows us to distinguish consent and missing info
                if email:
                    do_not_email = email['do_not_email']
                    email = email['address'].strip()

                for i in self.constits:
                    if i.id == id:
                        i.add_email(email, do_not_email)
                        i.status('found' if email else 'missing')
                        break

                break

            elif r.status_code == 429:
                # wait for the specified retry-after time
                time.sleep(int(r.headers["Retry-After"]))
            else:
                i.status('error')
                break

    def return_data(self):
        return self.emails, self.errors
