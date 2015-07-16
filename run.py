from jarvis import scraper
from jarvis import search
from jarvis import app

if __name__ == '__main__':
    scraper.scrape()
    search.preprocess_index()
    app.start()