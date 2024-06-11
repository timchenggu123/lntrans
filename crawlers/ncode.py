from typing import Any
import scrapy
import os
from scrapy.crawler import CrawlerProcess
class NcodeSpider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super(NcodeSpider, self).__init__(*args, **kwargs)
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def parse(self, response):
        filename = self.filename
        TITLE_SELECTOR='.novel_subtitle'
        CONTENT_SELECTOR = '#novel_honbun'
        with open(filename, 'a', encoding="utf-8") as f:
            f.write(response.css(TITLE_SELECTOR).get())
            f.write(response.css(CONTENT_SELECTOR).get())
        self.s_chptr+=1
        if self.s_chptr <= self.e_chptr:
            next_page = self.base_url + str(self.s_chptr)
            yield scrapy.Request(next_page, callback=self.parse)

    @classmethod
    def ncode_config(cls, ncode: str, output_dir="", s_chptr=1, e_chptr=float("inf")) -> None:
        cls.ncode = ncode.lower()
        cls.s_chptr = s_chptr
        cls.e_chptr = e_chptr
        cls.start_urls = [f'https://ncode.syosetu.com/{ncode}/{s_chptr}']
        cls.base_url= f'https://ncode.syosetu.com/{ncode}/'
        cls.name = ncode
        cls.output_dir = output_dir
        cls.filename=f'{output_dir}{ncode}.html'

class NcodeCrawler:
    def __init__(self, output_dir=""):
        self.output_dir = output_dir
        self.q = []
    
    def queue_novel(self, ncode: str, s_chptr=1, e_chptr=float("inf")):
        spider = type(f'Spider{ncode}', (NcodeSpider,), {})
        spider.ncode_config(ncode, output_dir=self.output_dir, s_chptr=s_chptr, e_chptr=e_chptr)
        self.q.append(spider)
    
    def run(self):
        process = CrawlerProcess(
            {
                'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
            }
        )
        for spider in self.q:
            process.crawl(spider)
        process.start()

if __name__ == "__main__":
    ncode = 'n1132dk'
    s_chptr=0
    e_chptr=365
    name = "ncode"
    NcodeSpider.ncode_config(ncode, s_chptr, e_chptr)
    NcodeSpider.run()