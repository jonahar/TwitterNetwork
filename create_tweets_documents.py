import os
import re
import json

data_dir = '/cs/labs/avivz/jonahar/Twitter/bitcoin_btc_data_dir'
documents_dir = '/cs/labs/avivz/jonahar/Twitter/bitcoin_btc_documents'


def tweet_text(t):
    """
    return the text of the given tweet object
    """
    if 'extended_tweet' in t:
        return t['extended_tweet']['full_text']
    elif 'full_text' in t:
        return t['full_text']
    else:
        return t['text']


def clean_text(text):
    text = re.sub(r'\b(?:(?:https?|ftp)://)?\w[\w-]*(?:\.[\w-]+)+\S*', ' ', text.lower())
    words = re.findall(r'[a-z]+', text)
    return ' '.join(words)


for scr_name in os.listdir(data_dir):
    sub_dir = os.path.join(data_dir, scr_name)
    if os.path.isdir(sub_dir):
        tweets_file = os.path.join(sub_dir, 'tweets')
        if os.path.isfile(tweets_file):
            # open a new document file for this user
            document_path = os.path.join(documents_dir, scr_name)
            with open(tweets_file) as f, open(document_path, mode='w') as document:
                for line in f:
                    t = json.loads(line[:-1])
                    text = tweet_text(t)
                    text = clean_text(text)
                    document.write(text)
                    document.write(' ')
