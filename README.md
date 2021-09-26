# Crypto Position Dasboard
Provides a basic UI for monitoring the current market price of many cryptocurrencies at once, as well as the user's positions in those currencies.  

## Background
In stock and currency trading, "position" refers to the average price at which the investor acquired the stock or currency. The current price relative to the investor's position determines whether the investor would make or lose money by selling. Modern cryptocurrency markets allow investors to invest in many currencies at once. Some currencies are more volatile than others, and can commonly rise or fall in value by 2-10% in a matter of minutes. This offers the opportunity to make (or lose) money quickly, and if the investor is holding several such currencies at once, it can be difficult to monitor all of them at once and make beneficial decisions quickly.

## Using the Dashboard
On the left, the user can select any number of available cryptocurrencies to monitor. They can enter their position in each currency and a target price. The ratio of target price to position is calculated as a convenience. Once the user selects currencies to monitor, current market data will appear for each currency on the right. The user's position, the current price, and the ratio of the current price to the user's position is shown. Clicking "save" at the bottom will save the user's current inputs, which can be loaded next time the program is opened.  
![Dashboard screenshot](Crypto%20Position%20Dashboard%20screenshot.JPG)

## The Code
Current cryptocurrency market data is obtained with the Coinbase Pro API. Whenever a price changes on the Coinbase market, that is reflected immediately in the dashboard. Any of the currencies available on Coinbase can be monitored, but I limit it here to 15. The UI is created with a rudimentary UI library called tkinter. Tkinter is extremely simple and fast to use for basic input and text display, I would not use it for anything else.
