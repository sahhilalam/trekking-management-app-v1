from flask import render_template, redirect, request, url_for, flash, session
from models import db, Trek, User, Booking

def admin_routes(app):

    @app.route("/admin")
    def admin_dashboard():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        total_treks = Trek.query.count()
        total_users = User.query.filter_by(role="User").count()
        total_staffs = User.query.filter_by(role="Staff").count()
        total_bookings = Booking.query.count()
        
        return render_template("admin/dashboard.html",
                               total_treks=total_treks,
                               total_bookings=total_bookings,
                               total_users=total_users,
                               total_staffs=total_staffs)
    

    @app.route("/admin/treks")
    def treks():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        treks = Trek.query.all()
        return render_template("admin/treks.html", treks=treks)
    

    @app.route("/admin/treks/add_trek")
    def add_trek():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        return render_template("admin/add_trek.html")