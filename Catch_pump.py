import hmac
import hashlib
import requests
import time
from urllib.parse import urlencode
BASE_URL = "https://api.binance.com"



class Binance():
  BASE_URL = "https://api.binance.com"
  recv_window = 5000

  def __init__(self,key,secret):
      self.key = key
      self.secret = secret
    

  def percentage(self,percent,whole):
    return (float(percent) * float(whole)) / 100.0


  def currentPrice(self,symbol):
      path= self.BASE_URL+"/api/v3/ticker/price"
      param={"symbol":symbol}
      return self.get_no_sign(path,param)["price"]    

  def get_asset_ammount(self,asset):             # SPOT 
    path = self.BASE_URL+"/api/v3/account"
    for ass in self._get(path)["balances"]:
      if ass["asset"]==asset:
          return ass            
       

  def market_buy(self,symbol,price):
    path= self.BASE_URL+"/api/v3/order" 
    param ={"symbol":symbol,"side":"BUY",\
        "type":"MARKET","quoteOrderQty":self._format(price)} 
    return self._post(path,param)

  def market_sell(self,symbol,quantity):
    path= self.BASE_URL+"/api/v3/order" 
    param ={"symbol":symbol,"side":"SELL",\
        "type":"MARKET","quantity":self._format(quantity)}
    return self._post(path,param)

  def sign(self, params={}):
    data = params.copy()
    ts = int(1000 * time.time()) 
    data.update({"timestamp": ts})
    h = urlencode(data)
    b = bytearray()
    b.extend(self.secret.encode())
    signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    data.update({"signature": signature})
    return data


  def get_no_sign(self, path, params={}):
    query = urlencode(params)
    url = "%s?%s" % (path, query)
    return requests.get(url, timeout=30, verify=True).json()

  def _get(self, path, params={}):
    ts = int(1000 * time.time()) 
    params.update({"timestamp": ts})
    params.update({"recvWindow": self.recv_window})
    query = urlencode(self.sign(params))
    url = "%s?%s" % (path, query)
    header = {"X-MBX-APIKEY": self.key}
    return requests.get(url, headers=header,timeout=30,\
      verify=True).json()

  def _post(self, path, params={}):
    ts = int(1000 * time.time()) 
    params.update({"timestamp": ts})
    params.update({"recvWindow": self.recv_window})
    query = urlencode(self.sign(params))
    header = {"X-MBX-APIKEY": self.key}
    return requests.post(path, headers=header, data=query,\
            timeout=30, verify=True).json()

B = Binance("1","2")


if __name__ == "__main__":
  btc_amount = B.get_asset_ammount("BTC")["free"]

  buy_amount = input("How much BTC do you want to buy with? (percent of all your BTC spot wallet, without %): ")
  asset = input("ASSET to pump (capital letter): ")

  symbol = asset + "BTC"
  buy_amount = B.percentage(buy_amount,btc_amount)     

  order_buy = B.market_buy(symbol, buy_amount)   

  bought_fiat = float(order_buy["price"])
  bought_quantity = float(order_buy["executedQty"])
  print(order_buy["status"])
  print(">>> %s %s bought at %s btc" % (order_buy["executedQty"],asset,order_buy["price"]))
  print("-"*50)

  time.sleep(1)

  sell_order = B.market_sell(symbol,bought_quantity)
  sell_price = B.currentPrice(symbol)
  print("We sell at %s" % (sell_price))
