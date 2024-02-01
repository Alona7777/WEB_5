import sys
from datetime import datetime, timedelta

import httpx
import asyncio
import platform



class HttpError(Exception):
    pass


async def request(url: str):
    timeout = httpx.Timeout(10.0, read=None)
    async with httpx.AsyncClient() as client:
        r = await client.get(url, timeout=timeout)
        if r.status_code == 200:
            result = r.json()
            return result
        else:
            raise HttpError(f"Error status: {r.status_code} for {url}")
        
async def get_response(shift):
    try:
        response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
        return parse_result(response, shift)
    except HttpError as err:
        print(err)
        return None

        
def parse_result(response, shift):
    res = response.get('exchangeRate')
    new_result = {}  
    for el in res:
        for k, v in el.items():
            if v == 'EUR':
                new_result['EUR'] = el
            if v == 'USD':
                new_result['USD'] = el
    eur_case = new_result.get('EUR')
    usd_case = new_result.get('USD')
    result_dict = {
        shift: 
        {'EUR': 
         {'sale': eur_case.get('saleRateNB'),
          'purchase': eur_case.get('purchaseRateNB')}, 
          'USD': 
          {'sale': usd_case.get('saleRateNB'),
           'purchase': usd_case.get('purchaseRateNB')}}
           }
        
    return result_dict

def user_input(value: str):
    if value.isdigit():
        value = int(value)
        if value <= 10:
            return value
    else:
        print('можна дізнатися курс валют не більше, ніж за останні 10 днів')
        day = input('ви повінні ввести ціле число, не більше 10 >>>>>  ')
        return user_input(day)

                
async def main(index_day):
    index_day = user_input(index_day)
    result = []
    date = datetime.now()
    shift = date.strftime('%d.%m.%Y')
    result.append(await get_response(shift))
    for n in range(1, index_day+1):
        d = datetime.now() - timedelta(n)
        shift = d.strftime("%d.%m.%Y")
        result.append(await get_response(shift))

    return result

if __name__ == '__main__':
    r = asyncio.run(main(sys.argv[1]))
    print(r)
