from abc import abstractmethod
from typing import Any
import scrapy
import os
import json
from scrapy.crawler import CrawlerProcess

class AbstractCrawler:
    def __init__(self, output_dir=""):
        self.output_dir = output_dir
        self.q = []

    def add(self, ncode: str):
        pass
    
    def run(self):
        process = CrawlerProcess(
            {
                'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            }
        )
        for spider in self.q:
            process.crawl(spider)
        process.start()

class NcodeSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super(NcodeSpider, self).__init__(*args, **kwargs)
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def parse(self, response):
        filename = os.path.join(self.dirname,f'{self.s_chptr}.html')
        TITLE_SELECTOR='.novel_subtitle'
        CONTENT_SELECTOR = '#novel_honbun'
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(response.css(TITLE_SELECTOR).get())
            f.write(response.css(CONTENT_SELECTOR).get())
        self.s_chptr+=1
        if self.s_chptr <= self.e_chptr:
            next_page = self.base_url + str(self.s_chptr)
            yield scrapy.Request(next_page, callback=self.parse)

    @classmethod
    def ncode_config(cls, ncode: str, output_dir="", s_chptr=1, e_chptr=float("inf")) -> None:
        output_dir = os.path.abspath(output_dir)
        cls.ncode = ncode.lower()
        cls.s_chptr = s_chptr
        cls.e_chptr = e_chptr
        cls.start_urls = [f'https://ncode.syosetu.com/{ncode}/{s_chptr}']
        cls.base_url= f'https://ncode.syosetu.com/{ncode}/'
        cls.name = ncode
        cls.output_dir = output_dir
        cls.dirname=os.path.join(output_dir, ncode)

class NcodeCrawler(AbstractCrawler):
    def add(self, ncode: str, s_chptr=1, e_chptr=float("inf")):
        spider = type(f'Spider{ncode}', (NcodeSpider,), {})
        spider.ncode_config(ncode, output_dir=self.output_dir, s_chptr=s_chptr, e_chptr=e_chptr)
        self.q.append(spider)

class NcodeReviewsSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super(NcodeReviewsSpider, self).__init__(*args, **kwargs)
        self.counter = 0
        if not os.path.exists(self.dirname):
            os.makedirs(self.dirname)

    def parse(self, response):
        if self.base_url is None:
            self.base_url = response.xpath('//a[text()="レビュー"]/@href').get()
            yield scrapy.Request(self.base_url, callback=self.parse)
            return
        out = []
        raws = response.css('.hyoukawaku_in')
        for raw in raws:
            title=raw.css('h2::text').get()
            user =raw.css('.review_user').xpath('div/a/text()').get()
            date =raw.css('.review_user_date::text').get().replace("年 ", "-").replace("月 ", "-").replace("日 ", " ").replace("時 ", ":").replace("分", "").replace("\n", "").replace("[", "").replace("]", "")
            body =''.join(raw.css('.review_main::text').getall())
            out.append({'title':title, 'user':user, 'date':date, 'body':body})

        filename = os.path.join(self.dirname, f'{self.counter}.json')
        with open(filename, 'w', encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=4)
        self.counter += 1
        
        next_page = response.xpath('//a[@title="次のページ"]/@href').get()
        if next_page:
            next_page = self.base_url + next_page
            yield scrapy.Request(next_page, callback=self.parse)
            
    @classmethod
    def ncode_config(cls, ncode: str, output_dir="") -> None:
        output_dir = os.path.abspath(output_dir)
        ncode=ncode.lower()
        cls.ncode = ncode
        cls.start_urls = [f'https://ncode.syosetu.com/{ncode}/']
        cls.base_url = None
        cls.name = ncode
        cls.output_dir = output_dir
        cls.dirname=os.path.join(output_dir, ncode)
        cls.custom_settings = {
            'DOWNLOAD_DELAY': 2,
            'CONCURRENT_REQUESTS': 4,
        }

class NcodeReviewsCrawler(AbstractCrawler):
    def add(self, ncode: str):
        spider = type(f'Spider{ncode}', (NcodeReviewsSpider,), {})
        spider.ncode_config(ncode, output_dir=self.output_dir)
        self.q.append(spider)

if __name__ == "__main__":
    ncode = 'n1132dk'
    s_chptr=0
    e_chptr=365
    name = "ncode"
    NcodeSpider.ncode_config(ncode, s_chptr, e_chptr)
    NcodeSpider.run()