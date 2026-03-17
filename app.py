"""
SAFE-SURF AI | THREAT INTELLIGENCE PLATFORM
Developed by: Dikshant Sharma (Lead Architect)
Version: 4.5 (Integrated Intelligence Dashboard + Forensic Fixes)
"""

import os, pickle, logging, smtplib, random, sqlite3, hashlib, io, requests, base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_cors import CORS 
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Matplotlib integration for Headless Server Analytics
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt

from models import db, User, SearchHistory
from features import extract_features

app = Flask(__name__)
CORS(app) 

app.config['SECRET_KEY'] = 'safesurf_v2_dikshant_sharma_intel_platform'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'safesurf.db')
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'profile_pics')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 

OTP_SENDER_EMAIL = "safesurfai@gmail.com" 
OTP_SENDER_PASSWORD = "ipsu zrmx rwit kwlv" 

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- ML INTELLIGENCE ---
model_path = os.path.join(basedir, 'classifier.pkl')
try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    logger.info("Intelligence Engine: Online")
except Exception as e:
    logger.error(f"Inference Engine Crash: {str(e)}")

# --- CORE UTILITIES ---

def force_ascii(text):
    if text is None: return ""
    return "".join(i for i in str(text) if 31 < ord(i) < 127)

def expand_url(url):
    """Reveals true destination using Browser-Grade headers to avoid bot-blocking."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, allow_redirects=True, timeout=5, headers=headers, stream=True)
        return response.url
    except Exception as e:
        logger.warning(f"Expansion Failed for {url}: {str(e)}")
        return url

def analyze_url(url):
    expanded_url = expand_url(url)
    f_list, f_analytics, force_phish = extract_features(expanded_url)
    prediction = model.predict(f_list)
    final_code = -1 if (force_phish or prediction[0] == -1) else 1
    return final_code, f_list, f_analytics, expanded_url

def send_otp_email(receiver_email, otp_code, subject_type="MFA Login"):
    msg = MIMEMultipart()
    msg['From'] = f"Safe-Surf AI Gateway <{OTP_SENDER_EMAIL}>"
    msg['To'] = receiver_email
    msg['Subject'] = f"SAFE-SURF AI: {subject_type} Code"
    body = f"SECURITY ALERT: Verification Requested.\n\nYour code is: {otp_code}"
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(OTP_SENDER_EMAIL, OTP_SENDER_PASSWORD)
        server.send_message(msg); server.quit()
        return True
    except: return False

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def mfa_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated and not session.get('mfa_passed'):
            flash("Identity Verification Required.", "warning")
            return redirect(url_for('mfa_verify'))
        return f(*args, **kwargs)
    return decorated_function

# --- API & ROUTES ---

@app.route('/api/v1/scan', methods=['POST'])
def api_scan():
    data = request.json
    silent = data.get('silent', False)
    if not data or 'url' not in data:
        return jsonify({"status": "error", "message": "No URL provided"}), 400
    try:
        url = data.get('url')
        final_code, f_list, f_analytics, expanded_url = analyze_url(url)
        res_text = "PHISHING ⚠️" if final_code == -1 else "SAFE ✅"
        
        if not silent:
            target_uid = current_user.id if current_user.is_authenticated else 1
            new_scan = SearchHistory(url=expanded_url, result=res_text, user_id=target_uid)
            db.session.add(new_scan)
            db.session.commit()

        return jsonify({
            "status": "success", "architect": "Dikshant Sharma",
            "verdict": "PHISHING" if final_code == -1 else "SAFE",
            "score": round((f_list[0].count(1) / len(f_list[0])) * 100, 1),
            "forensics": f_analytics,
            "expanded_url": expanded_url
        })
    except Exception as e: 
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/')
def home(): return render_template('home.html')

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/scan', methods=['GET', 'POST'])
@login_required
@mfa_required
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if not url: flash("No URL detected.", "warning"); return redirect(url_for('index'))
        try:
            final_code, f_list, f_analytics, expanded_url = analyze_url(url)
            res_text = "PHISHING ⚠️" if final_code == -1 else "SAFE ✅"
            res_color = "#ff4d4d" if final_code == -1 else "#00f2fe"
            db.session.add(SearchHistory(url=expanded_url, result=res_text, user_id=current_user.id))
            db.session.commit()
            return render_template('index.html', prediction_text=res_text, res_color=res_color, url=expanded_url, analytics=f_analytics)
        except Exception as e:
            db.session.rollback(); flash(f"Engine Error: {str(e)}", "danger"); return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/admin')
@login_required
@mfa_required
def admin():
    if not current_user.is_admin: flash("Forbidden.", "danger"); return redirect(url_for('home'))
    
    users = User.query.all()
    history = SearchHistory.query.all()
    phish_count = SearchHistory.query.filter(SearchHistory.result.like('%PHISHING%')).count()
    safe_count = len(history) - phish_count
    recent_scans = SearchHistory.query.order_by(SearchHistory.timestamp.desc()).limit(10).all()
    trend_data = [1 if 'SAFE' in s.result else 0 for s in reversed(recent_scans)]

    # --- GENERATE LIVE THREAT CHART (MEMORY BUFFER) ---
    chart_url = None
    if len(history) > 0:
        plt.figure(figsize=(5, 5))
        plt.pie([safe_count, phish_count], labels=['Safe', 'Phishing'], 
                colors=['#00f2fe', '#ff4d4d'], autopct='%1.1f%%', startangle=140)
        plt.title("Platform Threat Distribution", color='white', fontweight='bold')
        plt.gcf().set_facecolor('none') # Transparent background for UI
        
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', transparent=True)
        img.seek(0)
        chart_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

    db_path = os.path.join(basedir, 'safesurf.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    reports = conn.execute("SELECT * FROM reports ORDER BY timestamp DESC").fetchall()
    conn.close()
    
    return render_template('admin.html', users=users, history=history, reports=reports, 
                           safe_count=safe_count, phish_count=phish_count, trend_data=trend_data, 
                           chart_url=chart_url)

@app.route('/report', methods=['POST'])
@login_required
def report():
    target_url = request.form.get('target_url')
    comment = request.form.get('comment')
    db_path = os.path.join(basedir, 'safesurf.db')
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("INSERT INTO reports (url, comment) VALUES (?, ?)", (target_url, comment))
        conn.commit(); conn.close()
        return redirect(url_for('index', reported='true'))
    except Exception as e:
        logger.error(f"Reporting Error: {str(e)}")
        flash("Error logging threat data.", "danger"); return redirect(url_for('index'))

@app.route('/download_report/<path:url>/<result>')
@login_required
@mfa_required
def download_report(url, result):
    try:
        final_code, f_list, f_analytics, expanded_url = analyze_url(url)
        p_total, p_pass = len(f_list[0]), f_list[0].count(1)
        safety_score = round((p_pass / p_total) * 100, 1)
        clean_url, clean_result = force_ascii(expanded_url), force_ascii(result).strip()
        raw_sig = f"{expanded_url}{result}{datetime.now().strftime('%Y%m%d%H%M')}{app.config['SECRET_KEY']}"
        digital_sig = hashlib.sha256(raw_sig.encode()).hexdigest()[:12].upper()

        pdf = FPDF()
        pdf.add_page(); pdf.set_fill_color(252, 252, 252); pdf.rect(0, 0, 210, 297, 'F')
        pdf.set_font("courier", 'B', 16); pdf.set_text_color(0, 150, 180)
        pdf.cell(0, 10, text="SAFE-SURF AI | THREAT AUDIT REPORT v3.2", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.set_font("courier", '', 9); pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, text=f"LEAD ARCHITECT: DIKSHANT SHARMA | REF ID: {digital_sig}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C'); pdf.ln(5)
        pdf.set_font("courier", 'B', 10); pdf.set_text_color(50, 50, 50); pdf.write(5, "TARGET URL: "); pdf.set_font("courier", '', 10); pdf.multi_cell(0, 5, text=clean_url); pdf.ln(5)

        v_bg = (255, 230, 230) if "PHISHING" in clean_result else (230, 255, 250)
        v_text = (200, 0, 0) if "PHISHING" in clean_result else (0, 120, 120)
        pdf.set_fill_color(*v_bg); pdf.set_text_color(*v_text); pdf.set_font("courier", 'B', 14)
        pdf.cell(0, 12, text=f"FINAL VERDICT: {clean_result}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C', fill=True); pdf.ln(5)

        pdf.set_text_color(0, 100, 130); pdf.set_font("courier", 'B', 11)
        pdf.cell(0, 10, text="[DNA STATISTICAL BREAKDOWN]", new_x=XPos.LMARGIN, new_y=YPos.NEXT); pdf.set_font("courier", '', 10); pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 7, text=f"- Total Points Analyzed: {p_total}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 7, text=f"- Safety Points Passed:  {p_pass}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(0, 7, text=f"- Overall Safety Score:  {safety_score}%", new_x=XPos.LMARGIN, new_y=YPos.NEXT); pdf.ln(5)

        pdf.set_text_color(0, 80, 110); pdf.set_font("courier", 'B', 11); pdf.cell(0, 10, text="[SECURITY ADVISORY: PREVENTION TIPS]", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(80, 80, 80); pdf.set_font("courier", '', 9)
        pdf.multi_cell(0, 6, text="1. THE URGENCY TRAP: Avoid keywords like 'verify' or 'account-locked'.\n2. BRAND IMPOSTERS: Watch for typos like 'g00gle.com' or 'paypa1.com'.\n3. IP ADDRESS RED FLAG: Legitimate sites use domains, not raw IPs.\n4. PROTOCOL VULNERABILITY: Avoid sites using unencrypted HTTP.")

        pdf.set_y(-25); pdf.set_font("courier", 'I', 7); pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 5, text=f"SYSTEM TIMESTAMP: {datetime.now(timezone.utc).isoformat()} UTC", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.cell(0, 5, text="READ-ONLY FORENSIC DOCUMENT | AI-VERIFIED INTEGRITY", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        return send_file(io.BytesIO(pdf.output()), as_attachment=True, download_name=f"SafeSurf_Audit_{digital_sig}.pdf", mimetype='application/pdf')
    except Exception as e: flash(f"Forensic Error: {str(e)}", "danger"); return redirect(url_for('history'))

@app.route('/admin/update_email', methods=['POST'])
@login_required
def update_email():
    if not current_user.is_admin: return redirect(url_for('home'))
    user_id, new_email = request.form.get('user_id'), request.form.get('new_email')
    user = User.query.get(user_id)
    if user: user.email = new_email; db.session.commit(); flash(f"Email updated.", "success")
    return redirect(url_for('admin'))

@app.route('/admin/delete_user/<int:user_id>')
@login_required
def delete_user(user_id):
    if not current_user.is_admin: return redirect(url_for('home'))
    user = User.query.get(user_id)
    if user and not user.is_admin:
        SearchHistory.query.filter_by(user_id=user.id).delete(); db.session.delete(user); db.session.commit(); flash(f"User purged.", "success")
    return redirect(url_for('admin'))

@app.route('/history')
@login_required
@mfa_required
def history():
    user_scans = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.timestamp.desc()).all()
    return render_template('history.html', searches=user_scans)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
@mfa_required
def profile():
    if request.method == 'POST':
        nickname = request.form.get('nickname')
        if nickname: current_user.nickname = nickname
        if 'profile_pic' in request.files:
            pic = request.files['profile_pic']
            if pic and pic.filename != '':
                filename = secure_filename(pic.filename); os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True); pic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)); current_user.profile_pic = filename
        db.session.commit(); flash("Profile Updated.", "success"); return redirect(url_for('home')) 
    return render_template('profile.html', user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']): 
            session['mfa_user_id'] = user.id
            return redirect(url_for('mfa_verify'))
        flash("Invalid credentials.", "danger")
    return render_template('login.html')

@app.route('/mfa_verify', methods=['GET', 'POST'])
def mfa_verify():
    mfa_user_id = session.get('mfa_user_id')
    if not mfa_user_id: return redirect(url_for('login'))
    user = User.query.get(mfa_user_id)
    if request.method == 'GET' and 'mfa_otp' not in session:
        otp = str(random.randint(100000, 999999)); session['mfa_otp'] = otp; send_otp_email(user.email, otp)
    if request.method == 'POST':
        if request.form.get('otp') == session.get('mfa_otp'):
            login_user(user); session['mfa_passed'] = True; session.pop('mfa_user_id', None); session.pop('mfa_otp', None); return redirect(url_for('index'))
        flash("Invalid OTP.", "danger")
    return render_template('mfa.html', email=user.email)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_researcher = User(username=request.form['username'], email=request.form['email'], password=hashed_pw)
        if User.query.count() == 0: new_researcher.is_admin = True
        try: db.session.add(new_researcher); db.session.commit(); flash("Registered!", "success"); return redirect(url_for('login'))
        except: flash("Error: Account exists.", "danger")
    return render_template('register.html')

@app.route('/logout')
def logout(): logout_user(); session.clear(); return redirect(url_for('home'))

@app.route('/forgot_password')
def forgot_password(): 
    flash("Credential recovery under maintenance.", "info"); return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(debug=True)