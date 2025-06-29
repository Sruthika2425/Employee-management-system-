from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret123'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# ---------------- Models ---------------- #
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    department = db.Column(db.String(150), nullable=False)


# ---------------- Authentication ---------------- #
@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Login attempt: {username} / {password}")
        user = Admin.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            print("Login successful")
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
            print("Login failed")
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------------- CRUD ---------------- #
@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    employees = Employee.query.all()
    return render_template('dashboard.html', employees=employees)


@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        new_emp = Employee(name=name, email=email, department=department)
        db.session.add(new_emp)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('employee_form.html', employee=None)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_employee(id):
    emp = Employee.query.get_or_404(id)
    if request.method == 'POST':
        emp.name = request.form['name']
        emp.email = request.form['email']
        emp.department = request.form['department']
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('employee_form.html', employee=emp)


@app.route('/delete/<int:id>')
@login_required
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    db.session.delete(emp)
    db.session.commit()
    return redirect(url_for('dashboard'))


# ---------------- Initial Setup ---------------- #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not Admin.query.first():
            db.session.add(Admin(username='admin', password='admin123'))
            db.session.commit()
    app.run(debug=True)
