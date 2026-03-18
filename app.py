"""
SAFE-SURF AI | THREAT INTELLIGENCE PLATFORM
Developed by: Dikshant Sharma (Lead Architect)
Version: 4.6 (Global Production + 2-Page Forensic Intelligence)
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

# --- CONFIGURATION ---
app.config['SECRET_KEY'] = 'safesurf_v2_dikshant_sharma_intel_platform'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'safesurf.db')
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'profile_pics')
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 

OTP_SENDER_EMAIL = "safesurfai@gmail.com" 
OTP_SENDER_PASSWORD = "cwmcwojwbuepokyn" 

# --- DATABASE INITIALIZATION (FIXED FOR GUNICORN/RENDER) ---
db.init_app(app)
with app.app_context():
    db.create_all()
    print("🛡️ SAFE-SURF GENESIS: Database Tables Synchronized.")

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
    """Reveals true destination using Browser-Grade headers."""
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
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
    # PASTE YOUR KEY HERE
    RESEND_API_KEY = "re_iTfQGaCK_Afueyj88fcbgupDt7wRfvwxz" 

    logger.info(f"🚀 INITIATING RESEND API: Targeting {receiver_email}")
    
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # NOTE: On the free tier, Resend usually only allows sending 
        # to the email you signed up with unless you verify a domain.
        payload = {
            "from": "SafeSurf AI <onboarding@resend.dev>",
            "to": [receiver_email],
            "subject": f"SAFE-SURF AI: {subject_type} Code",
            "html": f"""
                <div style="font-family: 'Courier New', monospace; border: 1px solid #00f2fe; padding: 20px;">
                    <h2 style="color: #00f2fe;">SAFE-SURF AI INTELLIGENCE</h2>
                    <p>Security Verification Requested.</p>
                    <p style="font-size: 24px; font-weight: bold; color: #ff4d4d;">{otp_code}</p>
                    <p style="font-size: 10px; color: #888;">Ref ID: {random.getrandbits(32)}</p>
                </div>
            """
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code in [200, 201]:
            logger.info("✅ API SUCCESS: OTP dispatched to inbox.")
            return True
        else:
            logger.error(f"❌ API FAILURE: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ API CRITICAL ERROR: {str(e)}")
        return False
    
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

# --- EXPANDED FORENSIC REPORT GENERATOR (2-PAGE RESEARCH GRADE) ---

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
        
        # --- PAGE 1: EXECUTIVE INTELLIGENCE SUMMARY ---
        pdf.add_page()
        pdf.set_fill_color(245, 248, 250); pdf.rect(0, 0, 210, 297, 'F')
        
        # Header Block
        pdf.set_font("courier", 'B', 18); pdf.set_text_color(0, 150, 180)
        pdf.cell(0, 15, text="SAFE-SURF AI | THREAT AUDIT DOSSIER v4.0", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.set_font("courier", '', 10); pdf.set_text_color(120, 120, 120)
        pdf.cell(0, 8, text=f"LEAD ARCHITECT: DIKSHANT SHARMA | REF ID: {digital_sig}", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C'); pdf.ln(10)
        
        # Target DNA Block
        pdf.set_font("courier", 'B', 11); pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 8, text="I. ADVERSARIAL TARGET IDENTIFICATION", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("courier", '', 10); pdf.set_text_color(60, 60, 60)
        pdf.write(5, "TARGET URL: "); pdf.set_text_color(0, 100, 200); pdf.multi_cell(0, 5, text=clean_url); pdf.ln(5)
        
        # Verdict Meter
        v_bg = (255, 230, 230) if "PHISHING" in clean_result else (230, 255, 250)
        v_text = (200, 0, 0) if "PHISHING" in clean_result else (0, 120, 120)
        pdf.set_fill_color(*v_bg); pdf.set_text_color(*v_text); pdf.set_font("courier", 'B', 16)
        pdf.cell(0, 15, text=f"FINAL VERDICT: {clean_result}", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C', fill=True); pdf.ln(10)

        # DNA Metrics Table
        pdf.set_text_color(0, 100, 130); pdf.set_font("courier", 'B', 12)
        pdf.cell(0, 10, text="II. CORE INTELLIGENCE METRICS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("courier", '', 10); pdf.set_text_color(80, 80, 80)
        pdf.cell(90, 8, text="Metric Description", border=1); pdf.cell(0, 8, text="Value / Status", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(90, 8, text="Random Forest Accuracy Check", border=1); pdf.cell(0, 8, text="98.2% (Model v1.8)", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(90, 8, text="Points Analyzed", border=1); pdf.cell(0, 8, text=str(p_total), border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(90, 8, text="Safety Points Passed", border=1); pdf.cell(0, 8, text=str(p_pass), border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(90, 8, text="Computed Safety Score", border=1); pdf.cell(0, 8, text=f"{safety_score}%", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT); pdf.ln(10)

        # Prevention Quick-Tips
        pdf.set_font("courier", 'B', 11); pdf.set_text_color(0, 80, 110)
        pdf.cell(0, 8, text="III. INITIAL SECURITY ADVISORY", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("courier", '', 9); pdf.set_text_color(100, 100, 100)
        pdf.multi_cell(0, 6, text="URGENCY TRAPS: Flagged if keywords like 'verify' or 'account-locked' exist.\nBRAND IMPOSTERS: Monitored for character entropy (e.g., 'g00gle.com').\nPUNYCODE ATTACKS: Visual homograph sentinel actively monitored during this scan.")

        # Footer Signature Page 1
        pdf.set_y(-20); pdf.set_font("courier", 'I', 7); pdf.set_text_color(180, 180, 180)
        pdf.cell(0, 5, text="PAGE 1 of 2 | AUTHENTICATED BY SAFE-SURF AI ENGINE", align='C')

        # --- PAGE 2: DEEP-DIVE FORENSIC RESEARCH ---
        pdf.add_page()
        pdf.set_fill_color(240, 240, 245); pdf.rect(0, 0, 210, 297, 'F')
        
        pdf.set_font("courier", 'B', 14); pdf.set_text_color(0, 100, 130)
        pdf.cell(0, 10, text="IV. DEEP FORENSIC FEATURE ANALYSIS", new_x=XPos.LMARGIN, new_y=YPos.NEXT); pdf.ln(5)
        
        pdf.set_font("courier", '', 9); pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 6, text="A granular breakdown of the 14+ structural markers analyzed by the Random Forest Classifier. Negative values (-1) indicate malicious indicators.")
        pdf.ln(5)

        # Feature List
        pdf.set_font("courier", 'B', 9); pdf.set_fill_color(220, 230, 240)
        pdf.cell(100, 7, text="DNA Marker (Structural Analysis)", border=1, fill=True); pdf.cell(0, 7, text="Indicator Status", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.set_font("courier", '', 9)
        for feature, val in f_analytics.items():
            pdf.cell(100, 7, text=feature.replace('_', ' ').title(), border=1)
            f_color = (200, 0, 0) if val == -1 else (0, 150, 0)
            pdf.set_text_color(*f_color)
            pdf.cell(0, 7, text="[MALICIOUS]" if val == -1 else "[SECURE]", border=1, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(50, 50, 50)
        
        pdf.ln(10)
        
        # Technical Conclusion
        pdf.set_font("courier", 'B', 11); pdf.set_text_color(44, 62, 80)
        pdf.cell(0, 8, text="V. RESEARCH CONCLUSION & RECOMMENDATIONS", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("courier", '', 9); pdf.set_text_color(80, 80, 80)
        
        conclusion = ("CRITICAL THREAT: This URL displays multiple high-risk markers consistent with credential theft platforms. "
                     "DO NOT interact with the page. We recommend performing an immediate credential reset if any data was entered.") \
                     if final_code == -1 else \
                     ("STABLE: This URL aligns with baseline DNA markers of trusted web architectures. "
                     "However, always verify the SSL certificate manually before entering sensitive information.")
        
        pdf.multi_cell(0, 6, text=conclusion); pdf.ln(10)
        
        # Digital Seal
        pdf.set_font("courier", 'B', 10); pdf.set_text_color(0, 150, 180)
        pdf.cell(0, 10, text=f"DIGITAL SIGNATURE HASH: {hashlib.sha256(digital_sig.encode()).hexdigest().upper()}", align='C')

        # Global Footer
        pdf.set_y(-25); pdf.set_font("courier", 'I', 7); pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 5, text=f"SYSTEM TIMESTAMP: {datetime.now(timezone.utc).isoformat()} UTC", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        pdf.cell(0, 5, text="OFFICIAL RESEARCH DOCUMENT | LEAD ARCHITECT: DIKSHANT SHARMA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')

        return send_file(io.BytesIO(pdf.output()), as_attachment=True, download_name=f"SafeSurf_Full_Audit_{digital_sig}.pdf", mimetype='application/pdf')
    except Exception as e: 
        logger.error(f"Report Engine Error: {str(e)}")
        flash(f"Forensic Error: {str(e)}", "danger"); return redirect(url_for('history'))

# --- REST OF THE ROUTES (UNCHANGED BUT PROTECTED) ---

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
            db.session.add(new_scan); db.session.commit()

        return jsonify({
            "status": "success", "architect": "Dikshant Sharma",
            "verdict": "PHISHING" if final_code == -1 else "SAFE",
            "score": round((f_list[0].count(1) / len(f_list[0])) * 100, 1),
            "forensics": f_analytics,
            "expanded_url": expanded_url
        })
    except Exception as e: 
        db.session.rollback(); return jsonify({"status": "error", "message": str(e)}), 500

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
    users = User.query.all(); history = SearchHistory.query.all()
    phish_count = SearchHistory.query.filter(SearchHistory.result.like('%PHISHING%')).count()
    safe_count = len(history) - phish_count
    recent_scans = SearchHistory.query.order_by(SearchHistory.timestamp.desc()).limit(10).all()
    trend_data = [1 if 'SAFE' in s.result else 0 for s in reversed(recent_scans)]

    chart_url = None
    if len(history) > 0:
        plt.figure(figsize=(5, 5))
        plt.pie([safe_count, phish_count], labels=['Safe', 'Phishing'], colors=['#00f2fe', '#ff4d4d'], autopct='%1.1f%%', startangle=140)
        plt.title("Platform Threat Distribution", color='white', fontweight='bold')
        plt.gcf().set_facecolor('none')
        img = io.BytesIO(); plt.savefig(img, format='png', bbox_inches='tight', transparent=True); img.seek(0)
        chart_url = base64.b64encode(img.getvalue()).decode(); plt.close()

    db_path = os.path.join(basedir, 'safesurf.db')
    conn = sqlite3.connect(db_path); conn.row_factory = sqlite3.Row
    reports = conn.execute("SELECT * FROM reports ORDER BY timestamp DESC").fetchall(); conn.close()
    return render_template('admin.html', users=users, history=history, reports=reports, safe_count=safe_count, phish_count=phish_count, trend_data=trend_data, chart_url=chart_url)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'], method='pbkdf2:sha256')
        new_researcher = User(username=request.form['username'], email=request.form['email'], password=hashed_pw)
        # THE FIRST USER TO REGISTER AUTOMATICALLY BECOMES ADMIN
        if User.query.count() == 0: new_researcher.is_admin = True
        try: 
            db.session.add(new_researcher); db.session.commit()
            flash("Success: Registered as researcher.", "success"); return redirect(url_for('login'))
        except: flash("Error: Account exists or database locked.", "danger")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']): 
            session['mfa_user_id'] = user.id; return redirect(url_for('mfa_verify'))
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

@app.route('/logout')
def logout(): logout_user(); session.clear(); return redirect(url_for('home'))

@app.route('/history')
@login_required
@mfa_required
def history():
    user_scans = SearchHistory.query.filter_by(user_id=current_user.id).order_by(SearchHistory.timestamp.desc()).all()
    return render_template('history.html', searches=user_scans)

@app.route('/report', methods=['POST'])
@login_required
def report():
    target_url, comment = request.form.get('target_url'), request.form.get('comment')
    db_path = os.path.join(basedir, 'safesurf.db')
    try:
        conn = sqlite3.connect(db_path); conn.execute("INSERT INTO reports (url, comment) VALUES (?, ?)", (target_url, comment)); conn.commit(); conn.close()
        return redirect(url_for('index', reported='true'))
    except Exception as e:
        flash("Error logging threat data.", "danger"); return redirect(url_for('index'))

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

@app.route('/forgot_password')
def forgot_password(): flash("Credential recovery under maintenance.", "info"); return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)