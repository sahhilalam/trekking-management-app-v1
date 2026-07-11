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

        bookings = Booking.query.filter_by(trek_id=trek_id).order_by(Booking.booking_date.desc()).all()
        bookings_count = Booking.query.filter(Booking.trek_id == trek_id, 
                                              Booking.booking_status != "Cancelled").count()

        return render_template("staff/participants.html",
                                trek=trek,
                                bookings=bookings,
                                bookings_count=bookings_count)
    

    @app.route("/staff/booking/cancel/<int:booking_id>")
    def cancel_booking(booking_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "Staff":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))

        booking = Booking.query.filter_by(booking_id=booking_id).first()

        if not booking:
            flash("No booking found!", "danger")
            return redirect(url_for("staff_treks"))

        trek = booking.trek

        if trek.staff_id != session["user_id"]:
            flash("You cannot manage this booking.", "danger")
            return redirect(url_for("staff_treks"))
        
        if trek.status in ["Closed", "Completed"]:
            flash("Bookings cannot be cancelled after the trek has started.", "warning")
            return redirect(url_for("trek_participants", trek_id=trek.trek_id))

        if booking.booking_status != "Booked":
            flash("Only active bookings can be cancelled.", "warning")
            return redirect(url_for("trek_participants", trek_id=trek.trek_id))

        booking.booking_status = "Cancelled"
        trek.available_slots += 1

        db.session.commit()

        flash("Booking cancelled successfully.", "success")
        return redirect(url_for("trek_participants", trek_id=trek.trek_id))
    

    @app.route("/staff/profile", methods=["GET", "POST"])
    def staff_profile():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "Staff":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))

        staff = User.query.filter_by(user_id=session["user_id"]).first()

        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            phone = request.form["phone"]
            current_password = request.form["current_password"]
            new_password = request.form["new_password"]
            confirm_password = request.form["confirm_password"]

            existing_user = User.query.filter_by(email=email).first()

            if existing_user and existing_user.user_id != staff.user_id:
                flash("Email already exists!", "danger")
                return redirect(url_for("staff_profile"))
            
            if current_password or new_password or confirm_password:
                if current_password != staff.password:
                    flash("Current password is incorrect.", "danger")
                    return redirect(url_for("staff_profile"))

                if new_password != confirm_password:
                    flash("New passwords do not match.", "danger")
                    return redirect(url_for("staff_profile"))

                if new_password == "":
                    flash("New password cannot be empty.", "danger")
                    return redirect(url_for("staff_profile"))
                    staff.password = new_password
        
            staff.name = name
            staff.email = email
            staff.phone = phone

            db.session.commit()

            session["name"] = staff.name

            flash("Profile updated successfully!", "success")
            return redirect(url_for("staff_profile"))

        return render_template("staff/profile.html", staff=staff)