import scrapy
import os
import re
import inspect

class SaveState:
    spider = None
    save = False
    filepath = ''

    def __init__(self, spider, save):
        self.spider = spider
        self.save = save
        self.filepath = os.path.dirname(os.path.abspath(inspect.getfile(spider.__class__)).replace('\\', '/')) + '/states/'

    def save_state(self):
        if self.save:
            with open(self.filepath + self.spider.name + '.txt', 'w+') as file:
                file.writelines([f'{url}\n' for url in self.spider.start_urls])

    def update_state(self, url, meta, to_save):
        meta_to_save = {key: meta[key] for key in to_save}
        self.spider.start_urls[meta['n_url']] = url + '#!' + str(meta_to_save)

    def load_state(self, func=None, default_meta={}):
        urls = []
        meta = []
        func = func if func else self.spider.parse

        def add_urls(url_elements):
            urls.append(url_elements[0])
            if len(url_elements) != 2:
                meta.append(default_meta)
            else:
                meta.append(eval(url_elements[1]))

        if self.save:
            filepath = self.filepath + f'{self.spider.name}.txt'
            if os.path.exists(filepath):
                with open(filepath, 'r+') as file:
                    while True:
                        line = file.readline()
                        if not line:
                            break
                        line_elements = re.split('#!(?={.*?}$)', line)
                        add_urls(line_elements)

        for url in self.spider.start_urls:
            url_elements = re.split('#!(?={.*?}$)', url)

            if not url_elements[0] in urls:
                add_urls(url_elements)

        self.spider.start_urls = [x + str(y) for x, y in zip(urls, meta)]

        for i, url in enumerate(urls):
            meta[i]['n_url'] = i
            yield scrapy.Request(url, callback=func , meta=meta[i])