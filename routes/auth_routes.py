from flask import render_template, redirect, request, url_for, flash, session
from models import db, User

def auth_routes(app):

    @app.route("/", methods=["GET", "POST"])
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                flash("Email does not exist, please register!", "danger")
                return redirect(url_for("register"))
            
            if existing_user.password == password:
                if existing_user.account_status == "Pending":
                    flash("Your staff account is pending admin approval.", "warning")
                    return redirect(url_for("login"))
                elif existing_user.account_status == "Blacklisted":
                    flash("Your account has been blacklisted. Contact the administrator", "danger")
                    return redirect(url_for("login"))
                elif existing_user.account_status == "Approved":
                    session["user_id"] = existing_user.user_id
                    session["name"] = existing_user.name
                    session["role"] = existing_user.role
                    flash("Login successful!", "success")
                    if existing_user.role == "Admin":
                        return redirect(url_for("admin_dashboard"))
                    elif existing_user.role == "Staff":
                        return redirect(url_for("staff_dashboard"))
                    elif existing_user.role == "User":
                        return redirect(url_for("user_dashboard"))
            else:
                flash("Wrong password!", "danger")
                return redirect(url_for("login"))        

        return render_template("auth/login.html")
    
    
    
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            name = request.form["name"]
            email = request.form["email"]
            password = request.form["password"]
            confirm_password = request.form["confirm_password"]
            phone = request.form["phone"]
            role = request.form["role"]

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("Email already exists!", "danger")
                return redirect(url_for("register"))
            
            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return redirect(url_for("register"))
            
            if role == "User":
                account_status = "Approved"
                flash("Registration successful! Please login.", "success")
            elif role == "Staff":
                flash("Registration successful! Please wait for admin approval.", "success")
                account_status = "Pending"
            else:
                flash("Invalid role!", "danger")
                return redirect(url_for("register"))
            
            new_user = User(
                name=name,
                email=email,
                password=password,
                phone=phone,
                role=role,
                account_status=account_status
            )

            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for("login"))
        
        return render_template("auth/register.html")
    
    
    
    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out successfully!", "success")
        return redirect(url_for("login"))