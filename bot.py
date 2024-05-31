import requests
import os
from sickle import Sickle
from datetime import datetime

def scrape_arxiv():
    sickle = Sickle('https://export.arxiv.org/oai2')
    today = datetime.today().strftime('%Y-%m-%d')

    params = {
        'metadataPrefix': 'arXiv',
        'from': today,
        'until': today,
        'set': 'physics:quant-ph'
    }

    return sickle.ListRecords(**params)

def prepare_message(all_papers, keywords):

    messages = []
    titles = []

    for record in all_papers:
        header = record.header
        metadata = record.metadata

        title = metadata.get('title', [''])[0]
        abstract = metadata.get('abstract', [''])[0]
        keynames = metadata.get('keyname', [''])
        forenames = metadata.get('forenames', [''])
        if len(keynames) == len(forenames):
            authors = ', '.join([f"{forename} {keyname}" for forename, keyname in zip(forenames, keynames)])
        else:
            authors = ', '.join(keynames)

        if any(keyword.lower() in (title + abstract).lower() for keyword in keywords):

            titles.append(title)

            message = f"Authors: {authors}\n URL: {'https://arxiv.org/abs/'+header.identifier.split(':')[-1]}\n Abstract: {abstract}"
            messages.append(message)

    return titles, messages

def get_papers(keywords):
    all_papers = scrape_arxiv()
    messages = prepare_message(all_papers, keywords)
    return messages

def post_message(title, message, webhook):

    
    payload = {
        "username": "ArXiv Bot",
        "embeds": [
            {
                "title": title,
                "description": message,
            }
        ]
    }

    with requests.post(webhook, json=payload) as response:
        print(response.status_code)

project1 = {'webhook': os.getenv('PROJECT1_WEBHOOK'), 'keywords': ['metrology', 'sensing']}
project2 = {'webhook': os.getenv('PROJECT2_WEBHOOK'), 'keywords': ['machine learning', 'kernel methods']}
today = datetime.today().strftime('%Y-%m-%d')

for project in [project2]:
    first_title = f"Good morning! I hope you have a wonderful day!"
    first_message = f"Here are some papers from {today} that contain the keywords: {', '.join(project['keywords'])}."
    post_message(first_title, first_message, project['webhook'])

    titles, messages = get_papers(project['keywords'])
    for title, message in zip(titles, messages):
        post_message(title, message, project['webhook'])