from flask import Flask, render_template, request, redirect
from models import db, Task

app = Flask(__name__)

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasks.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# Create tables
with app.app_context():
    db.create_all()

# Home
@app.route("/")
def index():
    tasks = Task.query.all()
    return render_template("index.html", tasks=tasks)

# Add Task
@app.route("/add", methods=["POST"])
def add_task():
    name = request.form.get("task")
    priority = request.form.get("priority", "Medium")
    due_date = request.form.get("due_date", "")
    if name:
        task = Task(name=name, priority=priority, due_date=due_date)
        db.session.add(task)
        db.session.commit()
    return redirect("/")

# Delete Task
@app.route("/delete/<int:id>")
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect("/")

# Toggle Status
@app.route("/toggle/<int:id>")
def toggle_task(id):
    task = Task.query.get_or_404(id)
    if task.status == "Todo":
        task.status = "In Progress"
    elif task.status == "In Progress":
        task.status = "Done"
    else:
        task.status = "Todo"
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)