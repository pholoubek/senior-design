from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Content, Notification
from app import db
from app.auth.forms import LoginForm, RegisterForm, ResetPasswordForm
from app.emails.functions import send_confirmation_email
from werkzeug.urls import url_parse
from datetime import datetime
from flask import g, jsonify, make_response

from app.auth import bp
from datetime import datetime, timedelta
from app.auth.functions import username_exists, email_exists
from app.cookies_ccg import set_logout_time_cookie

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:    #  check if user is already logged
        return redirect(url_for('main.index'))

    logForm = LoginForm()      # form = LoginForm() - why arg request.form
    if logForm.validate_on_submit():
        #  retrieve user's password with username
        user = User.query.filter_by(username=g.logForm.username.data).first()

        #  if user doesn't exist print 'here func'or the password doesn't match
        if user is None or not user.check_password(g.logForm.password.data):
            flash('Incorrect username or password')
            return redirect(url_for('auth.login'))

        else:
            # if the user is registered in database but his email is not confirmed
            if user.confirmed is False:
                flash("You didn't confirmed your email. Check your email!")
                return redirect(url_for('emails.resend_confirmation_email_request'))

            #  remember sets always to True
            login_user(user, remember=True)
            #  query which keeps url to be redirected if an user was redirected due to not being logged in d
            next_page = request.args.get('next')
            #  if next_page is None or next arg is set to to absolute URL
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('main.index')

            return redirect(next_page)
    return render_template('auth/login.html', logForm=logForm)

@bp.route('/logout')
def logout():
    logout_user()
    response = set_logout_time_cookie()
    if response:
        return response # with cookie
    else:
        return redirect(url_for('main.index')) # without cookie


@bp.route('/register', methods=['GET', 'POST'])
def register():
    #  if user is logged in, redirect
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    regForm = RegisterForm()
    if regForm.validate_on_submit():
        #  create object user from app.models with the following attributes
        user = User(
            username = regForm.username.data,
            email = regForm.email.data,
        )

        user.set_password(regForm.password.data)
        user.set_default_avatar_hash()
        #  add user and commit into the database
        db.session.add(user)
        db.session.commit()
        send_confirmation_email(user) # send activation link to user's email
        flash('A confirmation email has been sent.', 'success')
        return redirect(url_for('main.index'))
    return render_template('auth/register2.html', regForm=regForm)

#  used for global forms
@bp.before_app_request
def before_request():
    g.login_form = LoginForm()
    g.register_form = RegisterForm()

@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # reset user's password
    # arg- token is jwt token
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_password_token(token)
    if user is None: # invalid token
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('main.index'))

    resetPwForm = ResetPasswordForm()
    if resetPwForm.validate_on_submit():
        new_pw = resetPwForm.password.data
        user.set_password(new_pw)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=resetPwForm)


@bp.route('/confirm_email/<token>', methods=['GET', 'POST'])
def confirm_email(token):
    # confirm user's new account via email
    # arg- token is jwt token
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_email_confirmation_token(token)
    if user is None: # invalid token
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('emails.resend_confirmation_email_request'))

    elif user.confirmed: # User's account is already confirmed
        flash('Your account is already confirmed. Please login.', 'success')
        return redirect(url_for('auth.login'))

    else: # account is confirmed make changes in db
        user.confirmed = True
        user.confirmed_on = datetime.now()

        #  For finally confirmed users create notificationHub
        notificationHub = Notification(userID = user.id)

        db.session.add(notificationHub)
        db.session.commit()
        flash('your account has been confirmed. please login.', 'success')

        ## automatically connect user after successfull account confirmation
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')

        #TODO: -> flash to NAVBAR
        flash('You are now logged in!', 'success')
        return redirect(next_page)
