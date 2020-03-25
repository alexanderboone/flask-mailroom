import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from passlib.hash import pbkdf2_sha256

from model import User, Donation, Donor

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY').encode()

@app.route('/')
def home():
    return redirect(url_for('all'))

@app.route('/donations/')
def all():
    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)

@app.route('/new-donation/', methods=['GET', 'POST'])
def new_donation():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        donor_name = request.form['donor_name']
        donation_amt = request.form['donation_amount']
        Donation(value=donation_amt, donor=Donor.get(Donor.name==donor_name)).save()
        return redirect(url_for('home'))
    else:
        donors = Donor.select()
        return render_template('new-donation.jinja2', donors=donors)

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = User.select().where(User.name == request.form["username"]).get()
        except User.DoesNotExist:
            user=''
            error_message="Incorrect username or password."

        if user and pbkdf2_sha256.verify(request.form["password"], user.password):
            session['username'] = request.form["username"]
            return redirect(url_for('new_donation'))
        return render_template('login.jinja2', error=error_message)
    else:
        return render_template('login.jinja2')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

