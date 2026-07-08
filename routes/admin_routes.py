from flask import render_template, redirect, request, url_for, flash, session
from models import db, Trek, User, Booking
from werkzeug.utils import secure_filename
import os
from datetime import datetime

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
    

    @app.route("/admin/treks/add_trek", methods=["GET", "POST"])
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

            if status not in ["Open", "Closed", "Completed"]:
                flash("Invalid status!", "danger")
                return redirect(url_for("add_trek"))
            
            existing_trek = Trek.query.filter_by(trek_name=trek_name).first()
            if existing_trek:
                flash("A trek with this name already exists.", "danger")
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
                            image=image_name)
            
            db.session.add(new_trek)
            db.session.commit()
            flash("Trek added successfully!", "success")
            return redirect(url_for("treks"))
        
        return render_template("admin/add_trek.html")
    

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
        
        if trek.image:
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], trek.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(trek)
        db.session.commit()
        flash("Trek deleted successfully!", "success")
        return redirect(url_for("treks"))