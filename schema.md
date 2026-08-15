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