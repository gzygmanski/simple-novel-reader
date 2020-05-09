from reader import FileReader
from parser import TocContent

test = FileReader('/home/shisam/horus.epub')
toc_path = test.get_toc_file()
path = test.get_directory_path(toc_path)


print(test.get_toc_file())
print(test.get_directory_path(toc_path))

parser = TocContent(path, toc_path)

toclist = parser.get_toc_list()

print(toclist[2])

for i in toclist[2]['text']:
    print(i)

# test2 = FileReader('/home/shisam/test.epub')
# toc_path = test2.get_toc_file()


# print(test2.get_toc_file())
# print(test2.get_directory_path(toc_path))

