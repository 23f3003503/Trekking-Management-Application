from flask import Flask, redirect, render_template, request, session 
from models import db, User, Trek, StaffProfile, Booking

app = Flask(__name__)
app.secret_key = "mad1_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trek.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(username="admin").first()

    if admin is None:

        admin = User(
            name="Administrator",
            username="admin",
            password="admin123",
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return "Username already exists. Please choose another username."
        
        new_user = User(
            name=name,
            username=username,
            password=password,
            role="trekker"
        )

        

        db.session.add(new_user)
        db.session.commit()

        return "Registration Successful!"
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        user=User.query.filter_by(username=username).first()
        if user is None:
            return "Username not found. Please register first."

        if user.password != password:
            return "Incorrect password."

        if not user.is_active:
            return "Your account has been deactivated."

        session["user_id"] = user.id
        session["role"] = user.role
        session["username"] = user.username

        if user.role == "admin":
            return redirect("/admin")

        elif user.role == "staff":
            return redirect("/staff")

        else:
            return redirect("/trekker")

    return render_template("login.html")

@app.route("/admin")
def admin():

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    total_treks = Trek.query.count()

    total_users = User.query.filter_by(role="trekker").count()

    total_staff = User.query.filter_by(role="staff").count()

    total_bookings = Booking.query.count()

    return render_template(
        "admin.html",
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings
    )

@app.route("/staff")
def staff():

    if "user_id" not in session or session["role"] != "staff":
        return redirect("/login")

    assigned_treks = Trek.query.filter_by(
        assigned_staff=session["user_id"]
    ).all()

    return render_template(
        "staff.html",
        assigned_treks=assigned_treks
    )

@app.route("/staff_edit_trek/<int:trek_id>", methods=["GET", "POST"])
def staff_edit_trek(trek_id):

    if "user_id" not in session or session["role"] != "staff":
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff != session["user_id"]:
        return "Unauthorized Access"

    if request.method == "POST":

        trek.available_slots = request.form["available_slots"]
        trek.status = request.form["status"]

        db.session.commit()

        return redirect("/staff")

    return render_template(
        "staff_edit_trek.html",
        trek=trek
    )

@app.route("/staff_participants/<int:trek_id>")
def staff_participants(trek_id):

    if "user_id" not in session or session["role"] != "staff":
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff != session["user_id"]:
        return "Unauthorized Access"

    bookings = Booking.query.filter_by(
        trek_id=trek.id
    ).all()

    return render_template(
        "staff_participants.html",
        trek=trek,
        bookings=bookings
    )

@app.route("/update_booking_status/<int:booking_id>/<status>")
def update_booking_status(booking_id, status):

    if "user_id" not in session or session["role"] != "staff":
        return redirect("/login")

    booking = Booking.query.get_or_404(booking_id)

    trek = Trek.query.get(booking.trek_id)

    if trek.assigned_staff != session["user_id"]:
        return "Unauthorized Access"

    booking.booking_status = status

    db.session.commit()

    return redirect(f"/staff_participants/{trek.id}")

@app.route("/trekker")
def trekker():

    if "user_id" not in session or session["role"] != "trekker":
        return redirect("/login")

    return render_template("trekker.html")

@app.route("/add_trek", methods=["GET", "POST"])
def add_trek():

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    if request.method == "POST":

        trek_name = request.form["trek_name"]
        location = request.form["location"]
        difficulty = request.form["difficulty"]
        duration = request.form["duration"]
        available_slots = request.form["available_slots"]
        description = request.form["description"]

        new_trek = Trek(
            trek_name=trek_name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=available_slots,
            description=description
        )

        db.session.add(new_trek)
        db.session.commit()

        return redirect("/view_treks")

    return render_template("add_trek.html")


@app.route("/view_treks")
def view_treks():

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    search = request.args.get("search")

    if search:
        treks = Trek.query.filter(
            Trek.trek_name.ilike(f"%{search}%")
        ).all()
    else:
        treks = Trek.query.all()

    return render_template(
        "view_treks.html",
        treks=treks
    )

@app.route("/treks")
def treks():

    if "user_id" not in session or session["role"] != "trekker":
        return redirect("/login")

    treks = Trek.query.all()

    return render_template(
        "trekker_treks.html",
        treks=treks
    )

@app.route("/book_trek/<int:id>")
def book_trek(id):

    if "user_id" not in session or session["role"] != "trekker":
        return redirect("/login")

    trek = Trek.query.get_or_404(id)

    if trek.available_slots <= 0:
        return "No slots available for this trek."

    existing_booking = Booking.query.filter_by(
        user_id=session["user_id"],
        trek_id=trek.id
    ).first()

    if existing_booking:
        return "You have already booked this trek."

    booking = Booking(
        user_id=session["user_id"],
        trek_id=trek.id,
        booking_status="Booked"
    )

    db.session.add(booking)

    trek.available_slots -= 1

    if trek.available_slots == 0:
        trek.status = "Closed"

    db.session.commit()

    return "Trek Booked Successfully!"

@app.route("/my_bookings")
def my_bookings():

    if "user_id" not in session or session["role"] != "trekker":
        return redirect("/login")

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]
    ).all()

    return render_template(
        "my_bookings.html",
        bookings=bookings
    )

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "user_id" not in session or session["role"] != "trekker":
        return redirect("/login")

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        username = request.form["username"]

        existing_user = User.query.filter(
            User.username == username,
            User.id != user.id
        ).first()

        if existing_user:
            return "Username already exists."

        user.name = request.form["name"]
        user.username = username
        user.password = request.form["password"]

        session["username"] = user.username

        db.session.commit()

        return redirect("/trekker")

    return render_template(
        "edit_profile.html",
        user=user
    )


