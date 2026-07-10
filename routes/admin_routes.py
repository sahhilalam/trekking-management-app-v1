from flask import render_template, redirect, request, url_for, flash, session
from models import db, Trek, User, Booking
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from sqlalchemy import or_

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
        
        status = request.args.get("status")
        search = request.args.get("search")

        query = Trek.query

        if status in ["Pending", "Approved", "Open", "Closed", "Completed"]:
            query=query.filter_by(status=status)

        if search:
            query = query.filter(or_(
                Trek.trek_name.ilike(f"%{search}%"),
                Trek.location.ilike(f"%{search}%"),
                Trek.difficulty.ilike(f"%{search}%")
            ))
        

        treks = query.all()
        all_treks = Trek.query.count()
        pending_treks = Trek.query.filter_by(status="Pending").count()
        approved_treks = Trek.query.filter_by(status="Approved").count()
        open_treks = Trek.query.filter_by(status="Open").count()
        closed_treks = Trek.query.filter_by(status="Closed").count()
        completed_treks = Trek.query.filter_by(status="Completed").count()


        return render_template("admin/treks.html", 
                               treks=treks,
                               all_treks=all_treks,
                               pending_treks=pending_treks,
                               approved_treks=approved_treks,
                               open_treks=open_treks,
                               closed_treks=closed_treks,
                               completed_treks=completed_treks)
    

    @app.route("/admin/treks/add", methods=["GET", "POST"])
    def add_trek():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))

        if request.method == "POST":
            trek_name = request.form["trek_name"]
            location = request.form["location"]
            staff_id = request.form["staff_id"]
            difficulty = request.form["difficulty"]
            duration = int(request.form["duration"])
            available_slots = int(request.form["available_slots"])
            start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
            description = request.form["description"]
            status = request.form["status"]
            image = request.files["image"]

            if duration <= 0:
                flash("Duration must be greater than 0.", "danger")
                return redirect(url_for("add_trek"))
            
            if available_slots <=0:
                flash("Available slots must be greater than 0.", "danger")
                return redirect(url_for("add_trek"))
            
            if end_date < start_date:
                flash("End date cannot be before the start date.", "danger")
                return redirect(url_for("add_trek"))
            
            if difficulty not in ["Easy", "Moderate", "Hard"]:
                flash("Invalid difficulty!", "danger")
                return redirect(url_for("add_trek"))

            if status not in ["Pending", "Approved", "Open", "Closed", "Completed"]:
                flash("Invalid status!", "danger")
                return redirect(url_for("add_trek"))
            
            existing_trek = Trek.query.filter_by(trek_name=trek_name).first()
            if existing_trek:
                flash("A trek with this name already exists.", "danger")
                return redirect(url_for("add_trek"))
            
            if staff_id == "":
                manager = None
            else:
                manager = User.query.filter_by(user_id=staff_id).first()
                if not manager:
                    flash("No such staff exist!", "danger")
                    return redirect(url_for("add_trek"))
                if manager.role != "Staff":
                    flash("Assigned person must be a staff.", "danger")
                    return redirect(url_for("add_trek"))
                if manager.account_status != "Approved":
                    flash("Staff must be approved by admin.", "danger")
                    return redirect(url_for("add_trek"))

            image_name = None
            if image and image.filename:
                image_name = secure_filename(image.filename)
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))

            new_trek = Trek(trek_name=trek_name,
                            location=location,
                            difficulty=difficulty,
                            duration=duration,
                            available_slots=available_slots,
                            start_date=start_date,
                            end_date=end_date,
                            status=status,
                            description=description,
                            image=image_name,
                            manager=manager)
            
            db.session.add(new_trek)
            db.session.commit()
            flash("Trek added successfully!", "success")
            return redirect(url_for("treks"))
        
        approved_staff = User.query.filter_by(role="Staff", account_status="Approved").all()

        return render_template("admin/add_trek.html", approved_staff=approved_staff)
    

    @app.route("/admin/treks/delete/<int:trek_id>")
    def delete_trek(trek_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        trek = Trek.query.filter_by(trek_id=trek_id).first()

        if not trek:
            flash("No trek found!", "danger")
            return redirect(url_for("treks"))
        
        if trek.bookings:
            flash("Cannot delete a trek with existing bookings.", "danger")
            return redirect(url_for("treks"))
        
        if trek.image:
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], trek.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(trek)
        db.session.commit()
        flash("Trek deleted successfully!", "success")
        return redirect(url_for("treks"))
    

    @app.route("/admin/treks/edit/<int:trek_id>", methods=["GET", "POST"])
    def edit_trek(trek_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        trek = Trek.query.filter_by(trek_id=trek_id).first()
        approved_staff = User.query.filter_by(role="Staff", account_status="Approved").all()

        if not trek:
            flash("No trek found!", "danger")
            return redirect(url_for("treks"))
        
        if request.method == "POST":
            trek_name = request.form["trek_name"]
            location = request.form["location"]
            staff_id = request.form["staff_id"]
            difficulty = request.form["difficulty"]
            duration = int(request.form["duration"])
            available_slots = int(request.form["available_slots"])
            start_date = datetime.strptime(request.form["start_date"], "%Y-%m-%d").date()
            end_date = datetime.strptime(request.form["end_date"], "%Y-%m-%d").date()
            description = request.form["description"]
            status = request.form["status"]
            image = request.files["image"]

            if duration <= 0:
                flash("Duration must be greater than 0.", "danger")
                return redirect(url_for("edit_trek", trek_id=trek_id))
            
            if available_slots <=0:
                flash("Available slots must be greater than 0.", "danger")
                return redirect(url_for("edit_trek", trek_id=trek_id))
            
            if end_date < start_date:
                flash("End date cannot be before the start date.", "danger")
                return redirect(url_for("edit_trek", trek_id=trek_id))
            
            if difficulty not in ["Easy", "Moderate", "Hard"]:
                flash("Invalid difficulty!", "danger")
                return redirect(url_for("edit_trek", trek_id=trek_id))

            if status not in ["Pending", "Approved", "Open", "Closed", "Completed"]:
                flash("Invalid status!", "danger")
                return redirect(url_for("edit_trek", trek_id=trek_id))
            
            existing_trek = Trek.query.filter_by(trek_name=trek_name).first()
            if existing_trek and existing_trek.trek_id != trek.trek_id:
                flash("A trek with this name already exists.", "danger")
                return redirect(url_for("edit_trek", trek_id=trek_id))
            
            if staff_id == "":
                manager = None
            else:
                manager = User.query.filter_by(user_id=int(staff_id)).first()
                if not manager:
                    flash("No such staff exist!", "danger")
                    return redirect(url_for("edit_trek", trek_id=trek_id))
                if manager.role != "Staff":
                    flash("Assigned person must be a staff.", "danger")
                    return redirect(url_for("edit_trek", trek_id=trek_id))
                if manager.account_status != "Approved":
                    flash("Staff must be approved by admin.", "danger")
                    return redirect(url_for("edit_trek", trek_id=trek_id))
                
            if image and image.filename:
                if trek.image:
                    old_image = os.path.join(app.config["UPLOAD_FOLDER"], trek.image)
                    if os.path.exists(old_image):
                        os.remove(old_image)
                image_name = secure_filename(image.filename)
                image.save(os.path.join(app.config["UPLOAD_FOLDER"], image_name))
                trek.image = image_name

            if trek.status != "Completed" and status == "Completed":
                bookings = Booking.query.filter_by(trek_id=trek_id, booking_status="Booked").all()
                for booking in bookings:
                    booking.booking_status = "Completed"
                
            trek.trek_name = trek_name
            trek.location = location
            trek.difficulty = difficulty
            trek.duration = duration
            trek.available_slots = available_slots
            trek.start_date = start_date
            trek.end_date = end_date
            trek.status = status
            trek.description = description
            trek.manager = manager

            db.session.commit()
            flash("Trek updated successfully!", "success")
            return redirect(url_for("treks"))
        
        return render_template("admin/edit_trek.html", trek=trek, approved_staff=approved_staff)
    

    @app.route("/admin/staff")
    def staff():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        status = request.args.get("status")
        search = request.args.get("search")

        query = User.query.filter_by(role="Staff")

        if status in ["Approved", "Pending", "Blacklisted"]:
            query = query.filter_by(account_status=status)
        
        if search:
            query = query.filter(or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            ))
        
        staff = query.all()

        total = User.query.filter_by(role="Staff").count()
        approved = User.query.filter_by(role="Staff", account_status="Approved").count()
        pending = User.query.filter_by(role="Staff", account_status="Pending").count()
        blacklisted = User.query.filter_by(role="Staff", account_status="Blacklisted").count()

        return render_template("admin/staff.html",
                               staff=staff,
                               total=total,
                               approved=approved,
                               pending=pending,
                               blacklisted=blacklisted)
    

    @app.route("/admin/staff/approve/<int:user_id>")
    def approve_staff(user_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        staff = User.query.filter_by(user_id=user_id).first()
        if not staff:
            flash("No staff found!", "danger")
            return redirect(url_for("staff"))
        
        if staff.role != "Staff":
            flash("Invalid staff!", "danger")
            return redirect(url_for("staff"))
        
        if staff.account_status == "Approved":
            flash("Staff is already approved!", "warning")
            return redirect(url_for("staff"))
        
        staff.account_status = "Approved"
        db.session.commit()
        flash("Staff approved successfully!", "success")
        return redirect(url_for("staff"))
    

    @app.route("/admin/staff/blacklist/<int:user_id>")
    def blacklist_staff(user_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        staff = User.query.filter_by(user_id=user_id).first()
        if not staff:
            flash("No staff found!", "danger")
            return redirect(url_for("staff"))
        
        if staff.role != "Staff":
            flash("Invalid staff!", "danger")
            return redirect(url_for("staff"))
        
        if staff.account_status == "Blacklisted":
            flash("Staff is already blacklisted!", "warning")
            return redirect(url_for("staff"))
        
        active_treks = Trek.query.filter(Trek.staff_id == user_id, 
                                         Trek.status.in_(["Open", "Closed", "Pending", "Approved"])).all()
        for trek in active_treks:
            trek.manager = None
        
        staff.account_status = "Blacklisted"
        db.session.commit()
        flash("Staff blacklisted successfully. Active treks have been unassigned.", "success")
        return redirect(url_for("staff"))
    


    @app.route("/admin/users")
    def users():
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        status = request.args.get("status")
        search = request.args.get("search")

        query = User.query.filter_by(role="User")

        if status in ["Approved", "Blacklisted"]:
            query = query.filter_by(account_status=status)
        
        if search:
            query = query.filter(or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            ))
        
        user = query.all()

        total = User.query.filter_by(role="User").count()
        approved = User.query.filter_by(role="User", account_status="Approved").count()
        blacklisted = User.query.filter_by(role="User", account_status="Blacklisted").count()

        return render_template("admin/users.html",
                               user=user,
                               total=total,
                               approved=approved,
                               blacklisted=blacklisted)
    

    @app.route("/admin/users/approve/<int:user_id>")
    def approve_user(user_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            flash("No user found!", "danger")
            return redirect(url_for("users"))
        
        if user.role != "User":
            flash("Invalid user!", "danger")
            return redirect(url_for("users"))
        
        if user.account_status == "Approved":
            flash("User is already approved!", "warning")
            return redirect(url_for("users"))
        
        user.account_status = "Approved"
        db.session.commit()
        flash("User approved successfully!", "success")
        return redirect(url_for("users"))
    

    @app.route("/admin/users/blacklist/<int:user_id>")
    def blacklist_user(user_id):
        if "user_id" not in session:
            flash("Please login first!", "danger")
            return redirect(url_for("login"))
        
        if session.get("role") != "Admin":
            flash("Access denied!", "danger")
            return redirect(url_for("login"))
        
        user = User.query.filter_by(user_id=user_id).first()
        if not user:
            flash("No user found!", "danger")
            return redirect(url_for("users"))
        
        if user.role != "User":
            flash("Invalid user!", "danger")
            return redirect(url_for("users"))
        
        if user.account_status == "Blacklisted":
            flash("User is already blacklisted!", "warning")
            return redirect(url_for("users"))
        
        user.account_status = "Blacklisted"
        db.session.commit()
        flash("User blacklisted successfully!", "success")
        return redirect(url_for("users"))