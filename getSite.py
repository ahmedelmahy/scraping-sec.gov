import os
import json
import requests
from bs4 import BeautifulSoup
# improve try except to create subfoulders to save sources
#import errno
import random
import sys
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='bs4')
#-------------------------------
## code to scrape free proxies into a list from online I run separately to generate the proxies.json file
#import requests
#from lxml.html import fromstring
#import json
#def get_proxies():
#    url = 'https://free-proxy-list.net/'
#    response = requests.get(url)
#    parser = fromstring(response.text)
#    proxies = set()
#    for i in parser.xpath('//tbody/tr')[:50]:
#        if i.xpath('.//td[7][contains(text(),"yes")]'):
#            #Grabbing IP and corresponding PORT
#            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
#            proxies.add(proxy)
#    return proxies
#
#g = get_proxies()
#with open('proxies.json', 'w') as outfile:
#    json.dump(list(g), outfile)
#    



class website_a_scrap:
    urls = []
    # stores a signature for each data downloaded
    signature = []
    # temporal store of sourse text
    temp = ''
    # load proxies
    
    
    def __init__(self, yyyy):
        # load proxies
        with open('proxies.json', 'r') as f:
            self.proxies = json.load(f)
            
        with open('useragents.json', 'r') as f:
            self.user_agent_list = json.load(f)

        # I would go for a statistical approach to change and change the list of proxies
        # and headers into dicts of 0s and add one everytime one of them works
        self.header_log = dict(zip(self.user_agent_list,[0]* len(self.user_agent_list)))
        self.proxy_log = dict(zip(self.proxies,[0]* len(self.proxies)))
        
        target_link = ['cgi-bin/browse-edgar?action=getcompany&CIK='+yyyy+'&type=&dateb=&owner=exclude&start='+str(i*100)+'&count=100' for i in range(0,200)]
        for i in target_link:
            # checking if there is a next button in the page
            temp_link = 'https://www.sec.gov/' + i
            source = self.get_xxx( temp_link )
            txt = source.text
            if 'Next 100' in txt:
                self.function_scrap( i )
            else:
                print('website is scraped! done')
                return(0)

                
        
    def function_scrap(self, target_link ):
        
        target_link = 'https://www.sec.gov/' + target_link
        print(target_link)
        if self.if_is_new_link( target_link ):
            try:
                source = self.get_xxx( target_link )
                self.temp = source.text
                i = source.text
            
                if self.check_is_it_new_content(i) == True:
                    file_name = 'pages/'+os.path.basename(target_link)
#               if not os.path.exists(os.path.dirname(file_name)):
#                    try:
#                        os.makedirs(os.path.dirname(file_name))
#                    except OSError as exc: # Guard against race condition
#                        if exc.errno != errno.EEXIST:
#                            raise
                    with open(file_name, "w") as f:
                        f.write(i)

                # create a signature for the file content
            
                    sign = i.count('a') * len(i) + i.count('e')
                    self.signature.append(sign)
                # if got other link:
                    self.temp = self.extract_new_urls(i)
                # strop at # recursions
                #if len(self.urls) > 2 :
                #    return(0)
            
            
                    if len(self.temp) > 0:
                    
                        for link in self.temp:
                            #print('-----'+link)
                            self.function_scrap( link )
            except:
                print("link couldnot be downloaded with all proxies")
            
        
    def get_xxx(self, target_link ):
        for i in range(1,50):
            # random choice of the user agent
            user_agent = random.choice(self.user_agent_list)
            #Set the headers 
            headers = {'User-Agent': user_agent}
            # random choice of the proxy
            proxy = random.choice(self.proxies)
            try:
                # test without proxy
                #r = requests.get(target_link, timeout= 2)
                # run with proxy
                r = requests.get(target_link, #proxies={"http": proxy, "https": proxy}, 
                                 headers= headers, timeout=2)
                    
                # to get current session cookies we use
                # r.cookies.get_dict()
                # I am not sure how to rotate cookies 
                # I can store cookies of each session and reuse them later but not sure if this is
                # the write way -- I will leave it for feedback
                self.proxy_log[proxy] += 1
                self.header_log[user_agent] += 1
                # write logs each successful 20 pages 
                if random.choice(range(0,20)) == 15:
                    with open('proxy_log.json', 'w') as outfile:
                       json.dump(self.proxy_log, outfile)
                    with open('header_log.json', 'w') as outfile:
                        json.dump(self.header_log, outfile)
                print('worked')
                # an alternative to logging working proxies, I will append working
                # proxies to the list again . they will then have higher probability
                # of getting selected. We can statistically analyse this later to 
                # purify the list of proxies
                self.proxies.append(proxy)
                return(r)
            except:
                print('Proxy is slow trying another one ...')
        #cookies = random( cookies list - fail cookies list )
        #proxies = random( proxies list - fail proxies list )
        #header = random( header list - fail header list )
        
        #output = get with cookies, proxies, header, to target_link
        #    
        #    if new cookies, store to cookies list
        #    if proxies fail, log it
        #    if proxies success, log it
        #    if header fail, log it
        #    if cookies fail, log it
        #    
        #return output 

    def if_is_new_link(self, target_link ):
         # load data  from previous runs
         # save links
         # remove the main domain from the link
         yyyy = target_link[target_link.find('gov/')+4:]
         if yyyy in self.urls:
             #print(0)
             return(False)
         else:
             self.urls.append(yyyy)
             print('Pages downloaded: ' + str(len(self.urls)))
             return(True)
        #if compare with record == new link:
        #    return True
        #else return False
    def check_is_it_new_content(self, i):
        sign = i.count('a') * len(i) + i.count('e')
        if sign in self.signature:
            return(False)
        else:
            return(True)
        
    def extract_new_urls(self, html):
        all_new_links_in_html = []
        soup = BeautifulSoup(html)
        for link in soup.findAll('a'):
            href = link.get('href')
            # modify below for what files exactly to scrape
            #if type(href) == str and href.startswith('/') and href not in self.urls and '.' in os.path.basename(href) and 'www' not in href:
            # scrape only html
            if type(href) == str and href.startswith('/') and href not in self.urls and 'www' not in href and 'data' in href:
                all_new_links_in_html.append(href[1:])
        return(all_new_links_in_html)
        
        
x = website_a_scrap(sys.argv[1])    