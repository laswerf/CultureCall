**CultureCall**
CultureCall is a prediction market app using virtual points (holding no real world value).
Users “bet” on shows, celebrities, etc. All markets must be instantiated with a wikipedia page (to which we will scrape the title) to prevent spam and will function like stock markets. Each user will get 10,000 points by default and there will be a leaderboard.

[Schema](/schema.md)

Key Components:
/markets - list of top 10 markets by past 7 days trading volume
/leaderboard - leaderboard of top users by points balance
/trade - look up markets with autocomplete, click on them to view stats + graph price, and place buy and sell orders
/create - create markets, we check that the markets are indeed not spam by using wikipedia api to make sure the titles are real things/people.

