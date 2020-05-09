from reader import FileReader
from parser import TocContent
from textwrap import wrap

test = FileReader('/home/shisam/horus.epub')
toc_path = test.get_toc_file()
path = test.get_directory_path(toc_path)

parser = TocContent(path, toc_path)

toclist = parser.get_toc_list()

# print(toclist[0])
max_lines = 10
max_cols = 40
on_page = []
pages = []

content = parser.get_chapter_text(0)
b = 1

for i in range(len(content)):

    split = wrap(content[i], max_cols)
    if b < max_lines:
        print (('i=%s, b=%s') % (i, b))
        on_page.append(content[i])
        b += 1
    else:
        pages.append(on_page)
        on_page = []
        b = 1
if len(on_page) != 0:
    pages.append(on_page)
    # if len(on_page) <= max_lines:
    #     for s in split:
    #         on_page.append(s)
    # if len(on_page) >= max_lines:
    #     pages.append(on_page)
    #     on_page = []

for page in pages:
    print(page)
    print('---')

print(len(content))
print(content)
# test2 = FileReader('/home/shisam/test.epub')
# toc_path = test2.get_toc_file()


# print(test2.get_toc_file())
# print(test2.get_directory_path(toc_path))

