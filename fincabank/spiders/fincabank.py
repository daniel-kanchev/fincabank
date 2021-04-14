import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from fincabank.items import Article


class fincabankSpider(scrapy.Spider):
    name = 'fincabank'
    start_urls = ['https://www.fincabank.kg/category/%d0%bd%d0%be%d0%b2%d0%be%d1%81%d1%82%d0%b8/']
    page = 0

    def parse(self, response):
        links = response.xpath('//h2/a/@href').getall()
        if links:
            yield from response.follow_all(links, self.parse_article)

            self.page += 1

            next_page = f'https://www.fincabank.kg/category/%D0%BD%D0%BE%D0%B2%D0%BE%D1%81%D1%82%D0%B8/page/{self.page}/'
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="fusion-meta-info-wrapper"]/span/text()').get()
        if date:
            date = " ".join(date.split())

        content = response.xpath('//div[@class="post-content"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
