from flask import render_template, redirect, request, url_for, flash, session
from models import db, User, Trek, Booking
from sqlalchemy import or_
from datetime import date

def user_routes(app):

    @app.route("/user")
    def user_dashboard():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "User":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if user.account_status == "Blacklisted":
            session.clear()
            flash("Your account has been blacklisted. Contact the administrator", "danger")
            return redirect(url_for("login"))
        
        available_treks = Trek.query.filter_by(status="Open").count()
        active_bookings = Booking.query.filter_by(user_id=session["user_id"], booking_status="Booked").count()
        cancelled_bookings = Booking.query.filter_by(user_id=session["user_id"], booking_status="Cancelled").count()
        completed_treks = Booking.query.filter_by(user_id=session["user_id"], booking_status="Completed").count()
        
        upcoming_treks = Booking.query.join(Trek).filter(
            Booking.user_id == session["user_id"],
            Booking.booking_status == "Booked",
            Trek.start_date >= date.today()
        ).order_by(Trek.start_date).limit(5).all()

        recent_history = Booking.query.join(Trek).filter(
            Booking.user_id == session["user_id"],
            Booking.booking_status == "Completed"
        ).order_by(Trek.end_date.desc()).limit(5).all()


        return render_template("user/dashboard.html",
                               available_treks=available_treks,
                               active_bookings=active_bookings,
                               cancelled_bookings=cancelled_bookings,
                               completed_treks=completed_treks,
                               upcoming_treks=upcoming_treks,
                               recent_history=recent_history)
    

    @app.route("/user/treks")
    def user_treks():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
    
        if session["role"] != "User":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if user.account_status == "Blacklisted":
            session.clear()
            flash("Your account has been blacklisted. Contact the administrator", "danger")
            return redirect(url_for("login"))
    
        difficulty = request.args.get("difficulty")
        search = request.args.get("search")
    
        query = Trek.query.filter_by(status="Open")
    
        if difficulty in ["Easy", "Moderate", "Hard"]:
            query = query.filter_by(difficulty=difficulty)
    
        if search:
            search = search.strip()
            query = query.filter(or_(
                Trek.trek_name.ilike(f"%{search}%"),
                Trek.location.ilike(f"%{search}%")
            ))
    
        treks = query.all()
    
        all_treks = Trek.query.filter_by(status="Open").count()
        easy_treks = Trek.query.filter_by(status="Open", difficulty="Easy").count()
        moderate_treks = Trek.query.filter_by(status="Open", difficulty="Moderate").count()
        hard_treks = Trek.query.filter_by(status="Open", difficulty="Hard").count()
    
        return render_template("user/treks.html",
                                treks=treks,
                                all_treks=all_treks,
                                easy_treks=easy_treks,
                                moderate_treks=moderate_treks,
                                hard_treks=hard_treks)
    


    @app.route("/user/treks/<int:trek_id>")
    def trek_detail(trek_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "User":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if user.account_status == "Blacklisted":
            session.clear()
            flash("Your account has been blacklisted. Contact the administrator", "danger")
            return redirect(url_for("login"))

        trek = Trek.query.filter_by(trek_id=trek_id, status="Open").first()

        if not trek:
            flash("No Trek found!", "danger")
            return redirect(url_for("user_treks"))

        return render_template("user/trek_detail.html", trek=trek)
    


    @app.route("/user/treks/book/<int:trek_id>")
    def book_trek(trek_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "User":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if user.account_status == "Blacklisted":
            session.clear()
            flash("Your account has been blacklisted. Contact the administrator", "danger")
            return redirect(url_for("login"))
        
        trek = Trek.query.filter_by(trek_id=trek_id).first()
        
        if not trek:
            flash("No Trek found!", "danger")
            return redirect(url_for("user_treks"))
        
        if trek.status != "Open":
            flash("Bookings are closed for this trek.", "warning")
            return redirect(url_for("trek_detail", trek_id=trek_id))
        
        if trek.available_slots <= 0:
            flash("No slots available.", "warning")
            return redirect(url_for("trek_detail", trek_id=trek_id))
        
        existing_booking = Booking.query.filter_by(user_id=session["user_id"], 
                                                   trek_id=trek_id, 
                                                   booking_status="Booked").first()
        
        if existing_booking:
            flash("You have already booked this trek.", "warning")
            return redirect(url_for("trek_detail", trek_id=trek_id))
        
        new_booking = Booking(booking_date=date.today(), 
                              booking_status="Booked", 
                              user_id=session["user_id"], 
                              trek_id=trek_id)
        
        trek.available_slots -= 1

        db.session.add(new_booking)
        db.session.commit()

        flash("Trek booked successfully!", "success")
        return redirect(url_for("user_bookings"))
        



    @app.route("/user/bookings")
    def user_bookings():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "User":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if user.account_status == "Blacklisted":
            session.clear()
            flash("Your account has been blacklisted. Contact the administrator", "danger")
            return redirect(url_for("login"))
        
        status = request.args.get("status")
        search = request.args.get("search")

        query = Booking.query.filter_by(user_id=session["user_id"])

        if status in ["Booked", "Cancelled", "Completed"]:
            query = query.filter_by(booking_status=status)

        if search:
            search = search.strip()
            query = query.join(Trek).filter(or_(
                Trek.trek_name.ilike(f"%{search}%"),
                Trek.location.ilike(f"%{search}%")
            ))

        bookings = query.order_by(Booking.booking_date.desc()).all()

        all_bookings = Booking.query.filter_by(user_id=session["user_id"]).count()

        booked = Booking.query.filter_by(user_id=session["user_id"],
                                         booking_status="Booked").count()

        cancelled = Booking.query.filter_by(user_id=session["user_id"],
                                            booking_status="Cancelled").count()

        completed = Booking.query.filter_by(user_id=session["user_id"],
                                            booking_status="Completed").count()
        
        return render_template("user/bookings.html",
                                bookings=bookings,
                                all_bookings=all_bookings,
                                booked=booked,
                                cancelled=cancelled,
                                completed=completed)



    @app.route("/user/bookings/cancel/<int:booking_id>")
    def user_cancel_booking(booking_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "User":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))

        user = User.query.filter_by(user_id=session["user_id"]).first()
        if user.account_status == "Blacklisted":
            session.clear()
            flash("Your account has been blacklisted. Contact the administrator", "danger")
            return redirect(url_for("login"))

        booking = Booking.query.filter_by(booking_id=booking_id).first()

        if not booking:
            flash("No booking found!", "danger")
            return redirect(url_for("user_bookings"))

        if booking.user_id != session["user_id"]:
            flash("You cannot cancel this booking.", "danger")
            return redirect(url_for("user_bookings"))

        trek = booking.trek

        if trek.status != "Open":
            flash("This booking can no longer be cancelled.", "warning")
            return redirect(url_for("user_bookings"))

        if booking.booking_status != "Booked":
            flash("Only active bookings can be cancelled.", "warning")
            return redirect(url_for("user_bookings"))

        booking.booking_status = "Cancelled"
        trek.available_slots += 1

        db.session.commit()

        flash("Booking cancelled successfully!", "success")
        return redirect(url_for("user_bookings"))



    @app.route("/user/history")
    def trek_history():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "User":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))

        user = User.query.filter_by(user_id=session["user_id"]).first()
        if user.account_status == "Blacklisted":
            session.clear()
            flash("Your account has been blacklisted. Contact the administrator", "danger")
            return redirect(url_for("login"))
        
        search = request.args.get("search")

        query = Booking.query.filter_by(user_id=session["user_id"], booking_status="Completed")

        if search:
            search = search.strip()
            query = query.join(Trek).filter(or_(
                Trek.trek_name.ilike(f"%{search}%"),
                Trek.location.ilike(f"%{search}%"),
                Trek.difficulty.ilike(f"%{search}%")
            ))

        bookings = query.order_by(Booking.booking_date.desc()).all()

        completed = Booking.query.filter_by(user_id=session["user_id"], booking_status="Completed").count()

        return render_template("user/history.html",
                               bookings=bookings,
                               completed=completed)



    @app.route("/user/profile", methods=["GET", "POST"])
    def user_profile():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))

        if session["role"] != "User":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))

        user = User.query.filter_by(user_id=session["user_id"]).first()
        if user.account_status == "Blacklisted":
            session.clear()
            flash("Your account has been blacklisted. Contact the administrator", "danger")
            return redirect(url_for("login"))

        if request.method == "POST":
            name = request.form["name"].strip()
            email = request.form["email"].strip().lower()
            phone = request.form["phone"].strip()
            current_password = request.form["current_password"]
            new_password = request.form["new_password"]
            confirm_password = request.form["confirm_password"]

            existing_user = User.query.filter_by(email=email).first()

            if existing_user and existing_user.user_id != user.user_id:
                flash("Email already exists!", "danger")
                return redirect(url_for("user_profile"))
            
            if current_password or new_password or confirm_password:
                if current_password != user.password:
                    flash("Current password is incorrect.", "danger")
                    return redirect(url_for("user_profile"))

                if new_password != confirm_password:
                    flash("New passwords do not match.", "danger")
                    return redirect(url_for("user_profile"))

                if new_password == "":
                    flash("New password cannot be empty.", "danger")
                    return redirect(url_for("user_profile"))
                    
                user.password = new_password
        
            user.name = name
            user.email = email
            user.phone = phone

            db.session.commit()

            session["name"] = user.name

            flash("Profile updated successfully!", "success")
            return redirect(url_for("user_profile"))

        return render_template("user/profile.html", user=user)