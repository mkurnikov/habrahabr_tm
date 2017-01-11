import re
from string import punctuation

import requests
from flask import Flask
from parsel import Selector
from yarl import URL


app = Flask(__name__)

BASE_URL = 'https://habrahabr.ru/'


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    base = URL(BASE_URL)
    full_url = base / path
    
    html = requests.get(full_url).text
    sel = Selector(html)
    
    tm_symbol = '™'
    new_lines = []
    text = sel.css('div.content').xpath('./text()').extract()
    for line in text:
        line = line.strip()
        if len(line) == 0:
            continue
        
        new_line = []
        for word in line.split():
            match = re.search('^[a-zA-Zа-яА-Я]{6}$', word.strip(punctuation))
            
            new_word = word
            if match:
                new_word = word.replace(match.group(0), match.group(0) + tm_symbol)
            
            new_line.append(new_word)
        
        new_lines.append(' '.join(new_line))
    
    output = str(full_url) + '\n'
    output += len(str(full_url)) * '^' + '\n'
    output += '\n'.join(new_lines)
    return output


if __name__ == '__main__':
    from argparse import ArgumentParser
    
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=None, help='Port.')
    parser.add_argument('--base', default='https://habrahabr.ru/', help='Base url.')
    args = parser.parse_args()
    
    BASE_URL = args.base
    app.run(port=args.port)
