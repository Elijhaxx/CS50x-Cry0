# Libraries
import os

from cs50 import SQL
from flask import Flask, render_template, redirect, request, session, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from assist import login_required, apology, lookup, usd, get_symbol_by_name
from model import predict_crypto_price


# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite
db = SQL("sqlite:///cryo.db")


# Prevent client's web browser from caching server responses
@app.after_request
def after_request(response):
    # Ensure responses aren't cached
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/homepage")
@login_required
def home():

    # Show Portfolio
    displayData = db.execute("SELECT cryptoName, cryptoSymbol, Coins, Price FROM CryptoData WHERE userID = :id", id=session["user_id"])

    for row in displayData:
        coinPrice = lookup(row["cryptoName"])
        print(row["cryptoName"])

        row["cryptoName"] = row["cryptoName"].title()
        row["cryptoSymbol"] = row["cryptoSymbol"].upper()
        row["coinPrice"] = usd(coinPrice["price"])
        row["Price"] = usd(row["Price"])

    return render_template("homepage.html", displayData=displayData)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Ensure Username was submitted
        if not request.form.get("username"):
            return apology("No username", 400)
        
        rows = db.execute("SELECT * FROM Users WHERE Username = :username", username=request.form.get("username"))

        # Ensure Username is available
        if len(rows) != 0:
            return apology("Username taken", 400)
        
        # Ensure password(s) were submitted
        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Password(s) not provided", 400)
        
        # Ensure password(s) match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Password(s) dont match", 400)
        
        # Hash password and insert into DB
        db.execute("INSERT INTO Users (Username, Hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=generate_password_hash(request.form.get("password")))

        # Redirect to landing page
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("No username", 403)
        
        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("No password", 403)
        
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username and password match
        if len(rows) != 1 or not check_password_hash(rows[0]["Hash"], request.form.get("password")):
            return apology("Invalid username and/or password", 403)
        
        # Remember which user has logged in
        session["user_id"] = rows[0]["ID"]

        # Redirect user to homePage
        return redirect("/homepage")
    
    # via GET
    else:
        return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    username = db.execute("SELECT Username, Cash FROM Users WHERE ID = :userId", userId=session["user_id"])
    cashBalance = usd(username[0]["Cash"])
    username = username[0]["Username"]

    return render_template("profile.html", username=username, cashBalance=cashBalance)


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():

    if request.method == "POST":

        cryptoCurrency = request.form.get("cryptoName")

        # Invalid Name
        if lookup(cryptoCurrency) is None:
            return apology("Invalid Cryptocurrency Name", 405)

        # Get quote using API
        quoteData = lookup(cryptoCurrency)

        # Predicted crypto price
        targetDate = request.form.get("target_date")

        predictedPrice = predict_crypto_price(cryptoCurrency, targetDate)

        # Display Quoted
        return render_template("quoted.html", name=quoteData["name"].title(), justSymbol=get_symbol_by_name(cryptoCurrency).upper(), price=usd(quoteData["price"]), predictedPrice=usd(predictedPrice), targetDate=targetDate)
    else:
        return render_template("quote.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        cryptoName = request.form.get("cryptoName")
        coins = request.form.get("coins")

        # Invalid symbol
        if lookup(cryptoName) == None:
            return apology("Invalid symbol", 406)
        
        # No coins | Not integer | Negative coins
        elif not coins or not coins.isdigit or float(coins) < 0:
            return apology("Must provide positive shares", 406)
        
        # Currency data
        currencyData = lookup(cryptoName)
        currencyPrice = currencyData["price"]

        # Cost
        totalPrice = float(coins) * currencyPrice

        # Check affordability
        balanceAmount = db.execute("SELECT Cash FROM Users WHERE ID = :id", id=session["user_id"])
        balanceAmount = balanceAmount[0]["Cash"]

        if totalPrice > balanceAmount:
            return apology("Can't afford", 406)
        
        # Update balance after Payment
        db.execute("UPDATE Users SET Cash = :cash WHERE ID = :id", cash=(balanceAmount - totalPrice), id=session["user_id"])

        # Update CryptoData Table
        rowsCheck = db.execute("SELECT * FROM CryptoData WHERE userID = :id AND cryptoName = :crypto", id=session["user_id"], crypto=cryptoName)

        # Update Holdings
        if len(rowsCheck) != 0:
            numberOfCoins = rowsCheck[0]["Coins"]
            boughtPrice = rowsCheck[0]["Price"]

            db.execute("UPDATE CryptoData SET Coins = :updatedCoins, Price = :updatedPrice WHERE cryptoName = :cryptoName AND userID = :id", updatedCoins=(numberOfCoins + int(coins)), updatedPrice=(float(boughtPrice + totalPrice)),cryptoName=cryptoName, id=session["user_id"])

            # Transaction history
            db.execute("INSERT INTO History (userID, cryptoSymbol, Coins, Price, Transacted) VALUES (:id, :cryptoSymbol, :coins, :price, CURRENT_TIMESTAMP)", id=session["user_id"], cryptoSymbol=get_symbol_by_name(cryptoName).upper(), coins=coins, price=totalPrice)
        
        else:
            # Add New record
            db.execute("INSERT INTO CryptoData (userID, cryptoName, cryptoSymbol, Coins, Price, Transacted) VALUES (:id, :crypto, :symbol, :coins, :price, CURRENT_TIMESTAMP)", id=session["user_id"], crypto=cryptoName, symbol=get_symbol_by_name(cryptoName), coins=coins, price=totalPrice)

            # Transaction history
            db.execute("INSERT INTO History (userID, cryptoSymbol, Coins, Price, Transacted) VALUES (:id, :cryptoSymbol, :coins, :price, CURRENT_TIMESTAMP)", id=session["user_id"], cryptoSymbol=get_symbol_by_name(cryptoName).upper(), coins=coins, price=totalPrice)

        flash(f"Brought {coins} coins of {cryptoName} for {usd(totalPrice)}!")
        return redirect("/homepage")
    
    else:
        return render_template("buy.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    ownedCrypto = db.execute("SELECT cryptoSymbol, Coins FROM CryptoData WHERE userID = :userID", userID=session["user_id"])

    if request.method == "POST":
        # Get Symbol & Coin
        cryptoSymbol = request.form.get("symbol")
        coinsToSell = request.form.get("coins")
        cryptoName = db.execute("SELECT cryptoName FROM CryptoData WHERE cryptoSymbol = :cryptoSymbol", cryptoSymbol=cryptoSymbol)[0]["cryptoName"]
        currentCryptoPrice = lookup(cryptoName)
        currentCryptoPrice = currentCryptoPrice["price"]

        for crypto in ownedCrypto:
            if crypto["cryptoSymbol"] == cryptoSymbol:

                # Check if User has that many coins willing to sell
                if float(coinsToSell) > crypto["Coins"]:
                    return apology("You dont have that many coins", 407)
                
                else:
                    # Sell Crypto
                    db.execute("UPDATE CryptoData SET Coins = Coins - :coinsToSell, Price = Price - :soldPrice WHERE cryptoSymbol = :cryptoSymbol AND userID = :userID", coinsToSell=coinsToSell, soldPrice=(currentCryptoPrice * float(coinsToSell)), cryptoSymbol=cryptoSymbol, userID=session["user_id"])

                    # Add sold price to balance
                    db.execute("UPDATE Users SET Cash = Cash + :soldPrice WHERE ID = :userID", soldPrice=(currentCryptoPrice * float(coinsToSell)), userID=session["user_id"])
                    
                    # Update Transaction
                    db.execute("INSERT INTO History (userID, cryptoSymbol, Coins, Price, Transacted) VALUES (:userID, :cryptoSymbol, :Coins, :Price, CURRENT_TIMESTAMP)", userID=session["user_id"], cryptoSymbol=cryptoSymbol.upper(), Coins="-" + coinsToSell, Price=(currentCryptoPrice * float(coinsToSell)))

                    # If crypto holding = 0, remove it
                    remainingCrypto = db.execute("SELECT Coins FROM CryptoData WHERE cryptoSymbol = :cryptoSymbol AND userID = :userID", cryptoSymbol=cryptoSymbol, userID=session["user_id"])
                    
                    if remainingCrypto[0]["Coins"] == 0:
                        db.execute("DELETE FROM CryptoData WHERE cryptoSymbol = :cryptoSymbol AND userID = :userID", cryptoSymbol=cryptoSymbol, userID=session["user_id"])

        flash(f"Sold {coinsToSell} coins of {cryptoSymbol} for {usd(currentCryptoPrice * float(coinsToSell))}")
        return redirect("homepage")
    else:
        return render_template("sell.html", ownedCrypto=ownedCrypto)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    transactionHistory = db.execute("SELECT cryptoSymbol, Coins, Price, Transacted FROM History WHERE userID = :userID ORDER BY Transacted DESC", userID=session["user_id"])
    return render_template("history.html", transactionHistory=transactionHistory)


@app.route("/logout")
def logout():

    # Forget ID
    session.clear()

    return redirect("/")
