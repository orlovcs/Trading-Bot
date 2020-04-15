class Stock:
   symbol = ""
   name = ""
   price = 0.0
   change = 0.0
   percent_change = 0.0

   def __init__(self, symbol, name, price, change, percent_change):
      self.symbol = symbol
      self.name = name
      self.price = float(price) #10.14
      self.change = float(change[1:]) #+0.97
      self.percent_change = float(percent_change[1:-1]) #+10.58%
