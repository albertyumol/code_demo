# -*- coding: utf-8 -*-

"""Scraping with Beautiful Soup.

This is a script that extracts all title of artciles, their excerpts and
reading time from my personal blog. The output is a csv file containg
the said fields.

To run: `python scraper_sample.py`
"""

#Import python libraries
import requests
import re
from bs4 import BeautifulSoup
import pandas as pd
import random
import unicodedata
import datetime
import time
import os
import csv

class Scraper:

    def __init__(self):
        self.user_agent_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
        ]
        self.user_agent = random.choice(self.user_agent_list)
        self.headers = {'User-Agent': self.user_agent}
        self.time_start = datetime.datetime.now()
        self.time_end = None
        self.delay_secs = 0


    def get_soup(self, url=None):
        self.delay()
        new_agent = random.choice(self.user_agent_list)
        while new_agent == self.user_agent:
            new_agent = random.choice(self.user_agent_list)
        self.user_agent = new_agent
        self.headers = {'User-Agent': self.user_agent}
        print(self.headers)
        response = requests.get(url, headers=self.headers)
        return BeautifulSoup(response.text, 'html.parser')

    def delay(self):
        new_delay = random.randint(1, 6)
        while new_delay == self.delay_secs:
            new_delay = random.randint(1, 6)
        self.delay_secs = new_delay
        time.sleep(self.delay_secs)

    def get_curr_timestamp(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_curr_date_minute(self):
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

class PersonalBlogScraper(Scraper):

    def __init__(self):
        super().__init__()
        self.url = "https://albertyumol.github.io/"

    def retrieve_max_page_num(self):
        soup = self.get_soup(url=self.url)
        self.max_page_num = int(soup.find("nav", {"class": "pagination"}).findAll('li')[-2].get_text())
        return self.max_page_num
    
    def retrieve_artciles(self):
        all_titles = []
        all_excerpts = []
        all_time_to_read = []
        for page_num in range(1, self.max_page_num + 1):
            if page_num == 1:
                page_num_url = self.url
            else:
                pre_page_url = self.url + 'page'
                listing_page_directory_url = pre_page_url + str(page_num)
                page_num_url = pre_page_url + str(page_num)
            soup = self.get_soup(url=page_num_url)
            print("Retrieving listings from  ", page_num_url)
            
            title_list = soup.findAll("h2", {"class": "archive__item-title"})
            excerpt_list = soup.findAll("p", {"class": "archive__item-excerpt"})
            time_to_read_list = soup.findAll("p", {"class": "page__meta"})
            
            all_titles.extend([i.get_text() for i in title_list])
            all_excerpts.extend([i.get_text() for i in excerpt_list])
            all_time_to_read.extend([i.get_text() for i in time_to_read_list])

            self.data = pd.DataFrame({'title': all_titles, 'excerpts': all_excerpts,
                                     'reading_time': all_time_to_read})
        return self.data

    def export_to_csv(self):
        data_dir = os.path.join(os.getcwd() + os.sep, 'data' + os.sep)
        try:
            os.mkdir(data_dir)
        except:
            pass
        path = os.path.join(data_dir, 'blog_articles_' + self.get_curr_date_minute() + '.csv')
        self.data.to_csv(path, encoding='utf-8', index=False)
        print("Done!")

if __name__ == '__main__':
    scraper = PersonalBlogScraper()
    scraper.retrieve_max_page_num()
    scraper.retrieve_artciles()
    scraper.export_to_csv()