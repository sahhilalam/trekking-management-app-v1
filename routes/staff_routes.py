from flask import render_template, redirect, request, url_for, flash, session
from models import db, User, Trek, Booking
from sqlalchemy import or_

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
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "Staff":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        query = Trek.query.filter_by(staff_id=session["user_id"])
        search = request.args.get("search")
        status = request.args.get("status")
        
        if status in ["Pending", "Approved", "Open", "Closed", "Completed"]:
            query = query.filter_by(status=status)

        if search:
            query = query.filter(or_(
                Trek.trek_name.ilike(f"%{search}%"),
                Trek.location.ilike(f"%{search}%"),
                Trek.difficulty.ilike(f"%{search}%")
            ))

        treks = query.all()

        assigned_treks = Trek.query.filter_by(staff_id=session["user_id"]).count()
        pending_treks = Trek.query.filter_by(staff_id=session["user_id"], status="Pending").count()
        approved_treks = Trek.query.filter_by(staff_id=session["user_id"], status="Approved").count()
        open_treks = Trek.query.filter_by(staff_id=session["user_id"], status="Open").count()
        completed_treks = Trek.query.filter_by(staff_id=session["user_id"], status="Completed").count()
        closed_treks = Trek.query.filter_by(staff_id=session["user_id"], status="Closed").count()
        
        return render_template("staff/treks.html", 
                               treks=treks,
                               assigned_treks=assigned_treks,
                               pending_treks=pending_treks,
                               approved_treks=approved_treks,
                               open_treks=open_treks,
                               closed_treks=closed_treks,
                               completed_treks=completed_treks)
    

    @app.route("/staff/treks/manage/<int:trek_id>", methods=["GET", "POST"])
    def manage_trek(trek_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "Staff":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        trek = Trek.query.filter_by(trek_id=trek_id).first()

        if not trek:
            flash("No trek found!", "danger")
            return redirect(url_for("staff_treks"))

        if trek.staff_id != session["user_id"]:
            flash("Invalid trek!", "danger")
            return redirect(url_for("staff_treks"))
        
        if trek.status == "Pending":
            flash("This trek cannot be managed until it is approved by the admin.", "warning")
            return redirect(url_for("staff_treks"))
        
        if trek.status == "Completed":
            flash("Completed treks cannot be modified.", "warning")
            return redirect(url_for("staff_treks"))
        
        if request.method == "POST":
            available_slots = int(request.form["available_slots"])

            if available_slots < 0:
                flash("Available slots cannot be negative.", "danger")
                return redirect(url_for("manage_trek", trek_id=trek_id))
            
            if "change_status" in request.form:
                if trek.status == "Approved":
                    trek.status = "Open"
                elif trek.status == "Open":
                    trek.status = "Closed"
                elif trek.status == "Closed":
                    trek.status = "Completed"
                    bookings = Booking.query.filter_by(trek_id=trek_id, booking_status="Booked").all()
                    for booking in bookings:
                        booking.booking_status = "Completed"
                else:
                    flash("Invalid status transition.", "danger")
                    return redirect(url_for("manage_trek", trek_id=trek_id))
                
            if trek.status in ["Approved", "Open"]:
                trek.available_slots = available_slots

            db.session.commit()
            flash("Trek updated successfully!", "success")
            return redirect(url_for("staff_treks"))

        return render_template("staff/manage_trek.html", trek=trek)


    @app.route("/staff/treks/participants/<int:trek_id>")
    def trek_participants(trek_id):
        pass 