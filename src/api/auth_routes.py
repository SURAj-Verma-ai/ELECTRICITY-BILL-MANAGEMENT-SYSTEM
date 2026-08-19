"""Auth routes: register, login, logout, change password, forgot password."""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from src.services.auth_service import (
    register_user,
    login_user,
    change_password,
    find_user_for_recovery,
    get_recovery_questions,
    verify_recovery_answers,
    reset_password,
    AuthError,
)
from src.content.security_questions import QUESTIONS
from src.utils.decorators import login_required
from src.extensions import limiter

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour")  # slows down bots mass-creating accounts
def register():
    if request.method == "POST":
        # Read one answer per security question. Blank boxes are just
        # skipped, the user only has to fill in a few of them.
        security_answers = {}
        for question in QUESTIONS:
            field_name = f"security_answer_{question['id']}"
            answer = request.form.get(field_name, "").strip()
            if answer:
                security_answers[question["id"]] = answer

        try:
            user = register_user(
                username=request.form.get("username", ""),
                email=request.form.get("email", ""),
                password=request.form.get("password", ""),
                confirm_password=request.form.get("confirm_password", ""),
                security_answers=security_answers,
            )
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Account created successfully.", "success")
            return redirect(url_for("dashboard"))
        except AuthError as e:
            flash(str(e), "error")
            return render_template(
                "register.html",
                username=request.form.get("username", ""),
                email=request.form.get("email", ""),
                questions=QUESTIONS,
            )

    return render_template("register.html", username="", email="", questions=QUESTIONS)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # slows down password-guessing attempts
def login():
    if request.method == "POST":
        try:
            user = login_user(
                username_or_email=request.form.get("identifier", ""),
                password=request.form.get("password", ""),
            )
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("dashboard"))
        except AuthError as e:
            flash(str(e), "error")
            return render_template(
                "login.html", identifier=request.form.get("identifier", "")
            )

    return render_template("login.html", identifier="")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/account/change-password", methods=["GET", "POST"])
@login_required
@limiter.limit("10 per hour")
def change_password_page():
    # This is for someone who IS logged in and DOES remember their current
    # password, they just want to set a new one. Different from recovery.
    if request.method == "POST":
        try:
            change_password(
                user_id=session["user_id"],
                old_password=request.form.get("old_password", ""),
                new_password=request.form.get("new_password", ""),
                confirm_password=request.form.get("confirm_password", ""),
            )
            flash("Password updated successfully.", "success")
            return redirect(url_for("dashboard"))
        except AuthError as e:
            flash(str(e), "error")

    return render_template("change_password.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def forgot_password():
    # Step 1 of recovery: find the account by username or email, then
    # remember WHO is recovering in the session (but do NOT log them in).
    if request.method == "POST":
        identifier = request.form.get("identifier", "")
        try:
            user = find_user_for_recovery(identifier)
            get_recovery_questions(user.id)  # make sure questions exist before continuing
        except AuthError as e:
            flash(str(e), "error")
            return render_template("forgot_password.html", identifier=identifier)

        session["recovery_user_id"] = user.id
        session.pop("recovery_verified", None)
        return redirect(url_for("auth.forgot_password_verify"))

    return render_template("forgot_password.html", identifier="")


@auth_bp.route("/forgot-password/verify", methods=["GET", "POST"])
@limiter.limit("5 per minute")  # security answers are easier to guess than passwords
def forgot_password_verify():
    # Step 2 of recovery: answer the security questions chosen at signup.
    user_id = session.get("recovery_user_id")
    if not user_id:
        flash("Please start the recovery process again.", "error")
        return redirect(url_for("auth.forgot_password"))

    try:
        questions = get_recovery_questions(user_id)
    except AuthError as e:
        flash(str(e), "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        submitted = {
            q["id"]: request.form.get(f"answer_{q['id']}", "") for q in questions
        }
        if verify_recovery_answers(user_id, submitted):
            session["recovery_verified"] = True
            return redirect(url_for("auth.forgot_password_reset"))

        flash("One or more answers were incorrect. Please try again.", "error")

    return render_template("forgot_password_verify.html", questions=questions)


@auth_bp.route("/forgot-password/reset", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def forgot_password_reset():
    # Step 3 of recovery: now that the questions are answered correctly,
    # let the user set a brand new password. No old password needed here.
    user_id = session.get("recovery_user_id")
    verified = session.get("recovery_verified")

    if not user_id or not verified:
        flash("Please complete the recovery steps first.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        try:
            reset_password(
                user_id,
                new_password=request.form.get("new_password", ""),
                confirm_password=request.form.get("confirm_password", ""),
            )
        except AuthError as e:
            flash(str(e), "error")
            return render_template("forgot_password_reset.html")

        # Recovery is done, clear the temporary session state so this
        # can't be replayed to reset the password again later.
        session.pop("recovery_user_id", None)
        session.pop("recovery_verified", None)
        flash("Your password has been reset. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("forgot_password_reset.html")
