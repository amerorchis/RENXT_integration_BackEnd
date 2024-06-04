# RENXT Integreation Backend Overview

This Flask application receives POST requests from a Chrome extension, which contain the name of a tag and a list of constituent IDs. It retrieves the email addresses and email consent for these IDs, then applies the specified tag to them using the Drip email manager.

## Features

* Receives POST requests containing tag information and constituent IDs.
* Retrieves email addresses and consent status from the NXT API.
* Applies tags to the retrieved email addresses using the Drip API.
* Sends confirmation emails upon successful tag application.

## Requirements

* Python 3.10 or lower (to use ratelimiter)

## Installation

### Running with Docker

1. Clone the repository.
2. Set your environment variables based on template.env.
3. Build the Docker image:

   `docker build -t renxt_integration_be .`

4. Run the Docker container:

   `docker run --env-file .env renxt_integration_be`

The application will be available at `http://127.0.0.1:5000/`.

## Usage

The application will be available at `http://127.0.0.1:5000/`.

### Endpoints

#### GET /

Returns a message prompting the user to make a POST request to use the program.

#### POST /

Processes a POST request containing tag and constituent IDs data.

### Example POST Request

<pre><code class="!whitespace-pre hljs language-json">{
'batch': 'Batch #GFT-2024-513',
'email': 'email@gaddress.com',
'tag': 'Test',
'tag_state': False,
'names': [['132207', 'Sam Walters'], ['132208', 'Michael Power'], ['132209', 'Roger Jacobs']]
}
</code></pre>

## Error Handling

### If a timeout occurs during the request:

* An email notification with logs is sent to the admin.
* An error message is returned to the Chrome extension.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For any questions or issues, please contact [andrew@glacier.org](mailto:andrew@glacier.org).
