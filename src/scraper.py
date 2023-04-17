import pandas as pd
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OSX 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/71.0.3578.98 Safari/537.36", 
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
}


def get_response(url: str) -> BeautifulSoup:
    '''A function to return a BeautifulSoup object
    '''
    res = requests.get(url, headers=HEADERS)
    print(res.status_code)
    return BeautifulSoup(res.content, 'html.parser')


def collect_data(soup: BeautifulSoup) -> pd.DataFrame():
    # collect title
    title = soup.select('#productTitle')[0].text.strip()

    # Collect specifications
    eles = soup.select('#feature-bullets li span')
    info = [ele.text.strip() for ele in eles]

    try:
        keys_raw = soup.select('#prodDetails > div > div:nth-child(1) > div:nth-child(1) > div')[0].select('th')
        keys = [key.text.strip() for key in keys_raw]

        values_raw = soup.select('#prodDetails > div > div:nth-child(1) > div:nth-child(1) > div')[0].select('td')
        values = [values.text.strip() for values in values_raw]

        other_keys = [x.text.strip() for x in soup.select('#productDetails_db_sections')[0].select('th')]
        other_values = [x.text.strip() for x in soup.select('#productDetails_db_sections')[0].select('td')]

        keys.extend(other_keys)
        values.extend(other_values)
    except:
        pass

    # Current Price
    price = soup.select('#corePriceDisplay_desktop_feature_div > div.a-section.a-spacing-none.aok-align-center > span.a-price.aok-align-center.reinventPricePriceToPayMargin.priceToPay > span:nth-child(2) > span.a-price-whole')[0].text


    reviews_url = 'amazon.in' + soup.select('#reviews-medley-footer > div.a-row.a-spacing-medium > a')[0]['href']


    keys = ['product name', 'info', 'current price', 'reviews'] + keys
    values= [title, '\n'.join(info), price, reviews_url] + values

    info_df = pd.DataFrame({
        'keys': keys,
        'values': values
    })

    return info_df


def collect_reviews(url: str) -> pd.DataFrame():
    names = []
    reviews = []
    data_string = ""

    from tqdm import tqdm

    for i in tqdm(range(1, 12)):
        response = requests.get(url + f'?pageNumber={i}')
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, 'html.parser')

        for item in soup.findAll("a", {"data-hook": "review-title"}):
            data_string = data_string + item.get_text()
            names.append(data_string)
            data_string = ""  
        
        for item in soup.find_all("span", {"data-hook": "review-body"}):
            data_string = data_string + item.get_text()
            reviews.append(data_string)
            data_string = ""
        
    df = pd.DataFrame({
        'keys': names,
        'values': reviews
    })

    return df



