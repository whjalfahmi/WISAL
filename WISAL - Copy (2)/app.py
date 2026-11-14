from flask import Flask, render_template, request, redirect, url_for, session
from models import db, User, HEP, ExerciseRecord
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import inspect, text
from datetime import datetime, timedelta

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wisal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "wisal-secret-key"

db.init_app(app)

with app.app_context():
    db.create_all()

    columns = [
        column["name"]
        for column in inspect(db.engine).get_columns("user")
    ]

    if "therapist_id" not in columns:
        with db.engine.begin() as connection:
            connection.execute(text(
                "ALTER TABLE user ADD COLUMN therapist_id INTEGER REFERENCES user(id)"
            ))

    omar = User.query.filter_by(email="omar@test.com").first()

    if not omar:
        omar = User(
            name="Omar",
            email="omar@test.com",
            password=generate_password_hash("Omar12345"),
            role="Patient"
        )
        db.session.add(omar)
    else:
        omar.password = generate_password_hash("Omar12345")
        omar.role = "Patient"

    leen = User.query.filter_by(email="leen@test.com").first()

    if not leen:
        leen = User(
            name="Leen",
            email="leen@test.com",
            password=generate_password_hash("Leen12345"),
            role="Physical Therapist"
        )
        db.session.add(leen)
    else:
        leen.password = generate_password_hash("Leen12345")
        leen.role = "Physical Therapist"
        
    db.session.flush()
    omar.therapist_id = leen.id
    db.session.commit()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session["user_id"] = user.id
            session["user_role"] = user.role
            session["user_name"] = user.name

            if user.role == "Patient":
                return redirect(url_for("patient_dashboard"))

            elif user.role == "Physical Therapist":
                return redirect(url_for("therapist_dashboard"))

        return render_template("login.html", error="Invalid email or password")

    return render_template("login.html")


@app.route("/patient")
def patient_dashboard():
    
        if "user_id" not in session:
            return redirect(url_for("login"))
    
        if session["user_role"] != "Patient":

            return redirect(url_for("login"))

        return render_template("patient.html")


@app.route("/therapist")
def therapist_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["user_role"] != "Physical Therapist":
        return redirect(url_for("login"))

    patients = User.query.filter_by(
        role="Patient",
        therapist_id=session["user_id"]
    ).all()

    return render_template(
        "therapist.html",
        patients=patients
    )


@app.route("/therapist/patient/<int:patient_id>")
def patient_details(patient_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["user_role"] != "Physical Therapist":
        return redirect(url_for("login"))

    patient = User.query.filter_by(
        id=patient_id,
        role="Patient",
        therapist_id=session["user_id"]
    ).first_or_404()

    heps = HEP.query.filter_by(
    patient_id=patient.id
).all()

    records = ExerciseRecord.query.filter_by(
    patient_id=patient.id
).order_by(
    ExerciseRecord.date.desc()
).all()
    
    weeks = request.args.get("weeks", type=int)
    recent_records = []
    completed_count = 0
    not_completed_count = 0
    no_record_count = 0
    reason_counts = {}
    difficulty_analysis = []


    if weeks is not None and 1 <= weeks <= 52:
        cutoff_date = datetime.utcnow() - timedelta(weeks=weeks)

        recent_records = ExerciseRecord.query.filter(
            ExerciseRecord.patient_id == patient.id,
            ExerciseRecord.date >= cutoff_date
        ).order_by(
            ExerciseRecord.date.desc()
        ).all()

        completed_count = sum(
            1 for record in recent_records
            if record.status == "Completed"
        )

        not_completed_count = sum(
            1 for record in recent_records
            if record.status == "Not Completed"
        )

        recorded_hep_ids = {
            record.hep_id for record in recent_records
        }

        no_record_count = sum(
            1 for hep in heps
            if hep.id not in recorded_hep_ids
        )

        from collections import Counter

        reason_counts = Counter(
            record.reason for record in recent_records
            if record.status == "Not Completed" and record.reason
        )


        for hep in heps:

            difficulty_records = [
                record for record in recent_records
                if record.hep_id == hep.id
                and record.difficulty is not None
                and 1 <= record.difficulty <= 5
            ]

            if difficulty_records:
                average_difficulty = sum(
                    record.difficulty for record in difficulty_records
                ) / len(difficulty_records)

                difficulty_analysis.append({
                    "exercise_name": hep.title,
                    "average": round(average_difficulty, 2),
                    "rating_count": len(difficulty_records)
                })




    return render_template(
        "patient_details.html",
        patient=patient,
        heps=heps,
        records=records,
        weeks=weeks,
        recent_records=recent_records,
        completed_count=completed_count,
        not_completed_count=not_completed_count,
        no_record_count=no_record_count,
        reason_counts=reason_counts,
        difficulty_analysis=difficulty_analysis
    )

@app.route("/therapist/patient/<int:patient_id>/assign-hep", methods=["GET", "POST"])
def assign_hep(patient_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["user_role"] != "Physical Therapist":
        return redirect(url_for("login"))

    patient = User.query.filter_by(
        id=patient_id,
        role="Patient",
        therapist_id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":

        new_hep = HEP(
            patient_id=patient.id,
            therapist_id=session["user_id"],
            title=request.form.get("title"),
            instructions=request.form.get("instructions"),
            sets=int(request.form.get("sets")),
            repetitions=int(request.form.get("repetitions")),
            duration=request.form.get("duration")
        )

        db.session.add(new_hep)
        db.session.commit()

        return redirect(url_for("patient_details", patient_id=patient.id))

    return redirect(url_for("patient_details", patient_id=patient.id))

@app.route("/therapist/hep/<int:hep_id>/update", methods=["POST"])
def update_hep(hep_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["user_role"] != "Physical Therapist":
        return redirect(url_for("login"))

    hep = HEP.query.filter_by(
        id=hep_id,
        therapist_id=session["user_id"]
    ).first_or_404()

    hep.title = request.form.get("title")
    hep.instructions = request.form.get("instructions")
    hep.sets = int(request.form.get("sets"))
    hep.repetitions = int(request.form.get("repetitions"))
    hep.frequency = request.form.get("frequency")

    db.session.commit()

    return redirect(url_for(
        "patient_details",
        patient_id=hep.patient_id
    ))

@app.route("/logout")
def logout():
        session.clear()
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)