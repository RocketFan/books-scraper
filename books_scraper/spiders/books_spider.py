import os
import scrapy
import re
import json

from ..include.save_state import SaveState
from ..items import BookItem
from tqdm import tqdm

class BooksSpider(scrapy.Spider):
    name = 'books'

    def __init__(self, save=False, *a, **kw):
        self.state = SaveState(self, save)
        self.start_urls = self.get_start_urls('categories.json')
        self.pbars = [tqdm(position=i, desc='Url ' + str(i), leave=True) for i in range(len(self.start_urls))]
        super(BooksSpider, self).__init__(*a, **kw)

    def get_start_urls(self, filename):
        file = open(filename)
        categories = json.load(file)
        file.close()

        return [c['url'] for c in categories]

    def closed(self, reason):
        self.state.save_state()

    def start_requests(self):
        return self.state.load_state(self.pre_parse, {'page': 0})

    def pre_parse(self, response):
        meta = response.meta
        meta['total_pages'] = int(response.xpath('.//ul[contains(@class, "paginationList-hld")]/li[last()-1]/a/text()').get())
        self.pbars[meta['n_url']].total = meta['total_pages']
        self.pbars[meta['n_url']].update(meta['page'])
        meta['page'] += 1

        yield scrapy.Request(response.url + '?page=' + str(meta['page']), callback=self.parse, meta=meta)

    def parse(self, response):
        meta = response.meta
        all_books = response.xpath('.//div[@class="authorAllBooks__single"]')
        for book in all_books:
            yield self.get_book_info(book)

        self.pbars[meta['n_url']].update(1)

        if meta['page'] < meta['total_pages']:
            url = re.match('.*?(?=\?)|(?=$)', response.url).group(0)
            self.state.update_state(url, meta, ['page'])
            meta['page'] += 1
            yield scrapy.Request(url + '?page=' + str(meta['page']), callback=self.parse, meta=meta)


    def get_book_info(self, book):
        item = BookItem()
        book_info = book.xpath('.//div[contains(@class, "authorAllBooks__singleText")]')

        author = book_info.xpath('./div[contains(@class, "authorAllBooks__singleTextAuthor")]/a/text()')
        if author:
            item['author'] = author.get().strip()

        series = book_info.xpath('./div[contains(@class, "listLibrary__info")]/a/text()')
        if series:
            item['series'] = series.get().strip()

        item['img'] = book.xpath('.//form[contains(@class, "authorAllBooks__singleImgWrap")]/img/@data-src').get()
        item['title'] = book_info.xpath('./div[1]/a/text()').get().strip()
        item['rating'] = float(book_info.xpath('.//span[contains(@class, "listLibrary__ratingStarsNumber")]/text()').get().strip().replace(',', '.'))
        item['n_rating'] = int(book_info.xpath('.//div[contains(@class, "listLibrary__ratingAll")]/text()').get().split()[0])
        item['n_readers'] = int(book_info.xpath('./div[last()]/span[1]/text()').get().split()[-1])
        item['n_opinions'] = int(book_info.xpath('./div[last()]/span[last()]/text()').get().split()[-1])

        return item