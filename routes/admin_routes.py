from flask import render_template, redirect, request, url_for, flash, session

def admin_routes(app):

    @app.route("/admin")
    def admin_dashboard():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        return render_template("admin/dashboard.html")