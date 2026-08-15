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
The ai assistant in VS code was used for minor help, but that was negligible. The only major AI usage was with styles.css, which I built from the base, but then used AI to enhance it largely. Essentially all other code, other than the css, was written by me or was taken from my flask pset in cs50.
