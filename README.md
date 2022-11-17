# StockMarketProject
Implementation of the 6WTrigger Algorithm

program to implement 6 Week Trigger algorithm to buy stocks.
Given weekly data on S&P500 stocks, outputs list of weeks that satisfy that trigger
The conditions:
  1. The closing price of that week must be greater than the opening price
  2. The low of that week must be lower than any low in the last 5 weeks "hence the name 6 week trigger"
  3. 
Also outputs a list of metrics for each stock
More details within the python file
