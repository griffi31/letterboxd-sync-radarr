# letterboxd-sync-radarr

A Python script to sync your Letterboxd watchlist with Radarr. This project uses Selenium to fetch movie titles from your Letterboxd watchlist and adds them to Radarr for easy tracking and management of movies.

## Features

- Fetches movie titles from your Letterboxd watchlist.
- Adds movies to your Radarr instance using the Radarr API.
- Allows for automated movie syncing.

## Prerequisites

Before using this tool, you need to have the following:

- A **Letterboxd** account to get your watchlist.
- A **Radarr** instance running with an API key.
- Python 3.8+ and necessary libraries installed.

### Required Libraries

- Selenium
- Requests

Install them using:

```bash
pip install -r requirements.txt
