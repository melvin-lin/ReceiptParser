import numpy as np
from google.cloud import vision
import datetime
import io
import os
import re

SKIPWORDS = ['time', 'date']
ENDWORDS = ['total', 'balance', 'amount']
STOPWORDS = ['visa', 'price you pay', 'debit', 'date', 'credit', 'subtotal', 'tax', 'coupons', 'btotal']
BLACKLIST_WORDS = ['register', 'cashier', 'thank', 'tran', 'store', 'closed', 'order', 'invoice', 'station', 'entry method', 'reference', 'count', 'www.', 'http', 'tel', 'merchant', 'grocery', 'seafood', 'produce', 'misc', 'cash', '@', 'hier', '*']
DISCARD_REG = ['price', 'orig', 'reg', 'each']

def is_number(str): 
    try: 
        _ = float(str)
        return True
    except Exception as e: 
        return False

def is_decimal(num): 
    if not is_number(num): 
        return False
    if round(float(num)) != float(num):
        return True
    else: 
        return False

def blacklist(label): 
    for blacklist_word in BLACKLIST_WORDS: 
        if blacklist_word in label.lower():
            return False
    return True

def skiplist(label): 
    for skiplist_word in SKIPWORDS: 
        if skiplist_word in label.lower():
            return False
    return True

def stoplist(label): 
    for stoplist_word in STOPWORDS: 
        if stoplist_word in label.lower(): 
            return False
    return True

def endlist(label):
    for endlist_word in ENDWORDS: 
        if endlist_word in label.lower() and \
            len(endlist_word) == len(label.lower()): 
            return False
    return True

class Parser: 
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
        
    def parse_date(self, date):
        if date == None: 
            return None

        for fmt in ['%d.%m.%y', '%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y', '%m/%d/%y', ]: 
            for substr in date.split(' '): 
                try: 
                    new_date = datetime.datetime.strptime(substr, fmt).strftime('%m/%d/%Y')
                    return new_date
                except Exception as e: 
                    pass
        return None
    
    def check_price(self, value): 
        if ' ' in value: 
            value = value.replace(' ', '')

        pr = value
        pr = pr.replace('F','').replace('N', '').replace('S', '').replace('D', '').replace('S.', '')
        pr = pr.replace('$','').replace(',','.')

        try: 
            if pr[0] == '-': 
                pr = pr.replace('-', '')
            if pr[len(pr)-1] == '.': 
                pr = pr[0:len(pr)-1]
        except: 
            pr = pr

        r = pr.replace('.','').replace('T', '').replace('-', '')
        if "." in pr and r.isnumeric() == True:  
            if r.isnumeric() == True:  
                return pr
        else: 
            return False

    def parse_receipt(self, path, record):
        gcloud_response = self.detect_text(path)
        return self.parse_response(gcloud_response, record)

    def detect_text(self, path): 
        with io.open(path, 'rb') as image_file: 
            content = image_file.read()
        image = vision.Image(content=content)
        response = self.client.text_detection(image=image)
        text = response.text_annotations[0].description
        if response.error.message: 
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        return response

    def is_integer(self, text_body): 
        try:
            _ = int(text_body)
        except:
            return False
        if round(float(text_body)) == float(text_body):
            return True
        return False
    
    def check_article_name(self, article_name):
        num_alnum = 0
        for c in article_name:
            if c.isalpha():
                num_alnum += 1
        if num_alnum <= 2:
            return False
        return True

    def remove_blacklist(self, description): 
        rmdes = []
        for label in description: 
            if blacklist(label) != True: 
                rmdes.append(label)

        for label in rmdes:
            description.remove(label) 
            
        return description

    def find_phone(self, description, receipt): 
        phone = re.findall("(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})", description)
        for value in phone: 
            return receipt.index(value)
        return None

    def retrieve_articles(self, articles, text, description): 
        articles = []
        update = []
        try:
            state = self.find_address(description)
            phone = self.find_phone(text, description)
        except: 
            phone = -1

        if state == phone: 
            index = -1
        elif phone == None: 
            index = state
        elif state == None: 
            index = phone
        elif state > phone: 
            index = state
        else: 
            index = phone

        for label in description[index+1:]:
            if (self.check_article_name(label) == True):  
                if (skiplist(label) == False): 
                    continue
                elif (stoplist(label) == False): 
                    return articles
                elif (endlist(label) == False):
                    return articles
                else: 
                    articles.append(label)
        return articles 
    
    def retrieve_prices(self, prices, description): 
        remove_label = []
        for label in description: 
            price = self.check_price(label)
            if (price != False): 
                prices.append(price)
                remove_label.append(label)

        for label in remove_label: 
            description.remove(label)

        return prices

    def retrieve_date(self, description): 
        for label in description: 
            if 'date' in label.lower(): 
                date = label.replace('Date:', '').replace('date:', '').replace('date','').replace('Date','').replace('date/time:', '')
                description.remove(label)
                return date
            elif 'pm' and '/' in label.lower():
                date_time = label.split( )
                return date_time[0]
            elif '/' and ':' in label.lower(): 
                return label
            elif '/' in label.lower():
                if label.replace('/','').isnumeric() == True: 
                    return label
        return None
            
    def remove_extra(self, articles, prices): 
        if len(articles) == len(prices): 
            return articles, prices
        elif len(articles) < len(prices): 
            return articles, prices[0:len(articles)]
        return articles, prices

    def find_address(self, description): 
        for index in range(len(description)):
            try:
                if 'MA' in description[index]:
                    return index
            except: 
                return -1 

    def sort_receipt(self, prices, articles): 
        remove_reg = []
        remove_sale = []

        for idx in range(len(articles)): 
            for discardlist in DISCARD_REG: 
                if discardlist in articles[idx].lower(): 
                    try: 
                        remove_reg.index(idx)
                    except: 
                        remove_reg.append(idx)
        
        for label in remove_reg[::-1]:
            articles.pop(label)
            prices.pop(label)

        for idx in range(len(prices)): 
            if '-' in prices[idx]: 
                remove_sale.append(idx)
        
        for label in remove_sale[::-1]: 
            prices.pop(label)
            articles.pop(label)
        
        return articles, prices

    def record_receipt(self, record, market, date, prices, articles): 
        articles, prices = self.sort_receipt(prices, articles)

        for i in range(len(articles)):
            try: 
                if 'T' in prices[i]: 
                    prices[i] = prices[i].replace('T', '')
                    prices[i] = round(float(prices[i]) + (float(prices[i]) * 0.0625), 2)
            except: 
                continue

            record.append({
                'Market': market,
                'Date': date, 
                'Item': articles[i],  
                'Price': prices[i]
            }) 
        return record
    
    def parse_response(self, gcloud_response, record):
        articles = []
        prices = []

        base_ann = gcloud_response.text_annotations[0]
        base_text = base_ann.description
        base_description = base_ann.description.splitlines()

        market = base_description[0]
        base_description.remove(market)
        self.remove_blacklist(base_description)

        date = self.parse_date(self.retrieve_date(base_description))
        self.retrieve_prices(prices, base_description)
        articles = self.retrieve_articles(articles, base_text, base_description)
        articles, prices = self.remove_extra(articles, prices)

        return self.record_receipt(record, market, date, prices, articles)