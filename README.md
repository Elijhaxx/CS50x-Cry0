# CryO - Cryptocurrency Portfolio Manager (CS50x 2023 Final Project)


### Video Demo: https://youtu.be/MgbWG7gyj8g?si=u44_Hy49UJC4ZU1y


## Description


This web application, developed as the final project for CS50, inspired by Week 9 Problem Set, Finance, lets users manage cryptocurrency portfolios. Built with Flask and SQLite, it offers functionalities for buying, selling and tracking holdings. Users can predict, view real-time quotes and access transaction histories.


## Pre-requisites:


- **Python:** You can download it from https://www.python.org/downloads/.
- **Dependencies:** Installation of required packages: Flask, cs50, flask_session and werkzeug.security.


## Run the application:


- **Navigate to the Project Directory** cd into the project directory
- **Open a terminal or command prompt**
- **Run the application:** Use "flask run" to start the Flask Server.


## Project Structure


- **app.py:** Handles routing and integrates with HTML templates.
- **assist.py:** Contains authentication, error handling, API requests and USD conversion functions.
- **model.py:** Manages predictive models for estimating cryptocurrency prices, uses Linear regression.
- **cryo.db:** SQLite database storing user information and transactions.


## Design Choices


- **Flask Framework:** Chosen for simplicity and flexibility.
- **SQLite Database:** Lightweight and suitable for this application's scale.


## Routes Explanation


1. **'/' (Landing Page)**
    - Renders landing page ('landing.html').
    - Users arrive here when accessing the root URL of the application.


2. **'/homepage'**
    - Requires login ('@login_required' decorator).
    - Displays the user's homepage ('homepage.html') after successful login.
    - Retrieves and displays the user's portfolio (crypto holdings and prices).


3. **'/register'**
    - Handles both GET and POST requests.
    - Renders the registration page ('register.html') for users to sign up.
    - Validates user input and stores new user data in the database upon successful registration.


4. **'/login'**
    - Handles both GET and POST requests.
    - Validates user credentials and allows access to the homepage upon successful login.
    - Uses session handling to maintain user login state.


5. **'/profile'**
    - Requires login ('@login_required' decorator).
    - Displays the user's profile information ('profile.html'), as of now it just includes username and cash balance.


6. **'/quote'**
    - Requires login ('@login_required' decorator).
    - Allows users to get a quote for a particular cryptocurrency.
    - Renders the 'quote.html' page and processes the requests for a cryptocurrency quote.


7. **'/buy'**
    - Requires login ('@login_required' decorator).
    - Facilitates the purchase of cryptocurrencies by users.
    - Handles both GET and POST requests for buying cryptocurrencies.


8. **'/sell'**
    - Requires login ('@login_required' decorator).
    - Enables users to sell their owned cryptocurrencies.
    - Handles both GET and POST requests for selling cryptocurrencies.


9. **'/history'**
    - Requires login ('@login_required decorator).
    - Displays the transaction history ('history.html') for the logged-in user.


10. **'/logout'**
    - Logs out the user by clearing the session.
    - Redirects the user to the landing page after successful logout.


### Additional Notes:
- **Login Required**: Some routes are decorated with '@login_required', ensuring that only authenticated users can access certain pages or functionalities.
- **Form Handling**: Many routes handle both GET and POST requests, managing form submissions, user inputs and database interactions.
- **Error Handling**: The routes might use 'apology()' function to handle various error scenarios like input or insufficient funds.


Each route encapsulates specific functionalities of the cryptocurrency trading platform, facilitating different actions for users.


## Database & Table


- **Users:** User related information like, Username, hashed-password and their balance.
- **CryptoData:** Cryptocurrency to user related information.
- **History:** All the transaction details (buy/sell).


## Future Plans


- **History Graph:** Addition of all cryptocurrency with their information listed.
- **Real-time Updates:** Implementation of live price updates.
- **Advanced Analytics:** Addition of tools for trend analysis.
- **Improved UI:** Enhancing user interface for better useability.


## Tools/Resources Used


- **Visual Studio Code for CS50:** Used for development and testing.
- **CS50.ai:** CS50's duck debugger, an experimental AI for rubber ducking, the BEST!. Link - https://cs50.ai.
- **C$50 Finance:** The structure of this project was inspired by Week 9 problem set Finance. Link - https://cs50.harvard.edu/x/2023/psets/9/finance/.
- **CoinGecko API:** Used for API requests on cryptocurrency. Link - https://www.coingecko.com/en/api.


## Credits


- Portions of code and inspiration drawn from CS50x Week 9 problem set and lectures.


## Acknowledgements


- Thanks to CS50x for providing a comprehensive learning experience in this course. This is the best learning journey I have had.


**Time-lapse for the project**: Started the project on November 1 2023 to November 21 2023.

