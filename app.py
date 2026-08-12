import os
from datetime import datetime

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, pts

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["pts"] = pts

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///culture.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

def getMarketPrice(mktId):
    check = db.execute("SELECT * FROM markets WHERE id = ?", mktId)
    if not check or not check[0]:
        return None
    check = check[0]
    ipo = check["ipo"]
    left = check["ipo_shares_left"]
    check = db.execute("SELECT * FROM history WHERE marketId = ? ORDER BY executeTime DESC", mktId)
    if check and check[0]:
        check = check[0]["executePrice"]
        if ipo > check:
            return ipo
        return check
    elif left > 0:
        return ipo
    else:
        print("No price!")
        return None

def getMarketName(mktId):
    check = db.execute("SELECT * FROM markets WHERE id = ?", mktId)
    if not check or not check[0]:
        raise Exception("Market not found.")
    check = check[0]
    return check["title"]
    
def refreshOrders(marketId):
    db.execute("BEGIN IMMEDIATE TRANSACTION")
    market = db.execute("SELECT * FROM markets WHERE id = ?", marketId)[0]
    left = market["ipo_shares_left"]
    ipo = market["ipo"]

    openOrders = db.execute("SELECT * FROM liveOrders WHERE marketId = ? ORDER BY createdAt DESC", marketId)

    def continueRefresh():
        lowestSeller = db.execute("SELECT * FROM liveOrders WHERE marketId = ? AND side='SELL' ORDER BY createdAt DESC LIMIT 1", marketId)
        highestBuyer = db.execute("SELECT * FROM liveOrders WHERE marketId = ? AND side='BUY' ORDER BY createdAt DESC LIMIT 1", marketId)
        print(left, ipo, highestBuyer)
        if left > 0 and highestBuyer and highestBuyer[0] and ipo <= highestBuyer[0]["limitPrice"]:
            buyer = highestBuyer[0]
            shares = min(left, buyer["sharesCount"])
            total = ipo * shares

            # IPO shares are sold directly from the market, not from a user's portfolio.
            db.execute("UPDATE markets SET ipo_shares_left = ipo_shares_left - ? WHERE id = ?", shares, marketId)
            db.execute("UPDATE users SET points = points - ? WHERE id = ?", total, buyer["initiatorId"])

            current = db.execute("SELECT sharesCount FROM portfolio WHERE userId = ? AND marketId = ?", buyer["initiatorId"], marketId)
            if current and current[0]:
                db.execute("UPDATE portfolio SET sharesCount = sharesCount + ? WHERE userId = ? AND marketId = ?", shares, buyer["initiatorId"], marketId)
            else:
                db.execute("INSERT INTO portfolio (userId, marketId, sharesCount) VALUES (?, ?, ?)", buyer["initiatorId"], marketId, shares)

            if buyer["sharesCount"] == shares:
                db.execute("DELETE FROM liveOrders WHERE id = ?", buyer["id"])
            else:
                db.execute("UPDATE liveOrders SET sharesCount = sharesCount - ? WHERE id = ?", shares, buyer["id"])

            db.execute("INSERT INTO history (sellerId, marketId, buyerId, sharesCount, executePrice, executeTime) VALUES (?, ?, ?, ?, ?, datetime('now'))", None, marketId, buyer["initiatorId"], shares, ipo)

            return True

        if not lowestSeller or not lowestSeller[0] or not highestBuyer or not highestBuyer[0]:
            print("There isn't a buyer and a seller for this market!")
            return False

        lowestSeller = lowestSeller[0]
        highestBuyer = highestBuyer[0]

        sellingPrice = lowestSeller["limitPrice"]
        buyingPrice = highestBuyer["limitPrice"]

        if sellingPrice > buyingPrice:
            return False

        sellTime = datetime.fromisoformat(lowestSeller["createdAt"])
        buyTime = datetime.fromisoformat(highestBuyer["createdAt"])

        sellPrice = 0

        if sellTime < buyTime:
            sellPrice = lowestSeller["limitPrice"]
        else:
            sellPrice = highestBuyer["limitPrice"]

        amttoSell = lowestSeller["sharesCount"]
        amttoBuy = highestBuyer["sharesCount"]

        totalShares = 0
        if amttoSell <= amttoBuy: # if the buyer is willing to pay for all storage
            totalShares = amttoSell # thus, we can treat amt to sell as total to be sold
        else:
            totalShares = amttoBuy # otherwise, the max we can sell is the max they are willing to buy

        total = sellPrice * totalShares

        sellid = lowestSeller["id"]
        buyid = highestBuyer["id"]

        # -- Update all database tables and record transaction -- #

        # update liveorders sell side
        # if the seller was selling all of their selling to this person, just delete it from their portfolio.
        if amttoSell <= amttoBuy:
            db.execute("DELETE FROM portfolio WHERE userId = ? AND marketId = ?", sellid, marketId)
            # remove the order from liveorders since its been filled entirely
            db.execute("DELETE FROM liveOrders WHERE side = 'SELL' AND initiatorId = ? AND marketId = ?", sellid, marketId)
            if (amttoSell == amttoBuy):
                # we can remove the corresponding buy order too
                db.execute("DELETE FROM liveOrders WHERE side = 'BUY' AND initiatorId = ? AND marketId = ?", buyid, marketId)
            else:
                # just decrement the corresponding buy order since its not done in full
                db.execute("UPDATE liveOrders SET sharesCount = sharesCount - ? WHERE side = 'BUY' AND initiatorId = ? AND marketId = ?", buyid, marketId)
        else: # if they were only selling some because less liquidity, just remove some from their share count.
            db.execute("UPDATE portfolio SET sharesCount = sharesCount - ? WHERE userId = ? AND marketId = ?", totalShares, sellid, marketId)
            # update liveorders since order has been partially filled
            db.execute("UPDATE liveOrders SET sharesCount = sharesCount - ? WHERE side = 'SELL' AND initiatorId = ? AND marketId = ?", totalShares, sellid, marketId)
            # delete buy order since it was filled entirely
            db.execute("DELETE FROM liveOrders WHERE side = 'BUY' AND initiatorId = ? AND marketId = ?", buyid, marketId)

        # give the seller their money the other person paid
        db.execute("UPDATE users SET points = points + ? WHERE id = ?", total, sellid)

        # add the stock to the buyer's portfolio and take the points from their balance for it
        db.execute("UPDATE portfolio SET points = points - ? WHERE id = ?", total, buyid)
        db.execute("INSERT INTO portfolio VALUES (?, ?, ?)", buyid, marketId, totalShares)

        # add transaction to history table
        db.execute("INSERT INTO history (sellerId, marketId, buyerId, sharesCount, executePrice) VALUES (?, ?, ?, ?, ?)", sellid, marketId, buyid, totalShares, sellPrice)

        return True
        
    while continueRefresh() == True:
        continue

    db.execute("COMMIT")



