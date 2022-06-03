from flask import (
    Blueprint, request, render_template, current_app, url_for, redirect, session
)
from flask_mail import Message, Mail
from itsdangerous import URLSafeTimedSerializer

from configuration import config
from database_adapter import adapter

bp = Blueprint('email', __name__, url_prefix='/email')


@bp.route('/confirm/<user_email>', methods=('GET', 'POST'))
def confirm_email(user_email):
    current_app.logger.info(f"{user_email} needs to confirm email.")
    if request.method == 'POST':
        current_app.logger.info(f"Sending a confirmation token to {user_email}.")
        token = generate_confirmation_token(user_email)
        confirm_url = url_for('.confirm_email_token', token=token, _external=True)
        html = render_template('email/email_confirmation.html', confirm_url=confirm_url)
        subject = "Cinema-eBooking Email Confirmation Link"
        send_email(user_email, subject, html)
        return render_template('email/confirmation_email_sent.html')
    return render_template('email/confirm_email.html')


@bp.route('/forgot/<user_email>', methods=('GET', 'POST'))
def send_password_reset_email(user_email):
    current_app.logger.info(f"{user_email} has forgotten password.")
    current_app.logger.info(f"Sending a confirmation token to {user_email}.")
    token = generate_confirmation_token(user_email)
    reset_url = url_for('.reset_password', token=token, _external=True)
    html = render_template('email/reset_password.html', reset_url=reset_url)
    subject = "Cinema-eBooking Password Reset Link"
    send_email(user_email, subject, html)
    return render_template('email/forgot_password_email_sent.html')


@bp.route('/booking_confirmation/<user_email>')
def send_booking_confirmation(user_email):
    current_app.logger.info(f"Sending a booking confirmation email to {user_email}")
    booking_info: dict = session.get('confirm_info')
    html = render_template('email/booking_email.html', total=booking_info.get('total'), booking_num=booking_info.get('booking_num'))  # TODO provide booking metadata
    subject = "Cinema-eBooking Confirmation Email"
    send_email(user_email, subject, html)
    return render_template('email/booking_confirmed.html', total=booking_info.get('total'), booking_num=booking_info.get('booking_num'))


@bp.route('/reset/<token>')
def reset_password(token):
    try:
        email = confirm_token(token)
        session['user_email'] = email
        current_app.logger.info(f"{email} has confirmed email token for password reset.")
    except:
        current_app.logger.info(f"Timeout Expired.")
    session['RESET_PASSWORD'] = True
    return redirect(url_for('user.change_password'))


@bp.route('/confirmation/<token>')
def confirm_email_token(token):
    email = str()
    try:
        email = confirm_token(token)
    except:
        current_app.logger.info(f"Timeout Expired.")

    current_app.logger.info(f"User {email} already confirmed.") if adapter.get_email_confirmed(
        email) else adapter.set_email_confirmed(email)
    current_app.logger.info(f"{email} has confirmed email token for email confirmation.")
    return redirect(url_for('.email_confirmed'))


@bp.route('/confirmed', methods=('GET', 'POST'))
def email_confirmed():
    if request.method == 'POST':
        return redirect(url_for('user.login'))
    return render_template('email/email_confirmed.html')


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(config['confirmation_email']['secret_key'])
    return serializer.dumps(email, salt=config['confirmation_email']['security_password_salt'])


def confirm_token(token, expiration=config['confirmation_email']['expiration']):
    serializer = URLSafeTimedSerializer(config['confirmation_email']['secret_key'])
    try:
        email = serializer.loads(
            token,
            salt=config['confirmation_email']['security_password_salt'],
            max_age=expiration
        )
    except:
        return False
    return email


def send_email(to, subject, template):
    to = [to] if type(to) != list else to
    msg = Message(
        subject,
        recipients=to,
        sender=config['confirmation_email']['sending_email'],
        html=template
    )
    mail = Mail()
    mail.init_app(current_app)
    mail.send(msg)
