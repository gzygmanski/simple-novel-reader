#!/bin/python3

from bs4 import BeautifulSoup
import urllib

class TocContent:
    def __init__(self, path, toc_file):
        self.path = path
        self.toc_file = toc_file
        self.toc_list = []
        self.heading_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        self.paragraph_tags = ['p', 'b', 'i', 's', 'em', 'strong', 'del', 'ins']

        self.parse_content()
        self.add_paragraphs()


    def get_soup(self, path, parser):
        with open(path) as f:
            doc = f.read()

        return BeautifulSoup(doc, parser)

    def parse_content(self):
        soup = self.get_soup(self.toc_file, 'xml')

        for nav_item in soup.find_all(True):
            if nav_item.name == 'navPoint':
                toc_id = int(nav_item['playOrder'])
                toc_name = nav_item.select('navLabel > text')[0].string
                toc_content = nav_item.content['src'].split('#')
                toc_content[0] = self.path + '/' + urllib.parse.unquote(toc_content[0])

                toc_dict = {
                    'id': toc_id,
                    'name': toc_name,
                    'content': toc_content,
                    'text': []
                }

                self.toc_list.append(toc_dict)

    def add_paragraphs(self):
        current_file = ''
        current_heading = ''
        current_id = ''
        has_content = False
        has_id = self.has_id()

        for document in self.toc_list:
            new_file = document['content'][0]
            current_heading = document['name']
            if len(document['content']) == 2:
                current_id = document['content'][1]

            if new_file != current_file:
                soup = self.get_soup(document['content'][0], 'html.parser')
                current_file = new_file

            for tag in soup.find_all():
                if tag.name in self.heading_tags:
                    if tag.text == current_heading:
                        has_content = True
                    else:
                        has_content = False
                elif tag.has_attr('id'):
                    if tag['id'] == current_id:
                        print(tag.name)
                        has_content = True
                    else:
                        has_content = False
                elif not has_id:
                    if tag.name in self.paragraph_tags:
                        if tag.text != '' and tag.text != '\xa0':
                            document['text'].append(tag.text)
                else:
                    if tag.name in self.paragraph_tags and has_content:
                        if tag.text != '' and tag.text != '\xa0':
                            document['text'].append(tag.text)

    def get_toc_list(self):
        return self.toc_list

    def get_toc(self):
        toc = []
        for item in toc_list:
            toc.append(item['name'])

        return toc

    def get_number_of_chapters(self):
        return len(self.toc_list)

    def get_id(self, chapter):
        return self.toc_list[chapter]['id']

    def get_chapter_title(self, chapter):
        return self.toc_list[chapter]['name']

    def get_chapter_text(self, chapter):
        return self.toc_list[chapter]['text']

    def has_text(self, chapter):
        return False if len(self.toc_list[chapter]['text']) == 0 else True

    def has_id(self):
        for content in self.toc_list:
            if len(content['content']) == 2:
                return True
        return False

class BookContent:
    def __init__(self, content_list):
        self.content_list = content_list
        self.paragraphs = []
        self.headings = []
        self.parse_content()

    def parse_content(self):
        for chapter in self.content_list:
            with open(chapter) as f:
                html_doc = f.read()

            soup = BeautifulSoup(html_doc, 'html.parser')
            chapter_content = []

            for heading in soup.find_all('h1'):
                self.headings.append(heading.string)
            for paragraph in soup.find_all('p'):
                chapter_content.append(paragraph.string)
            self.paragraphs.append(chapter_content)

    def count_chapters(self):
        print(len(self.headings))

    def get_toc(self):
        return self.headings

    def get_heading(self, chapter):
        return self.headings[chapter]

    def get_content(self, chapter):
        return self.paragraphs[chapter]
