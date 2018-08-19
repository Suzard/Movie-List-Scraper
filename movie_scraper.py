from collections import defaultdict
import scrapy
import re
#TO run
#scrapy crawl movie_scraper -s LOG_LEVEL=DEBUG 
'''
Goal: Retrieve the most popular movies and their actors
Implemented searching through extra pages as well
'''
class MovieSpider(scrapy.Spider):
    name = "movie_scraper"
    
    def start_requests(self):
        yield scrapy.Request(url='https://www.imdb.com/chart/moviemeter?ref_=nv_mv_mpm', callback=self.parse_genre)
    #end def

    def strip_list(self, list):
        stripped_list = []
        for i in list:
            if(i):
                stripped_list.append(i.strip())
            else:
                stripped_list.append(None)
        return stripped_list

    def retrieve_movie(self, response):
        '''
        iterates through the movie page and obtains a list of actors
        '''   
        name = response.xpath('//div[@class="title_wrapper"]//h1/text()').extract_first()
        current_page = response.xpath('//div[@id="titleCast"]/table/tr[@class="odd"] | //div[@id="titleCast"]/table/tr[@class="even"]')
        movie_dict = {}
        movie_dict[name] = []
        print(name)
        for movie in current_page:
            check_list = []
            actor_name = movie.xpath('./td[@class="itemprop"]/a/span/text()').extract_first()
            actor_url = response.urljoin(movie.xpath('./td[@class="itemprop"]/a/@href').extract_first())
            character_name = movie.xpath('./td[@class="character"]/text()').extract_first()
            if(not character_name):
                #if character name is a url, then the hyperlink must be accessed
                character_name = movie.xpath('./td[@class="character"]/a/text()').extract_first()
            character_url= response.urljoin(movie.xpath('./td[@class="character"]/a/@href').extract_first())
            check_list.extend((actor_name,actor_url, character_name, character_url))
            movie_dict[name].append(self.strip_list(check_list))
        print(movie_dict)
        #end def

    def retrieve_movie_list(self, response):
        '''
        iterates through a list of movies and also checks the next 
        page for additional lists which is done by calling parse_movie_pagelist
        again for the next page
        '''   
        current_page = response.xpath('//div[@class="article"]//h3[@class="lister-item-header"]/a/@href')
        for movie in current_page:
            movie_url = response.urljoin(movie.extract())
            yield scrapy.Request(movie_url, callback=self.retrieve_movie)
        #yield scrapy.Request(response, callback=self.retrieve_movie_list)
    #end def

    def parse_movie_pagelist(self, response):
        '''
        iterates through all lists of movies for that genre which
        is then passed to retrieve_movie_list to retrieve the movies
        '''   
        next_page = response.xpath('//div[@class="article"]//div[@class="desc"]/a[@class="lister-page-next next-page"]/@href')
        if(len(next_page) != 0):
            next_page_url = response.urljoin(next_page[0].extract())
            yield scrapy.Request(next_page_url, callback=self.retrieve_movie_list)
    #end def

    def parse_genre(self, response):
        '''
        https://www.imdb.com/chart/moviemeter?ref_=nv_mv_mpm
        give the function this link and it will retrieve all the 
        most popular movie genre pages
        '''        
        for genre_object in response.xpath('//div[@class="aux-content-widget-2"]/span[@class="ab_widget"]/ul/li[@class="subnav_item_main"]/a/@href'):
            genre_url = response.urljoin(genre_object.extract())
            yield scrapy.Request(genre_url, callback=self.parse_movie_pagelist)
        #end for
    #end def
