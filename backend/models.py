from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(50), nullable=False)  # Added phone
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Resume(db.Model):
    __tablename__ = "resumes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    role_title = db.Column(db.String(255), nullable=False)  # e.g. "Generative AI Intern"
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50), nullable=False)  # Added phone
    location = db.Column(db.String(255), nullable=True)
    is_fresher = db.Column(db.Boolean, default=True)
    years_experience = db.Column(db.Float, default=0.0)
    summary = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)  # technical skills
    soft_skills = db.Column(db.Text, nullable=True)
    education = db.Column(db.Text, nullable=True)
    projects = db.Column(db.Text, nullable=True)
    experience = db.Column(db.Text, nullable=True)
    certificates = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(512), nullable=True)
    template_type = db.Column(db.String(50), nullable=False)
    pdf_path = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship("User", backref="resumes")