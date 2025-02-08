from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import yagmail
from glob import glob
from prediction import modelPrediction
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "videoAnomly"


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form["email"]
        pwd = request.form["pwd"]
        # pwd = str(pwd)
        r1 = pd.read_excel('user.xlsx')
        print(f'email and pwd : {email, pwd}')
        for index, row in r1.iterrows():
            if row["email"] == str(email) and row["password"] == str(pwd):
                session['email'] = email  
                return redirect(url_for('home'))


        mesg = 'Invalid Login Try Again'
        return render_template('login.html', msg=mesg)
    else:
        return render_template('login.html')





@app.route('/register', methods=['POST', 'GET'])
def register():
    try:
        if request.method == 'POST':
            email = request.form['email']
            pwd = request.form['pwd']
            repwd = request.form['repwd']

            if pwd == repwd:  # Check if passwords match
                col_list = ["email", "password"]
                try:
                    # Try reading the existing file, if it exists
                    r1 = pd.read_excel('user.xlsx', usecols=col_list)
                except FileNotFoundError:
                    # If the file doesn't exist, create an empty DataFrame
                    r1 = pd.DataFrame(columns=col_list)

                # Check if the email already exists
                if email in r1['email'].values:
                    msg = 'Email already exists. Please use a different email.'
                    return render_template('register.html', msg=msg)

                # Append the new record
                new_row = pd.DataFrame({'email': [email], 'password': [pwd]})
                r1 = pd.concat([r1, new_row], ignore_index=True)
                r1.to_excel('user.xlsx', index=False)

                print("Records created successfully")
                msg = 'Registration Successful. You can log in here.'
                return render_template('login.html', msg=msg)
            else:
                msg = 'Password and Re-enter password do not match.'
                return render_template('register.html', msg=msg)

        return render_template('register.html')
    except Exception as e:
        return render_template('register.html', msg=str(e))
     


@app.route("/home")
def home():   
    if 'email' in session:
        return render_template("index.html")
    else:
        return render_template('login.html')


def sendmail(result, user_mails, video_path):  
    try:
        yag = yagmail.SMTP(user='tejashwinipatil2003@gmail.com', password='forauqtzsrhsjshc')
        for user_mail in user_mails:
            mail_contents = [f"\n \n {result} Suspicious Action is being Detected in ATM center. \n \n"]
            yag.send(to=user_mail, subject=f"{result} Action is being Detected",
                     contents=mail_contents, attachments=video_path)  

        print('[SUCCESS]  > Email sent successfully...')
        return "success"
    except Exception as e:
        print('[FAILED]    >', e)
        return "failed"


@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'email' in session:
        email_id = session['email']
        video_path = ""
        predict_pro = 0
        msg = ''

        if request.method == 'POST':
            video_file = request.files['video']
            print("video_file : ", video_file)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            video_filename = f"uploaded_video_{timestamp}.mp4"

            # Construct the full path with the timestamped filename
            video_path = f"static/source_video/{video_filename}"

            video_file.save(video_path)

            predict_pro = modelPrediction(video_path)

            print("video_path : ", video_path)

            if predict_pro != "Normal" and os.path.isfile(video_path):
                other_recipients = [email_id, ] 
                mail = sendmail(predict_pro, user_mails=other_recipients, video_path=video_path)

                if mail == "success":
                    msg = "File sent to " + email_id
                else:
                    msg = "Oops!! File sending failed to " + email_id

            print(" predict_pro : ", predict_pro, " msg:", msg)

            frame_paths = glob("static/temp/*.jpg")
            print(f"frame_paths : {frame_paths}")

        return render_template('index.html', images=frame_paths, video_path=video_path, pro=predict_pro, msg=msg)
    else:
        return redirect(url_for('login'))


@app.route('/password', methods=['POST', 'GET'])
def password():
    if 'email' in session:    
        if request.method == 'POST':
            current_pass = request.form['current']
            new_pass = request.form['new']
            verify_pass = request.form['verify']
            r1 = pd.read_excel('user.xlsx')
            for index, row in r1.iterrows():
                if row["password"] == str(current_pass):
                    if new_pass == verify_pass:
                        r1.loc[index, "password"] = verify_pass
                        r1.to_excel("user.xlsx", index=False)
                        msg1 = 'Password changed successfully'
                        return render_template('password.html', msg=msg1)
                    else:
                        msg = 'Re-entered password is not matched'
                        return render_template('password.html', msg=msg)
            else:
                msg3 = 'Incorrect Password'
                return render_template('password.html', msg=msg3)
        return render_template('password.html')
    else:
        return redirect(url_for('login'))


@app.route("/graph")
def graph():
    if 'email' in session:
        return render_template("graphs.html")
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None) 
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5003)
