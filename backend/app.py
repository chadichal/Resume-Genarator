import os
import time
import random
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_file,
    abort,
    jsonify,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from .models import db, User, Resume
from .pdf_utils import generate_resume_pdf
from .modules import calculate_ats_score  # Import for potential use

def _migrate_resume_columns(app):
    try:
        from sqlalchemy import text
        with db.engine.connect() as conn:
            cur = conn.execute(text("PRAGMA table_info(resumes)"))
            cols = [r[1] for r in cur.fetchall()]
            for col in ("soft_skills", "certificates", "profile_image", "phone"):
                if col not in cols:
                    conn.execute(text(f"ALTER TABLE resumes ADD COLUMN {col} TEXT"))
                    conn.commit()
    except Exception:
        pass

def create_app():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
    )
    app.config["SECRET_KEY"] = "change_this_secret_key"
    db_path = os.path.abspath(os.path.join(base_dir, "resume_builder.db")).replace("\\", "/")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 4 * 1024 * 1024
    app.config["UPLOAD_FOLDER"] = os.path.join(base_dir, "uploads")
    db.init_app(app)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    with app.app_context():
        db.create_all()
        _migrate_resume_columns(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/send_email_otp", methods=["POST"])
    def send_email_otp():
        email = request.json.get("email")
        if not email:
            return jsonify({"error": "Email required"}), 400
        otp = str(random.randint(100000, 999999))
        session["email_otp"] = otp
        session["email"] = email
        print(f"OTP for {email}: {otp}")  # Simulate send; replace with smtplib
        return jsonify({"message": "OTP sent"})

    @app.route("/verify_email_otp", methods=["POST"])
    def verify_email_otp():
        user_otp = request.json.get("otp")
        if user_otp == session.get("email_otp"):
            return jsonify({"success": True})
        return jsonify({"error": "Invalid OTP"}), 400

    @app.route("/send_phone_otp", methods=["POST"])
    def send_phone_otp():
        phone = request.json.get("phone")
        if not phone:
            return jsonify({"error": "Phone required"}), 400
        otp = str(random.randint(100000, 999999))
        session["phone_otp"] = otp
        session["phone"] = phone
        print(f"OTP for {phone}: {otp}")  # Simulate SMS; replace with Twilio
        return jsonify({"message": "OTP sent"})

    @app.route("/verify_phone_otp", methods=["POST"])
    def verify_phone_otp():
        user_otp = request.json.get("otp")
        if user_otp == session.get("phone_otp"):
            return jsonify({"success": True})
        return jsonify({"error": "Invalid OTP"}), 400

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            phone = request.form.get("phone", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            email_otp = request.form.get("email_otp", "")
            phone_otp = request.form.get("phone_otp", "")

            if not all([full_name, email, phone, password, confirm_password]):
                return render_template("register.html", error="All fields are required.")
            if password != confirm_password:
                return render_template("register.html", error="Passwords do not match.")
            if email_otp != session.get("email_otp"):
                return render_template("register.html", error="Invalid email OTP.")
            if phone_otp != session.get("phone_otp"):
                return render_template("register.html", error="Invalid phone OTP.")

            existing = User.query.filter_by(email=email).first()
            if existing:
                return render_template("register.html", error="Email already registered.")

            user = User(
                email=email,
                phone=phone,
                full_name=full_name,
                password_hash=generate_password_hash(password),
            )
            db.session.add(user)
            db.session.commit()
            session["user_id"] = user.id
            session["user_name"] = user.full_name
            return redirect(url_for("resume_builder"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user = User.query.filter_by(email=email).first()
            if not user or not check_password_hash(user.password_hash, password):
                return render_template(
                    "login.html", error="Invalid email or password."
                )
            session["user_id"] = user.id
            session["user_name"] = user.full_name
            return redirect(url_for("resume_builder"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("index"))

    def require_login():
        user_id = session.get("user_id")
        if not user_id:
            abort(401)
        return user_id

    @app.route("/resume", methods=["GET", "POST"])
    def resume_builder():
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))
        if request.method == "POST":
            full_name = request.form.get("full_name", "").strip()
            role_title = request.form.get("role_title", "Generative AI Intern").strip()
            email = request.form.get("email", "").strip()
            phone = request.form.get("phone", "").strip()
            location = request.form.get("location", "").strip()
            level = request.form.get("resume_level", "fresher")
            years_experience_raw = request.form.get("years_experience", "0").strip()
            try:
                years_experience = float(years_experience_raw or "0")
            except ValueError:
                years_experience = 0.0
            is_fresher = level == "fresher"
            summary = request.form.get("summary", "")
            skills = request.form.get("skills", "")
            soft_skills = request.form.get("soft_skills", "")
            education = request.form.get("education", "")
            projects = request.form.get("projects", "")
            experience = request.form.get("experience", "")
            certificates = request.form.get("certificates", "")
            template_type = request.form.get("template_type", "auto")
            if template_type == "auto":
                template_type = "fresher_modern" if is_fresher else "experienced_modern"
            profile_image_path = None
            if "profile_image" in request.files:
                f = request.files["profile_image"]
                if f and f.filename and "." in f.filename:
                    ext = f.filename.rsplit(".", 1)[1].lower()
                    if ext in ("jpg", "jpeg", "png", "gif"):
                        fn = secure_filename(f"profile_{user_id}_{int(time.time() * 1000)}.{ext}")
                        save_path = os.path.join(app.config["UPLOAD_FOLDER"], fn)
                        f.save(save_path)
                        profile_image_path = fn
            resume = Resume(
                user_id=user_id,
                full_name=full_name or session.get("user_name", ""),
                role_title=role_title or "Generative AI Intern",
                email=email,
                phone=phone,
                location=location,
                is_fresher=is_fresher,
                years_experience=years_experience,
                summary=summary,
                skills=skills,
                soft_skills=soft_skills,
                education=education,
                projects=projects,
                experience=experience,
                certificates=certificates,
                profile_image=profile_image_path,
                template_type=template_type,
            )
            db.session.add(resume)
            db.session.commit()
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pdf_dir = os.path.join(base_dir, "generated_pdfs")
            relative_path = generate_resume_pdf(resume, pdf_dir, base_dir, template_type)
            resume.pdf_path = relative_path
            db.session.commit()
            return redirect(url_for("preview_resume", resume_id=resume.id))
        return render_template(
            "resume.html",
            default_role_title="Generative AI Intern",
            user_name=session.get("user_name", ""),
        )

    @app.route("/preview/<int:resume_id>")
    def preview_resume(resume_id):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume:
            abort(404)
        # Optional: Calculate ATS score
        ats_score, matched, total, breakdown = calculate_ats_score(resume.skills + " " + resume.summary, resume.role_title)
        return render_template("preview.html", resume=resume)

    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        if ".." in filename or "/" in filename or "\\" in filename:
            abort(404)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if not os.path.exists(path):
            abort(404)
        return send_file(path, as_attachment=False)

    @app.route("/download/<int:resume_id>")
    def download_resume(resume_id):
        user_id = require_login()
        resume = Resume.query.filter_by(id=resume_id, user_id=user_id).first()
        if not resume or not resume.pdf_path:
            abort(404)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pdf_path = os.path.join(base_dir, resume.pdf_path)
        if not os.path.exists(pdf_path):
            abort(404)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"{resume.full_name.replace(' ', '_')}_resume.pdf",
        )

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()