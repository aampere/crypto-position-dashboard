# Crypto Position Dasboard
Provides a basic UI for monitoring the current market price of many cryptocurrencies at once, as well as the user's positions in those currencies.  

## Background
In stock and currency trading, "position" refers to the average price at which the investor acquired the stock or currency. The current price relative to the investor's position determines whether the investor would make or lose money by selling. Modern cryptocurrency markets allow investors to invest in many currencies at once. Some currencies are more volatile than others, and can commonly rise or fall in value by 2-10% in a matter of minutes. This offers the opportunity to make (or lose) money quickly, and if the investor is holding several such currencies at once, it can be difficult to monitor all of them at once and make beneficial decisions quickly.

## Using the Dashboard
On the left, the user can select any number of available cryptocurrencies to monitor. They can enter their position in each currency and a target price. The ratio of target price to position is calculated as a convenience. Once the user selects currencies to monitor, current market data will appear for each currency on the right and update live as markets move. The user's position, the current price, and the ratio of the current price to the user's position is shown. Clicking "save" at the bottom will save the user's current inputs, which can be loaded next time the program is opened. The user can edit the `pairs.json' file to change which currencies are avaiable to display, and how many to display.  
![Crypto Position Dashboard screenshot](https://user-images.githubusercontent.com/66134580/135137302-4fc8a8af-c227-4295-bc77-0bac944291c1.JPG)

## Setup
- Create and activate virtual environment `crypto-position-dashboard-venv`.
- Install requirements: `pip install -r requirements.txt`
- This program requires Coinbase Pro API keys. See https://help.coinbase.com/en/pro/other-topics/api/how-do-i-create-an-api-key-for-coinbase-pro for how to create API keys (requires a Coinbase Pro account) and https://docs.pro.coinbase.com/ for API documentation.
- Create a `.env` file, which will save your API keys as environment variables read by the program, containing:
  > coinbase_key = "your_key"  
  > coinbase_b64secret = "your_b64secret"  
  > coinbase_passphrase = "your_passphrase"  
- Run `cryptopositiondash.py' to start the dashboard.
