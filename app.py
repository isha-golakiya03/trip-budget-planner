from flask import Flask, render_template, request, redirect, url_for, session
import plotly.express as px

app = Flask(__name__)

app.secret_key = "tripbudget_secret_key_2026"


# =========================================================
# HOME
# =========================================================

@app.route("/")
def index():
    return render_template("index.html")


# =========================================================
# DESTINATION
# =========================================================

@app.route("/destination", methods=["GET", "POST"])
def destination():

    if request.method == "POST":

        destination_name = request.form.get(
            "destination",
            ""
        ).strip()

        if destination_name == "":
            destination_name = "Goa"

        session["destination"] = destination_name

        return redirect(url_for("agent"))

    return render_template(
        "destination.html",
        destination=session.get(
            "destination",
            ""
        )
    )


# =========================================================
# TRAVEL AGENT
# =========================================================

@app.route("/agent", methods=["GET", "POST"])
def agent():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        travelers = request.form.get(
            "travelers",
            "1"
        )

        travel_style = request.form.get(
            "travel_style",
            "Budget"
        )

        transport = request.form.get(
            "transport",
            "Train"
        )

        accommodation = request.form.get(
            "accommodation",
            "Hotel"
        )

        # Convert travelers into integer
        try:
            travelers = int(travelers)
        except ValueError:
            travelers = 1

        if travelers < 1:
            travelers = 1

        # Store data in session
        session["name"] = (
            name if name else "Traveler"
        )

        session["travelers"] = travelers

        session["travel_style"] = travel_style

        session["transport"] = transport

        session["accommodation"] = accommodation

        return redirect(url_for("planner"))

    return render_template(
        "agent.html",
        destination=session.get(
            "destination",
            "Goa"
        )
    )


# =========================================================
# PLANNER
# =========================================================

@app.route("/planner", methods=["GET", "POST"])
def planner():

    if request.method == "POST":

        start_date = request.form.get(
            "start_date",
            ""
        )

        days = request.form.get(
            "days",
            "3"
        )

        food_budget = request.form.get(
            "food_budget",
            "1000"
        )

        activity_budget = request.form.get(
            "activity_budget",
            "1000"
        )

        hotel_budget = request.form.get(
            "hotel_budget",
            "2000"
        )

        # =================================================
        # INPUT VALIDATION
        # =================================================

        try:
            days = int(days)
        except ValueError:
            days = 3

        try:
            food_budget = float(food_budget)
        except ValueError:
            food_budget = 1000

        try:
            activity_budget = float(activity_budget)
        except ValueError:
            activity_budget = 1000

        try:
            hotel_budget = float(hotel_budget)
        except ValueError:
            hotel_budget = 2000

        # Minimum values

        if days < 1:
            days = 1

        if food_budget < 0:
            food_budget = 0

        if activity_budget < 0:
            activity_budget = 0

        if hotel_budget < 0:
            hotel_budget = 0

        # =================================================
        # STORE PLANNER DATA
        # =================================================

        session["start_date"] = start_date

        session["days"] = days

        session["food_budget"] = food_budget

        session["activity_budget"] = activity_budget

        session["hotel_budget"] = hotel_budget

        # =================================================
        # TRANSPORT PRICE
        # =================================================

        transport = session.get(
            "transport",
            "Train"
        )

        transport_prices = {

            "Bus": 800,

            "Train": 1500,

            "Flight": 5000,

            "Car": 2500
        }

        transport_per_person = transport_prices.get(
            transport,
            1500
        )

        travelers = session.get(
            "travelers",
            1
        )

        # =================================================
        # BUDGET CALCULATIONS
        # =================================================

        transport_total = (
            transport_per_person *
            travelers
        )

        hotel_total = (
            hotel_budget *
            days
        )

        food_total = (
            food_budget *
            days *
            travelers
        )

        activity_total = (
            activity_budget *
            days *
            travelers
        )

        total_budget = (
            transport_total +
            hotel_total +
            food_total +
            activity_total
        )

        # =================================================
        # STORE CALCULATED DATA
        # =================================================

        session["transport_total"] = transport_total

        session["hotel_total"] = hotel_total

        session["food_total"] = food_total

        session["activity_total"] = activity_total

        session["total_budget"] = total_budget

        return redirect(
            url_for("analysis")
        )

    return render_template(
        "planner.html",

        destination=session.get(
            "destination",
            "Goa"
        ),

        travelers=session.get(
            "travelers",
            1
        ),

        travel_style=session.get(
            "travel_style",
            "Budget"
        ),

        accommodation=session.get(
            "accommodation",
            "Hotel"
        )
    )


# =========================================================
# ANALYSIS
# =========================================================