@app.route("/view_bookings")
def view_bookings():

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    bookings = Booking.query.all()

    return render_template(
        "view_bookings.html",
        bookings=bookings
    )

@app.route("/edit_trek/<int:id>", methods=["GET", "POST"])
def edit_trek(id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    trek = Trek.query.get_or_404(id)
    staff_members = User.query.filter_by(role="staff").all()

    if request.method == "POST":

        trek.trek_name = request.form["trek_name"]
        trek.location = request.form["location"]
        trek.difficulty = request.form["difficulty"]
        trek.duration = request.form["duration"]
        trek.available_slots = request.form["available_slots"]
        trek.description = request.form["description"]
        trek.assigned_staff = request.form["assigned_staff"]

        db.session.commit()

        return redirect("/view_treks")

    return render_template(
        "edit_trek.html",
        trek=trek,
        staff_members=staff_members
    )

@app.route("/delete_trek/<int:trek_id>")
def delete_trek(trek_id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)

    db.session.commit()

    return redirect("/view_treks")

@app.route("/add_staff", methods=["GET", "POST"])
def add_staff():

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    if request.method == "POST":

        name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        phone = request.form["phone"]
        experience = request.form["experience"]
        specialization = request.form["specialization"]

        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return "Username already exists."

        new_staff = User(
            name=name,
            username=username,
            password=password,
            role="staff"
        )

        db.session.add(new_staff)
        db.session.commit()

        staff_profile = StaffProfile(
            user_id=new_staff.id,
            phone=phone,
            experience=experience,
            specialization=specialization
        )

        db.session.add(staff_profile)
        db.session.commit()

        return redirect("/view_staff")

    return render_template("add_staff.html")

@app.route("/view_staff")
def view_staff():

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    search = request.args.get("search", "")

    staff_members = StaffProfile.query.join(User).filter(
        User.name.ilike(f"%{search}%")
    ).all()

    return render_template(
        "view_staff.html",
        staff_members=staff_members,
        search=search
    )

@app.route("/toggle_staff/<int:id>")
def toggle_staff(id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    staff = StaffProfile.query.get_or_404(id)

    staff.user.is_active = not staff.user.is_active

    db.session.commit()

    return redirect("/view_staff")

@app.route("/view_users")
def view_users():

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    search = request.args.get("search", "")

    users = User.query.filter(User.role == "trekker")

    if search:
        users = users.filter(User.name.ilike(f"%{search}%"))

    users = users.all()

    return render_template(
        "view_users.html",
        users=users,
        search=search
    )


@app.route("/toggle_user/<int:id>")
def toggle_user(id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    user = User.query.get_or_404(id)

    user.is_active = not user.is_active

    db.session.commit()

    return redirect("/view_users")


@app.route("/edit_staff/<int:id>", methods=["GET", "POST"])
def edit_staff(id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    staff = StaffProfile.query.get_or_404(id)

    if request.method == "POST":

        staff.user.name = request.form["name"]
        staff.user.username = request.form["username"]
        staff.user.password = request.form["password"]

        staff.phone = request.form["phone"]
        staff.experience = request.form["experience"]
        staff.specialization = request.form["specialization"]

        db.session.commit()

        return redirect("/view_staff")

    return render_template(
        "edit_staff.html",
        staff=staff
    )

@app.route("/delete_staff/<int:id>")
def delete_staff(id):

    if "user_id" not in session or session["role"] != "admin":
        return redirect("/login")

    staff = StaffProfile.query.get_or_404(id)

    user = User.query.get(staff.user_id)

    db.session.delete(staff)

    db.session.delete(user)

    db.session.commit()

    return redirect("/view_staff")


@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)