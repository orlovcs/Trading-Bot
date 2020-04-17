from datetime import datetime, timedelta
from pytz import timezone
import statistics
import pandas as pd


min_price = 6
max_price = 26
#cannot hold a small amount of stocks for this strategy, they need to balance out
stock_held_per_day = 150


def shares_to_buy(ratings, equity):
   ratings_sum = ratings['rating'].sum()
   shares_amount = {}
   #_ means the variable is a placeholder and won't be used
   for _, row in ratings.iterrows():
      #indicate for each symbol how many shares should be bought
      shares_amount[row['symbol']] = int(row['rating']/ratings_sum * equity/row['price'])
   return shares_amount


def asset_values(api, assets, on_date, market_open):
   #no assets
   if len(assets.keys()) == 0:
      return 0
   value = 0
   print(len(assets.keys()))
   on_date = on_date.strftime('%Y-%m-%dT%H:%M:%S.%f-04:00')
   barset = api.get_barset(
      symbols = assets.keys(),
      timeframe='day',
      limit = 1,
      end = on_date
   )
   print_idx = 0
   for symbol in assets:
      if market_open:
         value += assets[symbol] * barset[symbol][0].o
         if print_idx < 4:
            print(symbol+": "+str(assets[symbol])+" shares x "+str(barset[symbol][0].o)+" = "+str(assets[symbol] * barset[symbol][0].o))            
      else:
         value += assets[symbol] * barset[symbol][0].c
         if print_idx < 4:
            print(symbol+": "+str(assets[symbol])+" shares x "+str(barset[symbol][0].c)+" = "+str(assets[symbol] * barset[symbol][0].c))
      print_idx+=1
   if print_idx >= 4:
      print("...")
   return value


def rate_deviation(api, request_time):
   #assets available to trade, each object status, symbol, exchange, etc.
   assets = api.list_assets()
   #make sure asset is tradable
   assets = [asset for asset in assets if asset.tradable]
   ratings = pd.DataFrame(columns=['symbol', 'rating', 'price'])

   current_time = None
   if request_time is not None:
      current_time = request_time.date().strftime('%Y-%m-%dT%H:%M:%S.%f-04:00')

   #request data for 100 stocks at a time
   batch_size = 200

   #consider the last 5 days
   windows_size = 5
   index = 0
   while index < len(assets):
      #list of symbols for every batch_size
      symbols_batch = [asset.symbol for asset in assets[index:index+batch_size]]
      batch_bars = api.get_barset(
         symbols=symbols_batch,
         timeframe = 'day',
         limit = windows_size,
         end = current_time
      )

      for symbol in symbols_batch:
         #for every symbol in the batch select its bar chart
         bars = batch_bars[symbol]
         #check that we have a window_size days worth of bars
         if len(bars) == windows_size:
            #if gap from present is more than a day we can't use this data
            gap_from_last_bar = request_time - bars[-1].t.to_pydatetime().astimezone(timezone('EST'))
            if gap_from_last_bar.days > 1:
               continue

            #get last closing price
            last_price = bars[-1].c
            if last_price >= min_price and last_price <= max_price:
               #subtract closing price of first bar from last
               total_price_change = last_price - bars[0].c
               past_volumes = [bar.v for bar in bars[:-1]]
               past_volumes_stdev = statistics.stdev(past_volumes)
               #if stdev is 0 of past volumes, data likley isnt correct
               if past_volumes_stdev == 0:
                  continue

               #momentum is the speed of price change in a stock, it needs to be normalized with rate of change
               #rate of change = (current_price - initial_price)/initial_price
               normalized_momentum = total_price_change / bars[0].c

               #if volume data is fine, compare it with the volume change from yesterday
               volume_change = bars[-1].v - bars[-2].v
               #find number of volume change stdevs in volume change
               volume_change_deviations = volume_change / past_volumes_stdev

               #rating will be a combination of normalized momentum and day old volume deviations
               rating = normalized_momentum * volume_change_deviations
               #append to main pd dataframe if rating is above 0
               if rating > 0:
                  ratings = ratings.append({
                     'symbol': symbol,
                     'rating': rating,
                     'price': last_price
                  }, ignore_index=True)
      index += batch_size
   #sort the df by the ratings
   ratings = ratings.sort_values('rating', ascending=False)
   #reset the index to start from the highest rated stock downwards
   ratings = ratings.reset_index(drop=True)
   return ratings[:stock_held_per_day]



def backtest(api):

   starting_cash = input('Backtesting starting cash ')
   days_backwards = input('Backtesting days backwards ')
   min_price = input('Stock min price ')
   max_price = input('Stock max price ')

   equity = float(starting_cash)
   starting_equity = equity
   days_backwards = int(days_backwards)


   now = datetime.now(timezone('EST'))
   test_beginning = now - timedelta(days=days_backwards)

   #skip over non open market days
   calendars = api.get_calendar(
      start = test_beginning.strftime("%Y-%m-%d"),
      end = now.strftime("%Y-%m-%d")
   )
   day_idx = 0
   previous_equity = starting_equity
   assets_bought = {}
   for cal in calendars:
      
      #EACH DAY STEPS
      print("Beginning of " + str(cal.date))
      
      #1. Sell off overnight held assets immediately at open market price
      #Add the profits to our current portfolio
      asset_value = asset_values(api, assets_bought, cal.date, True)
      print("Portfolio cash is " + str(equity))
      print("All assets sold on open for a total of "+str(asset_value))
      equity += asset_value
      print("Portfolio is valued at " + str(equity))
      print("Portfolio change since yesterday is " + str(((equity-previous_equity)/previous_equity)*100.0) + "%")

      #2. Calculate which stocks should be bought today
      #Calculate how many shares of each stock should be bought
      ratings = rate_deviation(api, timezone('EST').localize(cal.date))
      assets_bought = shares_to_buy(ratings, equity)
      
      #record the current profits
      previous_equity = equity
      #don't sell on the last day
      if day_idx == len(calendars) - 1:
         break

      #3. For each stock, buy the appropriate amount of shares and hold it overnight
      for _, row in ratings.iterrows():
         amount_of_shares = assets_bought[row['symbol']]
         cost_of_shares = row['price'] * amount_of_shares
         equity -= cost_of_shares
      print("Stocks to be held overnight: ")
      asset_value = asset_values(api, assets_bought, cal.date, False)
      print("All assets bought on close for a total of "+str(asset_value))
      print("End of " + str(cal.date))
      print(" ")
      
      #4. Assets bought today will now be held overnight and sold on market open the next day
      day_idx += 1
   spy_bars = api.get_barset(
      symbols = 'SPY',
      timeframe = 'day',
      start = (calendars[0].date).strftime('%Y-%m-%dT%H:%M:%S.%f-04:00'),
      end = (calendars[1].date).strftime('%Y-%m-%dT%H:%M:%S.%f-04:00')
   )
   print("SPY close on start date: " + str(spy_bars['SPY'][0].c))
   print("SPY close on end date: " + str(spy_bars['SPY'][-1].c))
   print("Portfolio cash is " + str(equity))
   print("Portfolio total change is " + str(((equity-starting_equity)/starting_equity)*100.0) + "%")


