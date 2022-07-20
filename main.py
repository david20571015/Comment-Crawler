from crawler import crawl

if __name__ == '__main__':
    URL = 'https://www.chinatimes.com/realtimenews/20220720001867-260407?chdtv'
    print(crawl(URL, size=10))
