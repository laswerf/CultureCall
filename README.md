**CultureCall**
CultureCall is a prediction market app using virtual points (holding no real world value).
Users “bet” on shows, celebrities, etc. All markets must be instantiated with a wikipedia page (to which we will scrape the title) to prevent spam and will function like stock markets. Each user will get 10,000 points by default and there will be a leaderboard.

[Schema](/schema.md)

Simple Overview of features: user accounts, a portfolio, an order book, buy/sell limit orders, an actual matching algorithm, IPO shares, transaction history, market pricing, historical charts with date ranges, AJAX autocomplete, market creation backed by Wikipedia validation, seven-day volume rankings, and a leaderboard.

Key Subpages: 
/markets - list of top 10 markets by past 7 days trading volume 
/leaderboard - leaderboard of top users by points balance
/trade - look up markets with autocomplete, click on them to view stats + graph price, and place buy and sell orders
/create - create markets, we check that the markets are indeed not spam by using wikipedia api to make sure the titles are real things/people.
/about - basic description of how the site works

AI USAGE:
The ai assistant in VS code was used for minor help, but that was negligible. The only major AI usage was with styles.css, which I built from the base, but then used AI to enhance it largely. Essentially all other code, other than the css, and some JS for autocomplete with AJAX, was written by me or was taken from my flask pset in cs50.

SCHEMA: 

Here's the SQL schema:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL,
    points NUMERIC NOT NULL DEFAULT 10000.00
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE liveOrders (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    marketId INTEGER,
    initiatorId INTEGER,
        sharesCount INTEGER NOT NULL,
    side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
        limitPrice NUMERIC,
    createdAt TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(marketId) REFERENCES markets(id),
        FOREIGN KEY(initiatorId) REFERENCES users(id)
);
CREATE TABLE portfolio (
    userId INTEGER NOT NULL,
    marketId INTEGER NOT NULL,
    sharesCount INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (userId, marketId),
    FOREIGN KEY (userId) REFERENCES users(id),
    FOREIGN KEY (marketId) REFERENCES markets(id)
);
CREATE TABLE markets (    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,     title TEXT NOT NULL, ipo NUMERIC, ipo_shares_left INTEGER);
CREATE TABLE history (    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,    sellerId INTEGER,    marketId INTEGER,    buyerId INTEGER,    sharesCount INTEGER NOT NULL,    executePrice NUMERIC NOT NULL,    executeTime TEXT NOT NULL DEFAULT (datetime('now')),    FOREIGN KEY(marketId) REFERENCES markets(id),    FOREIGN KEY(sellerId) REFERENCES users(id),    FOREIGN KEY(buyerId) REFERENCES users(id));
```

As you can see, the schema consists of these tables:
- users for storing password hashes and points values and the like
- liveOrders for storing live orders, equivalent to a stock market order book. It has side (buy or sell), limit price, shares, and other key properties.
- portfolio for storing user positions, with userId, marketId, and sharesCount.
- markets for storing all market info, including title, ipo* price, and ipo shares left.
- history for storing all order history to see stuff like market volume in the past week for markets overview page

*The reason we have ipos for this is if we didn't there would be no way to buy shares of a market from someone

Market creation:
When users create markets, they must use title's that are avaliable as corresponding articles on the website https://wikipedia.org.
We do this to prevent spam, and the method we use is calling their title api and checking for a 404 error or not based on the market title. 
Wikipedia makes this very easy as they allow for redirecting market names (ex. "/Harvard" > "/Harvard_University") so users can have an easier chance just typing well known topics.

Orders:
When users submit an order with a limitPrice, it "refreshes" and the server fills all orders that can be filled (recursive through lowestSeller v. Highestbuyer)
and handles race conditions properly, as well as partial order fills (ex. seller 50 shares, buyer 30 shares, 30 share transaction can still take place)

Quote Search:
Using AJAX and 

Leaderboards:
The leaderboard page sorts by liquid points balance to the top players, allowing for some social credit or bragging rights!
I decided to only use liquid balance, and not balance added to value of all assets as with low liquidity the users could very easily make it look like they are worth far more than they actually are. For example, if a user with 100,000.00 points held 100,000 shares of a market and sold only one to their friend for 10,000 points, it would appear that they would be worth 1 billion points! But this would obviously be manipulation and hence our strategy for leaderboards.