@app.route("/analysis")
def analysis():

    transport_total = session.get(
        "transport_total",
        0
    )

    hotel_total = session.get(
        "hotel_total",
        0
    )

    food_total = session.get(
        "food_total",
        0
    )

    activity_total = session.get(
        "activity_total",
        0
    )

    total_budget = session.get(
        "total_budget",
        0
    )

    # Prevent division by zero

    if total_budget <= 0:
        total_budget = 1

    # =================================================
    # PERCENTAGE CALCULATIONS
    # =================================================

    transport_percent = round(
        (transport_total / total_budget) * 100,
        1
    )

    hotel_percent = round(
        (hotel_total / total_budget) * 100,
        1
    )

    food_percent = round(
        (food_total / total_budget) * 100,
        1
    )

    activity_percent = round(
        (activity_total / total_budget) * 100,
        1
    )

    return render_template(
        "analysis.html",

        destination=session.get(
            "destination",
            "Goa"
        ),

        transport_total=transport_total,

        hotel_total=hotel_total,

        food_total=food_total,

        activity_total=activity_total,

        total_budget=session.get(
            "total_budget",
            0
        ),

        transport_percent=transport_percent,

        hotel_percent=hotel_percent,

        food_percent=food_percent,

        activity_percent=activity_percent
    )


# =========================================================
# DAY-WISE PLAN
# =========================================================

@app.route("/daywise")
def daywise():

    destination_name = session.get(
        "destination",
        "Goa"
    )

    days = session.get(
        "days",
        3
    )

    plans = []

    # =================================================
    # CREATE DAY-WISE PLAN
    # =================================================

    for day in range(1, days + 1):

        if day == 1:

            morning = (
                f"Arrival in {destination_name} "
                "and hotel check-in"
            )

            afternoon = (
                "Explore nearby local attractions "
                "and have lunch"
            )

            evening = (
                "Enjoy local food and "
                "evening sightseeing"
            )

        elif day == 2:

            morning = (
                "Visit major tourist attractions"
            )

            afternoon = (
                "Lunch and adventure or "
                "recreational activities"
            )

            evening = (
                "Shopping and explore "
                "local markets"
            )

        elif day == 3:

            morning = (
                "Visit a famous landmark "
                "or nature spot"
            )

            afternoon = (
                "Relax and enjoy "
                "local experiences"
            )

            evening = (
                "Dinner and leisure time"
            )

        else:

            morning = (
                f"Explore another popular "
                f"place in {destination_name}"
            )

            afternoon = (
                "Local sightseeing and lunch"
            )

            evening = (
                "Relax, shopping and dinner"
            )

        plans.append({

            "day": day,

            "morning": morning,

            "afternoon": afternoon,

            "evening": evening
        })

    return render_template(
        "daywise.html",

        destination=destination_name,

        plans=plans
    )


# =========================================================
# SUMMARY
# =========================================================

@app.route("/summary")
def summary():

    # =================================================
    # GET BUDGET DATA FROM SESSION
    # =================================================

    transport_total = session.get(
        "transport_total",
        0
    )

    hotel_total = session.get(
        "hotel_total",
        0
    )

    food_total = session.get(
        "food_total",
        0
    )

    activity_total = session.get(
        "activity_total",
        0
    )

    total_budget = session.get(
        "total_budget",
        0
    )

    # =================================================
    # PLOTLY CHART DATA
    # =================================================

    categories = [
        "Transportation",
        "Accommodation",
        "Food",
        "Activities"
    ]

    values = [
        transport_total,
        hotel_total,
        food_total,
        activity_total
    ]

    # =================================================
    # CREATE PLOTLY BAR CHART
    # =================================================

    chart = px.bar(
        x=categories,
        y=values,
        title="Trip Budget Overview",
        labels={
            "x": "Expense Category",
            "y": "Amount (₹)"
        }
    )

    # =================================================
    # CONVERT CHART TO HTML
    # =================================================

    summary_chart = chart.to_html(
        full_html=False,
        include_plotlyjs="cdn"
    )

    # =================================================
    # SEND DATA TO SUMMARY.HTML
    # =================================================

    return render_template(

        "summary.html",

        destination=session.get(
            "destination",
            "Goa"
        ),

        name=session.get(
            "name",
            "Traveler"
        ),

        travelers=session.get(
            "travelers",
            1
        ),

        travel_style=session.get(
            "travel_style",
            "Budget"
        ),

        transport=session.get(
            "transport",
            "Train"
        ),

        accommodation=session.get(
            "accommodation",
            "Hotel"
        ),

        start_date=session.get(
            "start_date",
            ""
        ),

        days=session.get(
            "days",
            3
        ),

        transport_total=transport_total,

        hotel_total=hotel_total,

        food_total=food_total,

        activity_total=activity_total,

        total_budget=total_budget,

        # IMPORTANT
        # Plotly chart sent to HTML
        summary_chart=summary_chart
    )


# =========================================================
# RESET
# =========================================================

@app.route("/reset")
def reset():

    session.clear()

    return redirect(
        url_for("index")
    )


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )