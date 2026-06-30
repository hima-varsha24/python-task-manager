from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ai_service import suggest_tasks
from models import db, User, Task

app = Flask(__name__)
app.config["SECRET_KEY"] = "taskflow-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# Home
@app.route("/")
@login_required
def index():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template("index.html", tasks=tasks)

# Add Task
@app.route("/add", methods=["POST"])
@login_required
def add_task():
    name = request.form.get("task")
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "")
    description = request.form.get("description", "")
    if name:
        task = Task(name=name, description=description, priority=priority, due_date=due_date, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
    return redirect("/")

# AI Suggestions
@app.route("/ai/suggest", methods=["POST"])
@login_required
def ai_suggest():
    goal = request.form.get("goal", "").strip()
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    if not goal:
        flash("Tell AI what you want to plan first.")
        return render_template("index.html", tasks=tasks)

    existing_tasks = [
        {
            "name": task.name,
            "priority": task.priority,
            "due_date": task.due_date,
            "status": task.status,
        }
        for task in tasks
    ]

    ai_error = None
    try:
        suggestions = suggest_tasks(goal, existing_tasks)
    except Exception as error:
        ai_error = str(error)
        flash(ai_error)
        suggestions = []

    if goal and not suggestions and not ai_error:
        flash("AI could not create suggestions right now. Try a more specific goal.")

    return render_template("index.html", tasks=tasks, ai_goal=goal, ai_suggestions=suggestions)

# Toggle
@app.route("/toggle/<int:id>")
@login_required
def toggle_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        return redirect("/")
    if task.status == "Todo":
        task.status = "In Progress"
    elif task.status == "In Progress":
        task.status = "Done"
    else:
        task.status = "Todo"
    db.session.commit()
    return redirect("/")

# Delete
@app.route("/delete/<int:id>")
@login_required
def delete_task(id):
    task = Task.query.get_or_404(id)
    if task.user_id != current_user.id:
        return redirect("/")
    db.session.delete(task)
    db.session.commit()
    return redirect("/")

# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!")
            return redirect("/register")
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect("/")
    return render_template("register.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/")
        flash("Invalid email or password!")
        return redirect("/login")
    return render_template("login.html")

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)
