# -*- coding: utf-8 -*-
#抓取新浪国内新闻

import requests,re,json,pandas,time
#from bs4 import BeautifulSoup
from lxml import etree

#获取网页的html
def get_html(url):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        r.encoding = 'utf-8'
        return r.text
    except:
        return ''

#解析网页得到每个国内新闻链接
def get_sourceurls(html):
    try:
        # 把json数据字符串转换成python字典,相反的json.dumps()可以把数据转换成json数据
        jd = json.loads(html)
        s = jd['result']['data']
    except:
        s = ''
    sourceurls = []
    for j in s:
        url = j['url']
        sourceurls.append(url)
    return sourceurls

#得到所需信息

def get_wantedinfo(newurls):
    for newurl in newurls:
        newhtml = get_html(newurl)
        # 把newhtml变成可以使用Xpath的lxml.etree._Element类
        try:
            html = etree.HTML(newhtml)
        except:
            continue
            # soup = BeautifulSoup(newhtml, 'lxml')
            # title = soup.select('.main-title')[0].text
        try:
            # title = soup.select('.main-title')[0].text
            title = html.xpath('//h1[@class="main-title"]/text()')[0]
        except:
            title = 'title error'
        try:
            time = html.xpath('//span[@class="date"]/text()')[0]
        except:
            time = 'time error'
        try:
            # kw = soup.select('#keywords')[0].get('data-wbkey')
            kw = html.xpath('//div[@class="keywords"]')[0].get('data-wbkey')
            # article = '+'.join([article.text.strip() for article in soup.select('.article p')])
            # '+'.join 意思是把后面列表中的每一个元素用"+"连起来
            article = '+'.join([article.strip() for article in html.xpath('//div[@class="article"]/p/text()')])
        except:
            article = 'error'
        try:
            ctnum = re.findall('doc-i(.*?)\.shtml', newurl)
            cturl = 'http://comment5.news.sina.com.cn/page/info?version=1&format=json&channel=gn&newsid=comos-{}&group=undefined'
            commenturl = cturl.format(ctnum[0])
            cthtml = get_html(commenturl)
            ctdata = json.loads(cthtml)
            comments = ctdata['result']['count']
        except:
            comments = 'error'
        dic = {'标题': title, '链接': newurl, '参与人数和评论数': comments, '内容': article}
        infolist.append(dic)


if __name__ == '__main__':
    count = 0
    infolist = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    # 可以爬取很多页,这里爬取前10页
    for i in range(1, 11):
        url = 'http://api.roll.news.sina.com.cn/zt_list?channel=news&cat_1=gnxw&cat_2==gdxw1||=gatxw||=zs-pl||=mtjj&level==1||=2&show_ext=1&show_all=1&show_num=22&tag=1&format=json&page={}'.format(i)
        html = get_html(url)
        get_sourceurls(html)
        newurls = get_sourceurls(html)
        get_wantedinfo(newurls)
        #查看进度
        count = count + 1
        print(count)
        # 爬完一页休息2秒
        time.sleep(2)
        # 变成DataFrame格式,该格式脱身于统计R语言
    df = pandas.DataFrame(infolist)
    # 其中xlsx是Excel的后缀,可以把数据转换成Excel文件
    df.to_excel('news.xlsx')
    print(df)