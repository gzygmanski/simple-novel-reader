from imports.reader import FileReader
from imports.parser import BookContent

fileinput = '/home/shisam/amagi.epub'
reader = FileReader(fileinput)
toc_file = reader.get_toc_file()
content_file = reader.get_content_file()
path = reader.get_directory_path(toc_file)
book = BookContent(path, toc_file, content_file)

toc = book.get_toc_list()

print(toc[3]['name'])
print(toc[3]['src'])
