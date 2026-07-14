from flask import Flask, render_template, request
from models import db, User

app = Flask(__name__)
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

        if user.role == "admin":
            return render_template("admin.html")

        elif user.role == "staff":
            return render_template("staff.html")

        else:
            return render_template("trekker.html")

    return render_template("login.html")


if __name__ == "__main__":
    app.run(debug=True)