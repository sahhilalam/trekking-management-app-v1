from flask import render_template, redirect, request, url_for, flash, session

def user_routes(app):

    @app.route("/user")
    def user_dashboard():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "User":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        return render_template("user/dashboard.html")