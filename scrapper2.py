from bs4 import BeautifulSoup
import unicodedata
from urllib import request
from urllib.request import Request, urlopen

from PyInquirer import prompt,Separator

class News:
    def __init__(self,id,title,desc,pd,link):
        self.id = id
        self.title = title
        self.desc = desc
        self.publish_date = pd
        self.link = link
        
class AzerTacNews:
    def __init__(self,page=1,baseurl='https://azertag.az',titles_url='https://azertag.az/bolme/official_chronicle?page=',perpage_news_number = 19):
        self._current_page = page
        self._baseUrl = baseurl
        self._titles_url = titles_url
        self.perpage_news_number = perpage_news_number
        self.newsdata = {}

    def show_page(self,newsaddress):
        newsurl = self._baseUrl+newsaddress
        request_site = Request(newsurl, headers={"User-Agent": "Mozilla/5.0"})
        fp = request.urlopen(request_site)
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
        soup = BeautifulSoup(mystr,features="html.parser")
        print(soup.find('div',id='selectedtext').get_text())

    def load_news_titles_page(self):
        url = self._titles_url+str(self._current_page)
        request_site = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        fp = request.urlopen(request_site)
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()
        MAIN_CNTNT_CLASS = 'news-item float-left withimg'
        soup = BeautifulSoup(mystr,features="html.parser")
        news = soup.find_all('div',MAIN_CNTNT_CLASS)
        if len(list(self.newsdata.values())) == 0:
            pageId = 1
        else:
            pageId = list(self.newsdata.values())[-1].id + 1 if list(self.newsdata.values())[-1].id != None else 1
        for n in news:
            link = n.h1.a['href']
            title = n.find('span',itemprop='headline')
            date = n.find('div','news-date').string.strip()
            news_short = unicodedata.normalize('NFKC',n.find('div','news-short').string).strip().replace('\n','')
            if not title.span is None: 
                title.span.extract()
            self.newsdata[pageId] = News(pageId,unicodedata.normalize('NFKC',title.contents[0].string).strip().replace('\n',' '),news_short,date,link)
            pageId+=1
            #print('loadednews '+ unicodedata.normalize('NFKC',title.contents[0].string).strip())

    def giveNewsRow(self,news):
        return "| "+news.publish_date+" | "+" | "+str(news.id)+" | "+news.title+" |"
        
    def promompt_news_titles(self):
        if len(list(self.newsdata.values())) == 0:
            self.load_news_titles_page()
        news_start = ((self._current_page-1)*self.perpage_news_number)  # next page start index
        news_end = self._current_page*self.perpage_news_number # next page end index + 1
        news_titles = [self.giveNewsRow(x) for x in list(self.newsdata.values())[news_start:news_end]]
        news_titles.extend([Separator(),'NEXT PAGE',Separator(),'PREVIOUS PAGE',Separator(),'EXIT =>',Separator(),{'name': 'PAGE: '+str(self._current_page),'disabled': ''}])
        questions = [
            {
                'type': 'list',
                'name': 'New',
                'message': 'Select News article: ',
                'choices': news_titles
            }
            ]
        answer = prompt(questions)['New']
        if(answer is 'NEXT PAGE'):
            self.next_page()
            return
        if(answer is 'PREVIOUS PAGE'):
            self.previous_page()
            return
        if(answer is 'EXIT =>'):
            return
        else:
            print(answer.split('|')[3])
            self.show_page(self.newsdata[int((answer.split('|')[3]).strip())].link)
            self.promompt_news_titles()
        
    def next_page(self):
        if(len(self.newsdata.values()) >= (self._current_page + 1) * self.perpage_news_number): # we have cached news
            self._current_page+=1
            self.promompt_news_titles()
        else:
            self._current_page += 1
            self.load_news_titles_page()
            self.promompt_news_titles()
    def previous_page(self):
        if(self._current_page == 1): return
        self._current_page -= 1
        self.promompt_news_titles()


print("""
    __                        _______         _   _                     __   
   / /       /\              |__   __|       | \ | |                    \ \  
  | |       /  \    _______ _ __| | __ _  ___|  \| | _____      _____    | | 
 / /       / /\ \  |_  / _ \ '__| |/ _` |/ __| . ` |/ _ \ \ /\ / / __|    \ \\
 \ \      / ____ \  / /  __/ |  | | (_| | (__| |\  |  __/\ V  V /\__ \    / /
  | |    /_/    \_\/___\___|_|  |_|\__,_|\___|_| \_|\___| \_/\_/ |___/   | | 
   \_\_____                                                        _____/_/  
    |______|                                                      |______|   
""")
newsop = AzerTacNews()
newsop.promompt_news_titles()