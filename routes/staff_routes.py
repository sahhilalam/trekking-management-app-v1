from flask import render_template, redirect, request, url_for, flash, session
from models import db, User, Trek, Booking

def staff_routes(app):

    @app.route("/staff")
    def staff_dashboard():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "Staff":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        assigned_treks = Trek.query.filter_by(staff_id=session["user_id"]).count()
        open_treks = Trek.query.filter_by(staff_id=session["user_id"], status="Open").count()
        completed_treks = Trek.query.filter_by(staff_id=session["user_id"], status="Completed").count()
        total_participants = Booking.query.join(Trek).filter(Trek.staff_id == session["user_id"]).count()
        
        return render_template("staff/dashboard.html",
                               assigned_treks=assigned_treks,
                               open_treks=open_treks,
                               completed_treks=completed_treks,
                               total_participants=total_participants)
    

    @app.route("/staff/treks")
    def staff_treks():
        pass