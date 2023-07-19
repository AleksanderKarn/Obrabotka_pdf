url = 'https://prices.autoins.ru/priceAutoPublicCheck/api/spareprice'

header = {
  "headers": {
    "accept": "*/*",
    "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "cache-control": "no-cache",
    "content-type": "application/json",
    "pragma": "no-cache",
    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "cookie": "_ym_uid=1686747327858288950; _ym_d=1686747327",
    "Referer": "https://prices.autoins.ru/priceAutoPublicCheck/averagePrices",
    "Referrer-Policy": "strict-origin-when-cross-origin"
  },
  "method": "POST"
}

car_ids = {
    'JAC': '77',
    'KIA': '4',
    'NISSAN': '6',
    'SKODA': '12',
    'TOYOTA': '2',
    'Volkswagen': '7',
    'CHERY': '30',
    'HYUNDAI': '3',
    'VW': '7'

}

car_list = ['CHERY', 'HYUNDAI', 'JAC', 'KIA', 'NISSAN', 'SKODA', 'TOYOTA', 'VOLKSWAGEN', 'VW']



username = ''
password = ''
email_server = "imap.mail.ru"
directory = 'Obrabotka_pdf/'
