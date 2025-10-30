from flask import Flask, request, render_template_string, redirect, make_response, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
import threading
import time

app = Flask(__name__)
app.secret_key = os.urandom(32)

FLAG = os.getenv("FLAG", "DH{FAKE_FLAG}")
ADMIN_PASSWORD = os.urandom(16).hex()

users = {
    'admin': ADMIN_PASSWORD
}

@app.before_request
def prevent_csrf():
    if request.headers.get('Sec-Fetch-Site') is not None and \
       request.headers.get('Sec-Fetch-User') != '?1' and request.method == 'POST':
        return '<script>alert("CSRF detected");history.go(-1);</script>'

@app.route('/', methods=['GET'])
def index():
    name = request.args.get('username', session.get('username', 'guest'))
    return f'<h1>Hello, {name}!</h1>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return '''
            <form method="post">
                Username: <input type="text" name="username"><br>
                Password: <input type="password" name="password"><br>
                <input type="submit" id="submitBtn" value="Login">
            </form>
        '''
    
    username = request.form.get('username')
    password = request.form.get('password')
    if users.get(username) == password:
        resp = make_response(redirect('/'))
        resp.set_cookie('csrf_token', os.urandom(16).hex(), httponly=True)
        session['username'] = username

        return resp
    else:
        return '<script>alert("Invalid credentials");history.go(-1);</script>'

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return '''
            <form method="post">
                Username: <input type="text" name="username"><br>
                Password: <input type="password" name="password"><br>
                <input type="submit" value="Register">
            </form>
        '''
    
    username = request.form.get('username')
    password = request.form.get('password')
    if username in users:
        return "<script>alert('Username already exists');history.go(-1);</script>"
    users[username] = password
    return redirect('/login')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    username = session.get('username')
    csrf_token = request.cookies.get('csrf_token')
    if username is None:
        return redirect("/login")
    
    if request.method == 'GET':
        return render_template_string('''
            <form method="post">
                <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                New Password: <input type="password" name="new_password"><br>
                <input type="submit" value="Change Password">
            </form>
        ''', csrf_token=csrf_token)

    if request.form.get('csrf_token') != csrf_token:
        return '<script>alert("Invalid CSRF token");history.go(-1);</script>'
    
    new_password = request.form.get('new_password', '')
    users[username] = new_password
    return '<script>alert("Password changed successfully");history.go(-1);</script>'

@app.route('/admin', methods=['POST'])
def admin():
    username = session.get('username')
    if username != 'admin':
        return redirect('/')
    return FLAG

@app.route('/report', methods=["GET", "POST"])
def report():
    username = session.get('username')
    if username is None:
        return redirect("/login")
    
    if request.method == "GET":
        return '''
            <form method="post">
                Report URL: <input type="text" name="url"><br>
                <input type="submit" value="Report">
            </form>
        '''
    
    url = request.form.get("url", "")
    if not url.startswith("http://") and not url.startswith("https://"):
        return '<script>alert("Invalid URL");history.go(-1);</script>'
    
    t = threading.Thread(target=visit_url, args=(url,))
    t.start()

    return '<script>alert("URL reported successfully");history.go(-1);</script>'

def visit_url(url):
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--window-size=1920x1080')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)

        driver.get("http://localhost:3000/login")
        driver.find_element(by=By.NAME, value="username").send_keys("admin")
        driver.find_element(by=By.NAME, value="password").send_keys(ADMIN_PASSWORD)
        driver.find_element(by=By.ID, value="submitBtn").click()
        time.sleep(1)

        driver.get(url)
        time.sleep(1)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