@app.route("/")
@login_required
def index():
    balance = db.execute("SELECT points FROM users WHERE id = ?", session["user_id"])[0]["points"]
    portfolio = db.execute("SELECT * FROM portfolio WHERE userId = ?", session["user_id"])
    open = db.execute("SELECT * FROM liveOrders WHERE initiatorId = ?", session["user_id"])
    history = db.execute("SELECT * FROM history WHERE sellerId = ? OR buyerId = ? ORDER BY executeTime DESC", session["user_id"], session["user_id"])
    print(history)
    for transaction in history:
        if transaction["sellerId"] == session["user_id"]:
            transaction["side"] = "Sell"
        else:
            transaction["side"] = "Buy"
        transaction["market"] = db.execute("SELECT * FROM markets WHERE id = ?", transaction["marketId"])[0]["title"]
    return render_template("index.html", points=pts(balance), portfolio=portfolio, open=open, price=getMarketPrice, pts=pts, mktName=getMarketName, history=history)

@app.route("/cancel", methods=["POST"])
@login_required
def cancel():
    market = request.form.get("market")
    db.execute("BEGIN IMMEDIATE TRANSACTION")
    db.execute("DELETE FROM liveOrders WHERE (initiatorId = ?) AND marketId = ?", session["user_id"], market)
    db.execute("COMMIT")
    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == 'GET':
        return render_template("signup.html")
    else:
        if not request.form.get("password") or request.form.get("confirmation") != request.form.get("password"):
            return apology("Password incorrectly entered or not entered at all", 400)
        if not request.form.get("username"):
            return apology("Please fill out all fields.", 400)
        if len(db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username"))) > 0:
            return apology("Username already taken", 400)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get(
            "username"), generate_password_hash(request.form.get("password")))
    return redirect("/")

@app.route("/autocomplete")
def autocomplete():
    query = request.args.get("q")
    results = db.execute("SELECT * FROM markets WHERE title LIKE '%' || ? || '%' LIMIT 5", query)
    print(results)
    return render_template("autocomplete.html", markets=results, price=getMarketPrice)

@app.route("/trade", methods=["GET", "POST"])
@login_required
def trade():
    mktTitle = request.args.get("market")
    if request.method == "POST":
        mktTitle = request.form.get("mktTitle")
        action = request.form.get("action")
        amount = request.form.get("amount")
        price = request.form.get("price")
        if not amount or not action or not action in ["BUY", "SELL"] or int(amount) <= 0 or not price or int(price) <= 0:
            return apology("All fields were not filled out correctly.", 403)
        already = db.execute("SELECT * FROM liveOrders WHERE initiatorId = ?", session["user_id"])
        if len(already) > 0:
            return apology("You already have open orders for this market. Please cancel them before making more.", 403)
        id = db.execute("SELECT * FROM markets WHERE title = ?", mktTitle)
        if not id or not id[0] or not id[0]["id"]:
            return apology("Market not found", 403)
        id = id[0]["id"]
        db.execute("INSERT INTO liveOrders (initiatorId, marketId, sharesCount, side, limitPrice) VALUES (?, ?, ?, ?, ?)", session["user_id"], id, amount, action, price)
        print(id, mktTitle)
        refreshOrders(id)
        return redirect("/")
    elif mktTitle:
        mkt = db.execute("SELECT * FROM markets WHERE title = ?", mktTitle)[0]
        mktId = mkt["id"]
        left = mkt["ipo_shares_left"]
        ipo = mkt["ipo"]
        print(mktId)
        mktPrice = getMarketPrice(mktId)
        if not mktPrice:
            return apology("Market does not exist!", 403)
        lowestSeller = db.execute("SELECT * FROM liveOrders WHERE marketId = ? AND side='SELL' ORDER BY createdAt DESC LIMIT 1", mktId)
        if lowestSeller and lowestSeller[0]:
            lowestSeller = lowestSeller[0]["limitPrice"]
        else:
            lowestSeller = None
        highestBuyer = db.execute("SELECT * FROM liveOrders WHERE marketId = ? AND side='BUY' ORDER BY createdAt DESC LIMIT 1", mktId)
        if highestBuyer and highestBuyer[0]:
            highestBuyer = highestBuyer[0]["limitPrice"]
        else:
            highestBuyer = None
        return render_template("quote.html", mktTitle=mktTitle, mktPrice=mktPrice, pts=pts, left=left, ipo=ipo, lowestSeller=lowestSeller, highestBuyer=highestBuyer)
    else:
        return render_template("trade.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")