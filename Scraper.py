from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.proxy import *

from bs4 import BeautifulSoup
from time import sleep

import pandas as pd
import numpy as np

def random_wait(mean_time):    
    sleep(np.random.exponential(mean_time))

class Scraper:
    
    def __init__(self,isHeadless=False,proxy=None):
        self.isHeadless = isHeadless
        self.create_browser('',proxy=proxy)
        self.proxies = []
    
    def create_browser(self,start_url='', proxy=None):

        o = Options()
        o.add_argument('-private')
        o.headless = self.isHeadless

        self.browser = webdriver.Firefox(options=o,proxy=proxy)
    
    def load_link(self,link):
        try:
            self.browser.get(link)
        except TimeoutException:
            pass
        
    def scrape_link(self,link,scrape_routine):
        self.load_link(link)
        data = scrape_routine(self.browser)
        return data
    
    def scrape_links(self,links,scrape_routine):
        total_data = pd.DataFrame()
        for link in links:
            random_wait(5)
            try:
                data = self.scrape_link(link,scrape_routine)

            # Ifthere is any exception assume that it is because of ip being banned.
            except Exception:
                self.rotate_proxy()
                random_wait(4)
                data = self.scrape_link(link,scrape_routine)       
            
            total_data = pd.concat([total_data,data],ignore_index=True)
            
        return total_data
    
    def set_proxy_list(self,proxy_list):
        self.proxies = list(proxy_list)
    
    def rotate_proxy(self):
        
        n = len(self.proxies)
        if n > 0:
            new_proxy = self.proxies.pop(np.random.randint(n))
            print('\t Rotating proxy >> {}'.format(new_proxy))
            self.change_proxy(new_proxy)
        else:
            raise IndexError("No more available proxies.")
        
    def change_proxy(self,myProxy):

        proxy = Proxy({
        'proxyType': ProxyType.MANUAL,
        'httpProxy': myProxy,
        'ftpProxy': myProxy,
        'sslProxy': myProxy,
        'noProxy':''})
        
        self.close()
        self.create_browser(proxy=proxy)       
        
    def browser(self):
        return self.browser()
    
    def close(self):
        self.browser.quit()