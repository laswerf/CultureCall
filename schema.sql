-- Schema:

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    hash TEXT NOT NULL,
    points NUMERIC NOT NULL DEFAULT 10000.00
);

CREATE TABLE markets (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    title TEXT NOT NULL
);

CREATE UNIQUE INDEX idx_mkt_title ON markets (title);

CREATE TABLE history (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    sellerId INTEGER,
    marketId INTEGER,
    buyerId INTEGER,
    sharesCount INTEGER NOT NULL,
    executePrice NUMERIC NOT NULL,
    executeTime TEXT NOT NULL,
    FOREIGN KEY(marketId) REFERENCES markets(id),
    FOREIGN KEY(sellerId) REFERENCES users(id), 
    FOREIGN KEY(buyerId) REFERENCES users(id)
); -- executeTimes are ISO 8601 strings


CREATE TABLE liveOrders (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    marketId INTEGER,
    initiatorId INTEGER,
	sharesCount INTEGER NOT NULL,
    side TEXT NOT NULL CHECK (side IN ('BUY', 'SELL')),
	orderType TEXT NOT NULL,
	limitPrice NUMERIC,
    createdAt TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY(marketId) REFERENCES markets(id),
	FOREIGN KEY(initiatorId) REFERENCES users(id)
);

CREATE INDEX idx_live_matching ON liveOrders (marketId, side, orderType, limitPrice, createdAt);

CREATE TABLE portfolio (
    userId INTEGER NOT NULL,
    marketId INTEGER NOT NULL,
    sharesCount INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (userId, marketId),
    FOREIGN KEY (userId) REFERENCES users(id),
    FOREIGN KEY (marketId) REFERENCES markets(id)
);