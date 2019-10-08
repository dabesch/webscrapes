# webscrapes
_A store of various scripts for experimenting in web scraping_


#### GOTScrape.py
_An data analysis piece for Game of Thrones_

An example of web scraping summary information from IMDB.com. This is a scrape of episode information including the 
rating & release date.
Another scrape is included which pulls together the full cast and crew details for working on each episode.

This is a fast scrape which uses `bs4` package from `BeautifulSoup` to extract the information.
This was designed to pull the latest rating data from IMDB

From this 2 .csv files should be produced:
* `episode.csv` which contains episode summary data
* `credits.csv` which contains a list of all crew and cast grouped by department

#### yieldCurvesData.py
_Scrapes US treasury website for publicly available data_

Extracts the data and outputs to a pandas dataframe. These functions can then be imported into another workplace for 
analysing trends in yield curves
