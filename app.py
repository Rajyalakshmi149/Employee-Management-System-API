
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)


# Employee Model
class Employee(db.Model):
    __tablename__ = "employee"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "department": self.department,
            "designation": self.designation
        }


# Home Route
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "Employee Management API is running"
    }), 200


# GET: All Employees
@app.route("/api/employees", methods=["GET"])
def get_employees():
    employees = Employee.query.all()

    return jsonify([
        employee.to_dict() for employee in employees
    ]), 200


# GET: Employee by ID
@app.route("/api/employees/<int:id>", methods=["GET"])
def get_employee(id):
    employee = db.session.get(Employee, id)

    if employee is None:
        return jsonify({
            "message": f"Employee with ID {id} not found"
        }), 404

    return jsonify(employee.to_dict()), 200


# POST: Create Employee
@app.route("/api/employees", methods=["POST"])
def create_employee():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    required_fields = [
        "name", "email", "department", "designation"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({
                "error": f"{field} is required"
            }), 400

    employee = Employee(
        name=data["name"],
        email=data["email"],
        department=data["department"],
        designation=data["designation"]
    )

    try:
        db.session.add(employee)
        db.session.commit()

        return jsonify({
            "message": "Employee created successfully",
            "employee": employee.to_dict()
        }), 201

    except Exception:
        db.session.rollback()

        return jsonify({
            "error": "Unable to create employee. Check the database schema and whether the email already exists."
        }), 400


# PUT: Update Employee
@app.route("/api/employees/<int:id>", methods=["PUT"])
def update_employee(id):
    employee = db.session.get(Employee, id)

    if employee is None:
        return jsonify({
            "message": f"Employee with ID {id} not found"
        }), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    allowed_fields = [
        "name", "email", "department", "designation"
    ]

    for field in allowed_fields:
        if field in data:
            setattr(employee, field, data[field])

    try:
        db.session.commit()

        return jsonify({
            "message": "Employee updated successfully",
            "employee": employee.to_dict()
        }), 200

    except Exception:
        db.session.rollback()

        return jsonify({
            "error": "Unable to update employee. Check the email and database constraints."
        }), 400


# DELETE: Employee by ID
@app.route("/api/employees/<int:id>", methods=["DELETE"])
def delete_employee(id):
    employee = db.session.get(Employee, id)

    if employee is None:
        return jsonify({
            "message": f"Employee with ID {id} not found"
        }), 404

    db.session.delete(employee)
    db.session.commit()

    return jsonify({
        "message": "Employee deleted successfully"
    }), 200


# Check registered routes
@app.route("/api/routes", methods=["GET"])
def list_routes():
    return jsonify([
        {
            "url": str(route),
            "methods": sorted(
                route.methods - {"HEAD", "OPTIONS"}
            )
        }
        for route in app.url_map.iter_rules()
    ]), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
