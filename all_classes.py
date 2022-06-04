import requests as re
import pandas as pd
import json


class Authentication:
    def __init__(self, login, password):
        self.login = login
        self.password = password

    @staticmethod
    def auth(login, password):
        s = re.Session()
        s.get('https://passport.moex.com/authenticate', auth=(login, password))
        headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv: 66.0)Gecko/20100101 Firefox/66.0"}
        cookies = {'MicexPassportCert': s.cookies['MicexPassportCert']}
        return headers, cookies


class DataDownload:
    def __init__(self, securities, date_from, date_till, headers, cookies):
        self.securities = securities
        self.date_from = date_from
        self.date_till = date_till
        self.headers = headers
        self.cookies = cookies

    @staticmethod
    def go_data(securities, date_from, date_till, headers, cookies):
        url = f'https://iss.moex.com/iss/analyticalproducts/futoi/securities/' \
              f'{securities}.json?from={date_from}&till={date_till}'
        req = re.get(url, headers=headers, cookies=cookies)
        dataj = json.loads(req.text)
        df = pd.DataFrame(dataj['futoi']['data'], columns=dataj['futoi']['columns'])
        df['pos_short'] = df['pos_short'] * -1
        df["tradedate"] = df[['tradedate', 'tradetime']].apply(lambda x: ' '.join(x), axis=1)
        del df["tradetime"]
        df = df.sort_values(by=['systime']).reset_index(drop=True)
        assert isinstance(df, object)
        return df
