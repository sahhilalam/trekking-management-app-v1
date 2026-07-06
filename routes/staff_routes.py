from flask import render_template, redirect, request, url_for, flash, session

def staff_routes(app):

    @app.route("/staff")
    def staff_dashboard():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "Staff":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        return render_template("staff/dashboard.html")