import threading
from ratelimiter import RateLimiter
import time
try:
    from api.batch_post import BatchPost
    from api.constituent import Constituent
except ModuleNotFoundError:
    from batch_post import BatchPost
    from constituent import Constituent

import threading
import time
from ratelimiter import RateLimiter

class API_Search:
    """
    Takes a BatchPost and searches each constituent, saving the results in the original object.
    """
    def __init__(self, batch: 'BatchPost', bb_session):
        """
        Initializes the API_Search instance with a BatchPost and a Blackbaud session.

        batch (BatchPost): The batch of constituents to be processed.
        bb_session: The session object for making API requests.
        """
        self.constits = batch.constits
        self.bb_session = bb_session
        self.lock = threading.Lock()  # Initialize a lock for thread-safe operations

    def api_calls(self):
        """
        Initiates API calls to search for each constituent in the batch. Uses threading
        to perform multiple calls concurrently while respecting rate limits.
        """
        threads = []  # List to hold the threads

        # Define the rate limit for API calls
        account_rate_limit_throttle = 10
        rate_limiter = RateLimiter(max_calls=account_rate_limit_throttle, period=1)

        # Create and start a thread for each constituent in the batch
        for constit in self.constits:
            with rate_limiter:
                thread = threading.Thread(target=self.search_constituent, args=(constit,))
                threads.append(thread)
                thread.start()

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    def search_constituent(self, constit: Constituent):
        """
        Searches for a specific constituent by making an API call. Updates the constituent
        object with the email and status based on the API response.

        constit (Constituent): The constituent to search for.
        """
        while True:
            # Make an API call to get constituent data
            r = self.bb_session.get(f'https://api.sky.blackbaud.com/constituent/v1/constituents/{constit.id}')

            if r.status_code == 200:
                # If the response is successful, extract email data
                email_data = r.json().get('email', None)
                email = email_data['address'].strip() if email_data else None
                do_not_email = email_data['do_not_email'] if email_data else False

                # Use a lock to ensure thread-safe update of the constituent object
                with self.lock:
                    constit.add_email(email, do_not_email)
                    constit.status('found' if email else 'missing')
                break

            elif r.status_code == 429:
                # If the rate limit is exceeded, wait for the specified retry-after time
                time.sleep(int(r.headers["Retry-After"]))
            else:
                # For other errors, set the constituent status to 'error'
                with self.lock:
                    constit.status('error')
                break
