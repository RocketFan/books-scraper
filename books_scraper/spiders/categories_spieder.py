import scrapy
import re

from ..items import CategoryItem

class CategoriesSpider(scrapy.Spider):
    name = 'categories'

    start_urls = ['https://lubimyczytac.pl/ksiazki/kategorie']

    base_url = 'https://lubimyczytac.pl/ksiazki/k'

    def parse(self, response):
        all_categories = response.xpath('//section[@class="categoryCategories"]/div/div[1]/div[1]')

        for category in all_categories:
            item = CategoryItem()

            item['category'] = category.xpath('./div[1]/h2/a/text()').get()
            genres = category.xpath('.//a[contains(@class, "categoryCategories__listItem")]')
            
            for genre in genres:
                item['url'] = self.base_url + genre.xpath('./@href').get()[10:]
                item['genre'] = genre.xpath('./text()').get()

                yield item