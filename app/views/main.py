from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

main = Blueprint("main", __name__)


@main.route("/")
def home():
    if current_user.is_authenticated and current_user.role == "admin":
        return redirect(
            url_for("admin.dashboard")
        )  # Redirect to admin dashboard if user is admin
    return render_template("index.html", user=current_user)
