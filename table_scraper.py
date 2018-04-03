from bs4 import BeautifulSoup as BS
import urllib.request as r
import sys


if len(sys.argv) < 3:
	print("Usage: python table_scraper.py <url> <output_file>")
	sys.exit(1)

url = sys.argv[1]
outfile = sys.argv[2]

soup = BS(r.urlopen(url), "html5lib")
tables = soup.find_all("table")

print("Tables on " + url)
for i, table in enumerate(tables):
	print(str(i+1) +") " +",".join([" ".join([s.strip() for s in d.strings]) for d in table.find_all("tr")[0].find_all(["td", "th"])]))

uinput = input("Which tables (0 for all): ").replace(",", " ")
utables = None
if uinput.strip() == "0":
    utables = range(len(tables))
else:
    utables = [int(a)-1 for a in uinput.split()]

for u in utables:
    table = tables[u]
    data = []
    rows = table.find_all("tr")
    propogate_forward = []
    for row in rows:
        cells = row.find_all(["td", "th"])
        new_cells = []
        # insert cells that need to be propogated rightward i.e. colspan > 1
        for cell in cells:
            for j in range(int(cell.get('colspan', 1))):
                new_cells.append(cell)
            if 'colspan' in cell:
                del cell['colspan']
        cells = new_cells
        
        # initialize downward propogation array to length of first row
        if propogate_forward == []:
            propogate_forward = [None for i in range(len(cells))]
        
        # insert cells that need to be propogated downward i.e. rowspan > 1
        for i, p in enumerate(propogate_forward):
            if p:
                if p[1] > 0:
                    cells.insert(i, p[0])
                    p[1] -= 1
                if p[1] == 0:
                    p = None
        for i, cell in enumerate(cells):
            if cell.get('rowspan', None) != None:
                propogate_forward[i] = [cell, int(cell.get('rowspan'))-1]
                del cell['rowspan']

        # only get content from each cell in row, ignoring any html structure
        # problems: footnote superscripts (non-data in general) can be treated as data
        data.append([" ".join([s.strip() for s in d.strings]) for d in cells])
    fname = outfile.rsplit(".", 1)[0] + "_" + str(u+1) + ".csv"
    with open(fname, "w", encoding = "utf-8") as f:
        for row in data:
            f.write(",".join(["\"" + d +"\"" for d in row]) + "\n")
