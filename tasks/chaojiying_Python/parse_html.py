from lxml import etree
import csv

with open('./test.html','r',encoding='utf-8') as f:
    html = f.read()

html = etree.HTML(html)

# trs = html.xpath('//table[@id="its"]/tbody//trs[not(contains(@id))]')
trs = html.xpath('//table[@id="project"]/tbody//tr[(@class)]')
# print(trs)
items = []
for tr in trs:
    item = []
    tds = tr.xpath('./td')
    item.append(tds[5].text)
    item.append(tds[6].text)
    items.append(item)

with open('cmegsb_2022.csv','w',encoding='utf-8',newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['姓名', '电话'])
    writer.writerows(items)
