from bs4 import BeautifulSoup

def get_soup(path, parser):
    with open(path) as f:
        doc = f.read()

        return BeautifulSoup(doc, parser)



toc_file = '/tmp/reader/toc.ncx'

with open(toc_file) as f:
    xml_doc = f.read()

soup = BeautifulSoup(xml_doc, 'xml')

toc_list = []
for nav_item in soup.find_all(True):
    if nav_item.name == 'navPoint':
        toc_id = int(nav_item['playOrder'])
        toc_name = nav_item.select('navLabel > text')[0].string
        toc_content = nav_item.content['src'].split('#')
        toc_content[0] = '/tmp/reader' + '/' + toc_content[0]
        toc_dict = {
            'id': toc_id,
            'name': toc_name,
            'content': toc_content,
            'text': []
        }
        toc_list.append(toc_dict)
i = 0
current_id = ''
has_content = None
for item in toc_list:
    if len(item['content']) == 1:
        soup = get_soup(item['content'][0], 'html.parser')
    else:
        for tag in soup.find_all(True):
            if tag.has_attr('id'):
                if tag['id'] == item['content'][1]:
                    has_content = True
                else:
                    has_content = False
            if has_content:
                if tag.name == 'p' and not tag.text == '' and not tag.text == '\xa0':
                    item['text'].append(tag.text)

print(toc_list[33])
