from flask import Flask, render_template, request, flash, redirect, send_file, session, url_for
import os
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

from models import init_db, add_enquiry, get_all_enquiries, create_admin, verify_admin
from utils import export_to_excel, import_from_excel, export_to_gsheets, import_from_gsheets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'super_secret_key_for_vs_interior')

# Initialize DB on startup
init_db()

# Dummy Projects Data for the website
projects_db = [
    {
        "id": "1",
        "name": "Siddhatech Software",
        "category": "Commercial",
        "type": "Commercial Office",
        "location": "Pune, India",
        "concept": "Optimized workspace featuring an open-plan design with formal conference rooms.",
        "description": "A state-of-the-art office designed for productivity and modern aesthetics. It features ergonomic furniture, dynamic lighting, and collaborative open spaces.",
        "images": ["https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&q=80&w=1200", "https://images.unsplash.com/photo-1524758631624-e2822e304c36?auto=format&fit=crop&q=80&w=1200", "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&q=80&w=1200"]
    },
    {
        "id": "2",
        "name": "'Gaurav' Bungalow",
        "category": "Residential",
        "type": "Premium Residential",
        "location": "Pune City",
        "concept": "A seamless blend of classic comfort and modern aesthetics.",
        "description": "This luxurious bungalow features striking architecture with classic tiled roofing and extensive terrace spaces, creating a lavish residential experience.",
        "images": [
            "/static/images/projects/gaurav/media__1775029955580.jpg",
            "/static/images/projects/gaurav/media__1775029955654.jpg",
            "/static/images/projects/gaurav/media__1775029955717.jpg",
            "/static/images/projects/gaurav/media__1775029955839.jpg",
            "/static/images/projects/gaurav/media__1775029955904.jpg",
            "/static/images/projects/gaurav/media__1775029994345.jpg",
            "/static/images/projects/gaurav/media__1775029994525.jpg",
            "/static/images/projects/gaurav/media__1775029994540.jpg",
            "/static/images/projects/gaurav/media__1775030002273.jpg"
        ]
    },
    {
        "id": "3",
        "name": "WB Sales",
        "category": "Commercial",
        "type": "Commercial Office",
        "location": "Viman Nagar, Pune",
        "concept": "Sleek, brand-forward workspace with dynamic zones.",
        "description": "A modern commercial interior for WB Sales at Viman Nagar, featuring professional workstations, vibrant branding elements, and ergonomic spaces designed for performance.",
        "images": [
            "/static/images/projects/wb_sales/wb_sales_1.jpg",
            "/static/images/projects/wb_sales/wb_sales_2.jpg",
            "/static/images/projects/wb_sales/wb_sales_3.jpg",
            "/static/images/projects/wb_sales/wb_sales_4.jpg",
            "/static/images/projects/wb_sales/wb_sales_5.jpg"
        ]
    },
    {
        "id": "4",
        "name": "Amanora Lake House",
        "category": "Commercial",
        "type": "Hospitality & Leisure",
        "location": "Amanora, Pune",
        "concept": "Nature-inspired luxury lakeside interiors.",
        "description": "A premium hospitality project blending natural textures with contemporary design, offering guests a serene lakeside experience through curated materials and open layouts.",
        "images": ["https://images.unsplash.com/photo-1571896349842-33c89424de2d?auto=format&fit=crop&q=80&w=1200"]
    },
    {
        "id": "5",
        "name": "MCA Pune",
        "category": "Commercial",
        "type": "Institutional",
        "location": "Pune",
        "concept": "Professional institutional interiors with functional precision.",
        "description": "An institutional commercial project for MCA Pune, delivering a disciplined, professional interior design with focused spatial planning and premium finishes.",
        "images": ["https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&q=80&w=1200"]
    },
    {
        "id": "6",
        "name": "Fluent India",
        "category": "Commercial",
        "type": "Corporate Office",
        "location": "Pune",
        "concept": "Fluid, open-plan corporate design built for collaboration.",
        "description": "A vibrant corporate office interior for Fluent India, designed around collaboration-first principles with open zones, breakout areas, and a contemporary aesthetic.",
        "images": [
            "/static/images/projects/fluent_india/fluent_1.jpg",
            "/static/images/projects/fluent_india/fluent_2.jpg",
            "/static/images/projects/fluent_india/fluent_3.jpg",
            "/static/images/projects/fluent_india/fluent_4.jpg"
        ]
    },
    {
        "id": "7",
        "name": "Sweet Water Villa",
        "category": "Residential",
        "type": "Premium Villa",
        "location": "Pune",
        "concept": "Luxury villa living with calm, earthy elegance.",
        "description": "A stunning residential villa interior featuring warm natural palettes, bespoke joinery, expansive living areas, and a seamless flow between indoor and outdoor spaces.",
        "images": [
            "/static/images/projects/sweet_water_villa/villa_1.jpg",
            "/static/images/projects/sweet_water_villa/villa_2.jpg",
            "/static/images/projects/sweet_water_villa/villa_3.jpg",
            "/static/images/projects/sweet_water_villa/villa_4.jpg",
            "/static/images/projects/sweet_water_villa/villa_5.jpg"
        ]
    }
]


# --- Public Endpoints ---

@app.route('/')
def index():
    return render_template('index.html', projects=projects_db)

@app.route('/project/<project_id>')
def project_detail(project_id):
    project = next((p for p in projects_db if p["id"] == project_id), None)
    if not project:
        return "Project not found", 404
    return render_template('project.html', project=project)

@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    project_details = request.form.get('details')
    start_date = request.form.get('start_date')
    hear_about = request.form.get('hear_about')
    
    if add_enquiry(name, email, phone, project_details, start_date, hear_about):
        flash("Thank you for your enquiry! We will get in touch shortly.", "success")
    else:
        flash("There was an issue submitting your enquiry. Please try again.", "error")
        
    return redirect('/#enquiry')


# --- Admin Authentication & Middleware ---

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# Pre-defined admin credentials
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "password123")

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Hardcoded credentials check
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_id'] = 1 # give a dummy id
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('admin_login'))


# --- Admin Dashboard & Tools ---

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    enquiries = get_all_enquiries()
    return render_template('admin_dashboard.html', enquiries=enquiries)

@app.route('/admin/export/excel')
@admin_required
def export_excel():
    enquiries = get_all_enquiries()
    output = export_to_excel(enquiries)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=f"VS_Enquiries_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/admin/export/gsheets', methods=['POST'])
@admin_required
def export_gsheets():
    sheet_url = request.form.get('sheet_url')
    enquiries = get_all_enquiries()
    
    success, message = export_to_gsheets(enquiries, sheet_url)
    if success:
        flash(message, 'success')
    else:
        flash(f"Error: {message}", 'error')
        
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/import/excel', methods=['POST'])
@admin_required
def import_excel():
    if 'file' not in request.files:
        flash('No file part', 'error')
        return redirect(url_for('admin_dashboard'))
        
    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(url_for('admin_dashboard'))
        
    if file:
        success, message = import_from_excel(file.stream)
        if success:
            flash(message, 'success')
        else:
            flash(f"Error: {message}", 'error')
            
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/import/gsheets', methods=['POST'])
@admin_required
def import_gsheets():
    sheet_url = request.form.get('sheet_url')
    
    success, message = import_from_gsheets(sheet_url)
    if success:
        flash(message, 'success')
    else:
        flash(f"Error: {message}", 'error')
        
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    # Initialize DB (in production run via a separate script)
    init_db()
    is_debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ['true', '1', 't']
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=is_debug)
