from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Todo
from .import db

my_view = Blueprint("my_view", __name__)

@my_view.route("/")
def home():
    todos = Todo.query.all()
    message = request.args.get('message', None)
    message_type = request.args.get('message_type', 'info')  
    return render_template("./index.html", todos=todos, message=message, message_type=message_type)

@my_view.route("/add", methods=["POST"])
def add():
    task = request.form.get("task")
    if not task.strip():
        return redirect(url_for("my_view.home", message="Task cannot be empty.", message_type="error"))
    
    # Verificar se a tarefa já existe no banco de dados
    existing_todo = Todo.query.filter_by(task=task.strip()).first()
    if existing_todo:
        return redirect(url_for("my_view.home", message="Task already exists.", message_type="error"))
    
    new_todo = Todo(task=task.strip())
    message = "Something went wrong."  
    message_type = "error"
    try:
        db.session.add(new_todo)
        db.session.commit()
        message = "Task added successfully!"
        message_type = "success"
    except Exception as e:
        db.session.rollback()
        message = f"Error adding task: {str(e)}"
    
    return redirect(url_for("my_view.home", message=message, message_type=message_type))


@my_view.route("/update/<int:todo_id>", methods=["POST"])
def update(todo_id):
    todo = Todo.query.filter_by(id=todo_id).first()
    if not todo:
        return redirect(url_for("my_view.home", message="Task not found.", message_type="error"))
    
    message = "Something went wrong."  
    message_type = "error"
    try:
        todo.complete = not todo.complete
        db.session.commit()
        status = "completed" if todo.complete else "incomplete"
        message = f"Task marked as {status}."
        message_type = "success"
    except Exception as e:
        db.session.rollback()
        message = f"Error updating task: {str(e)}"
    
    return redirect(url_for("my_view.home", message=message, message_type=message_type))


@my_view.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        message = "Task not found."
        return redirect(url_for("my_view.home", message=message, message_type="error"))
    
    try:
        db.session.delete(todo)
        db.session.commit()
        message = "Task deleted successfully!"
        message_type = "success"
    except Exception as e:
        db.session.rollback()
        message = f"Error deleting task: {str(e)}"
        message_type = "error"
    
    return redirect(url_for("my_view.home", message=message, message_type=message_type))

@my_view.route("/edit/<int:todo_id>", methods=["POST"])
def edit(todo_id):
    new_task = request.form.get("new_task")
    if not new_task.strip():
        message = "Task cannot be empty."
        return redirect(url_for("my_view.home", message=message, message_type="error"))
    
    todo = Todo.query.filter_by(id=todo_id).first()
    if not todo:
        message = "Task not found."
        return redirect(url_for("my_view.home", message=message, message_type="error"))
    
    todo.task = new_task
    try:
        db.session.commit()
        message = "Task updated successfully!"
        message_type = "success"
    except Exception as e:
        db.session.rollback()
        message = f"Error updating task: {str(e)}"
        message_type = "error"
    
    return redirect(url_for("my_view.home", message=message, message_type=message_type))
