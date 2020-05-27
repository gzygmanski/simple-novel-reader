#!/bin/python3

from bs4 import BeautifulSoup
import urllib, os

class BookContent:
    def __init__(self, path, toc_file, content_file):
        self.path = path
        self.toc_file = toc_file
        self.content_file = content_file
        self.heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        self.paragraph_tags = ['p']
        self.style_tags = ['span', 'i', 'b', 'em', 'strong', 'a']
        self._set_toc_soup()
        self._set_content_soup()
        self._set_toc_list()
        self._set_reference_toc()
        self._set_content_dict()
        self._set_order_list()
        self._set_content()
        self._set_paragraphs()

    def _set_toc_soup(self):
        self.toc_soup = self.make_soup(self.toc_file, 'xml')

    def _set_content_soup(self):
        self.content_soup = self.make_soup(self.content_file, 'xml')

    def _set_toc_list(self):
        self.toc_list = []
        for index, nav_item in enumerate(self.toc_soup.navMap.find_all(recursive=False)):
            if nav_item.name == 'navPoint':
                toc_id = index + 1
                toc_name = nav_item.select('navLabel > text')[0].string
                toc_content = nav_item.content['src'].split('#')
                toc_content[0] = os.path.join(self.path, urllib.parse.unquote(toc_content[0]))
                if len(toc_content) == 2:
                    toc_inner_id = toc_content[1]
                else:
                    toc_inner_id = None
                toc_dict = {
                    'id': toc_id,
                    'inner_id': toc_inner_id,
                    'name': toc_name,
                    'src': [toc_content[0]],
                    'text': []
                }
                self.toc_list.append(toc_dict)

    def _set_reference_toc(self):
        self.reference_toc_src = None
        for item in self.content_soup.guide.find_all('reference'):
            if item['type'] == 'toc':
                reference = item['href'].split('#')
                self.reference_toc_src = self.path + '/' + urllib.parse.unquote(reference[0])

    def _set_content_dict(self):
        self.content_dict = {}
        self.content_toc_id = None
        for item in self.content_soup.find_all('item'):
            if item.has_attr('media-type') and item['media-type'] == 'application/xhtml+xml':
                content_id = item['id']
                content_src = self.path + '/' + urllib.parse.unquote(item['href'])
                if content_src != self.reference_toc_src:
                    self.content_dict[content_id] = content_src
                else:
                    self.content_toc_id = content_id

    def _set_order_list(self):
        self.order_list = []
        for item in self.content_soup.find_all('itemref'):
            if item.has_attr('idref'):
                if item['idref'] != self.content_toc_id:
                    self.order_list.append(item['idref'])

    def _set_content(self):
        paths_continue = False
        for index in range(len(self.toc_list)):
            for idref in self.order_list:
                if self.toc_list[index]['src'][0] == self.content_dict[idref]:
                    paths_continue = True
                if paths_continue:
                    if index != len(self.toc_list) - 1 and \
                        self.toc_list[index + 1]['src'][0] != self.content_dict[idref]:
                        self.toc_list[index]['src'].append(self.content_dict[idref])
                    else:
                        paths_continue = False
                        break
            if len(self.toc_list[index]['src']) > 1 and self.toc_list[index]['src'][0] == \
                self.toc_list[index]['src'][1]:
                self.toc_list[index]['src'].pop(0)

    def _set_paragraphs(self):
        current_file = ''
        current_heading = ''
        current_id = ''
        has_content = False
        for item in self.toc_list:
            for document in item['src']:
                new_file = document
                current_heading = item['name']
                if item['inner_id'] is not None:
                    current_id = item['inner_id']
                if new_file != current_file:
                    soup = self.make_soup(document, 'html.parser')
                    current_file = new_file
                if soup.body.find_all('p') == []:
                    if 'div' not in self.paragraph_tags:
                        self.paragraph_tags.append('div')
                else:
                    if 'div' in self.paragraph_tags:
                        self.paragraph_tags.remove('div')
                for tag in soup.body.find_all():
                    try:
                        if tag.name in self.heading_tags or tag.has_attr('id'):
                            if tag.text == current_heading or tag['id'] == current_id:
                                has_content = True
                            else:
                                has_content = False
                    except KeyError:
                        has_content = False
                    if item['inner_id'] is None or has_content:
                        if tag.name in self.paragraph_tags:
                            if tag.text.lstrip() != '' and tag.text.lstrip() != '\xa0':
                                item['text'].append(tag.text.lstrip())
                        if tag.name in self.style_tags \
                            and (tag.parent.name not in self.paragraph_tags \
                            and tag.parent.name not in self.style_tags):
                            if tag.text.lstrip() != '' and tag.text.lstrip() != '\xa0':
                                item['text'].append(
                                    tag.text.lstrip()
                                )

    def get_toc_list(self):
        return self.toc_list

    def get_toc(self):
        toc = {}
        for chapter in self.toc_list:
            toc[chapter['id']] = chapter['name']
        return toc

    def get_number_of_chapters(self):
        return len(self.toc_list)

    def get_id(self, chapter):
        return self.toc_list[chapter]['id']

    def get_document_title(self):
        return self.content_soup.find('title').text

    def get_chapter_title(self, chapter):
        return self.toc_list[chapter]['name']

    def get_chapter_text(self, chapter):
        return self.toc_list[chapter]['text']

    def has_text(self, chapter):
        return False if len(self.toc_list[chapter]['text']) == 0 else True

    def make_soup(self, path, parser):
        with open(path) as f:
            doc = f.read()
        return BeautifulSoup(doc, parser)
