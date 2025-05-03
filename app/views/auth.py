from flask import flash, render_template, Blueprint, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
from app.models.user import User
from app import db
from flask_wtf.csrf import generate_csrf

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    # redirect user if logged in
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        # Login logic here
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role")

        user = User.query.filter_by(username=username, role=role).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main.home"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html", csrf_token=generate_csrf())


@auth.route("/register", methods=["GET", "POST"])
def register():
    # Registration logic here
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        role = request.form.get("role")
        niche = request.form.get("niche")

        # Check if trying to register as admin
        if role == "admin":
            # Check if admin already exists
            admin_exists = User.query.filter_by(role="admin").first()
            if admin_exists:
                flash("Admin account already exists. Only one admin account is allowed.", "danger")
                return redirect(url_for("auth.register"))

        user_by_username = User.query.filter_by(username=username).first()

        if password != confirm_password:
            flash("Passwords do not match", "warning")
            return redirect(url_for("auth.register"))

        if user_by_username:
            flash("Username already exists", "warning")
            return redirect(url_for("auth.register"))

        user_by_email = User.query.filter_by(email=email).first()
        if user_by_email:
            flash("Email address already exists", "warning")
            return redirect(url_for("auth.register"))

        if role == "influencer":
            new_user = User(username=username, email=email, role=role, niche=niche)
        else:
            new_user = User(username=username, email=email, role=role)

        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    # Check if admin exists to disable admin option in the template
    admin_exists = User.query.filter_by(role="admin").first()
    return render_template("signup.html", csrf_token=generate_csrf(), admin_exists=admin_exists)


@auth.route("/logout")
def logout_the_user():
    logout_user()
    return redirect(url_for("main.home"))
