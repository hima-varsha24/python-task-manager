tasks = []

# ---------------- Functions ---------------- #

def add_task():
    name = input("Enter task: ").strip()
    tasks.append({"name": name, "done": False})
    print(f"✅ Task added: {name}")

def view_tasks():
    if not tasks:
        print("\n📝 No tasks yet!")
    else:
        print("\n📝 Your Tasks:")
        for i, task in enumerate(tasks, start=1):
            status = "✅" if task.get("done", False) else "❌"
            print(f"{i}. {task['name']} [{status}]")

def toggle_task():
    view_tasks()
    if not tasks:
        return
    index = int(input("Enter task number to toggle: ")) - 1
    if 0 <= index < len(tasks):
        tasks[index]["done"] = not tasks[index]["done"]
        print(f"🔄 Task toggled: {tasks[index]['name']}")
    else:
        print("❌ Invalid task number.")

def edit_task():
    view_tasks()
    if not tasks:
        return
    index = int(input("Enter task number to edit: ")) - 1
    if 0 <= index < len(tasks):
        new_name = input("Ent_

