import pandas as pd
import csv
from bs4 import BeautifulSoup
import json
import urllib.request as urllib

#read in the dataset
data_df = pd.read_json("/yelp_dataset/yelp_academic_dataset_business.json", lines=True)

search_urls = {}
for index, row in data_df.iterrows():
    temp = 'https://www.yelp.com/biz/'
    search_urls[row['business_id']] = temp + row['business_id']

def get_pages(link):
    page = urllib.urlopen(link)
    soup = BeautifulSoup(page)
    links = soup.find_all('span', {'class': 'lemon--span__373c0__3997G text__373c0__2Kxyz text-color--black-extra-light__373c0__2OyzO text-align--left__373c0__2XGa-'})
    pages = []
    if len(links) != 0:
        edit = links[0].text
        temp = edit.split('of ')
        number_of_pages = int(temp[len(temp)-1])
        val = '?start='
        pages.append(link)
        while(number_of_pages != 1):
            num = (number_of_pages-1)*20
            fi = val + str(num)
            pages.append(link+fi)
            number_of_pages = number_of_pages-1
        non_recommended_reviews = soup.find_all('a', {'class': 'lemon--a__373c0__IEZFH link__373c0__1G70M link-color--inherit__373c0__3dzpk link-size--default__373c0__7tls6'})
        for x in non_recommended_reviews:
            if 'not currently recommended' in x.text:
                hyper = x['href']
                pages.append("https://www.yelp.com" + hyper)
    if len(links) == 0:
        print(link)
    return pages

def one_page_parsing(page_url):
    page = urllib.urlopen(page_url)
    soup = BeautifulSoup(page)
    review_texts = []
    dates = {}
    if 'not_recommended_reviews' in page_url:
        dd = soup.find_all('span', {'class': 'rating-qualifier'})
        final_dates = []
        for x in dd:
            t = x.text
            tt = t.replace('\n', '')
            ttt = tt.replace(' ', '')
            final_dates.append(ttt)
        temp = soup.find_all('p')
        reviews = temp[3:len(temp)]
        review_me = []
        for x in reviews:
            review_me.append(x.text)
        for x, y in zip(final_dates, review_me):
            value = y.replace('\xa0', '')
            dates[value] = x
    if 'not_recommended_reviews' not in page_url:     
        review_text = soup.find_all('p', {'class':'lemon--p__373c0__3Qnnj text__373c0__2Kxyz comment__373c0__3EKjH text-color--normal__373c0__3xep9 text-align--left__373c0__2XGa-'})
        d = soup.find_all('span', {'class' : 'lemon--span__373c0__3997G text__373c0__2Kxyz text-color--mid__373c0__jCeOG text-align--left__373c0__2XGa-'})
        if len(d) == 0 or len(review_text) == 0:
            dates['no review'] = page_url
        all_the_dates = []
        for x in d:
            all_the_dates.append(x.text)
        if len(review_text) < len(all_the_dates):
            extra_reviews = soup.find_all('div', {'class': 'lemon--div__373c0__1mboc margin-t3__373c0__1l90z padding-t3__373c0__1gw9E border--top__373c0__3gXLy border-color--default__373c0__3-ifU'})
            extra_reviews.text = []
            for review in extra_reviews:
                extra_reviews.text.append(review.text)
            for x in extra_reviews.text:
                new = x.split('Previous review')
                value = new[1].replace('\xa0', '')
                value_value = value.replace('Read more', '')
                dates[value_value] = new[0] #could be multiple reviews on the same date
                all_the_dates.remove(new[0])
            for x, y in zip(review_text, all_the_dates):
                text = x.text
                value = text.replace('\xa0', '')
                dates[value] = y
        if len(review_texts) == len(all_the_dates):
            for x, y in zip(review_text, all_the_dates):
                dates[x.text] = y
    return dates

df = pd.DataFrame(columns = ['business_id', 'date', 'review_content'])
for business, url in search_urls.items():
    pages = get_pages(url) #get all of the pages of reviews
    reviews = []
    for x in pages:
        r = one_page_parsing(x)
        for key, value in r.items(): #dicitonary of reviews --> review:date
            row = [business, value, key]
            df.loc[len(df)] = row
