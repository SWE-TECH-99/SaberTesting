# 📰 BBC Article Scraper

## Description

This project consists of two main components:

1. **Python Scraper**: A script that scrapes article headlines and URLs from the BBC website and stores them in a PostgreSQL database.
2. **Next.js Frontend**: A web application that displays the scraped articles and allows users to delete articles from the database.

## Prerequisites

- Python 3.x
- Node.js
- PostgreSQL

## Setup

### PostgreSQL Database

Ensure you have PostgreSQL installed and running. Create a new database for this project.

### Environment Variables

Create a `.env.local` file in the `bbc-scraper-frontend` directory with the following content:

### Install Required Packages
Python
Navigate to the project root directory and install the required packages:
pip install requests beautifulsoup4 psycopg2-binary aiohttp tqdm

## Run the Scraper
Navigate to the bbc-scraper-frontend directory and run the scraper script to populate the database:
cd bbc-scraper-frontend
python scraper.py

## Next.js Frontend
### Install Dependencies
Navigate to the bbc-scraper-frontend directory:
cd bbc-scraper-frontend
### Install the necessary Node.js packages:
yarn install
Start Development Server
Run the development server:
yarn dev
Open your browser and navigate to http://localhost:3000 to view the application.

### Usage
The homepage will display a list of scraped articles.
Each article has a "Delete" button that allows you to remove the article from the database.

### Verify the Database
You can use the following query to check if the articles are present in the database:
SELECT * FROM public.articles
ORDER BY id ASC;




### Troubleshooting
Ensure the PostgreSQL database is running and accessible.
Check the .env.local file for correct database credentials.
Ensure all dependencies are installed by following the setup steps.
Enjoy scraping and managing BBC articles! 🚀