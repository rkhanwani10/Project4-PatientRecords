from models import Base, Department, Patient
from flask import Flask, render_template, redirect, jsonify, request, url_for, abort, g
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine, desc
from datetime import datetime

engine = create_engine('sqlite:///patientRecords.db')

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

@app.route('/')
def showDepartments():
    departments = session.query(Department).order_by(Department.department_name).all()
    recently_admitted = session.query(Patient).order_by(desc(Patient.date_of_admission)).all()
    return render_template('home.html', departments=departments,
        patients=recently_admitted)

@app.route('/catalog/<department>/items')
def showPatients(department):
    departments = session.query(Department).order_by(Department.department_name).all()
    joined = session.query(Patient).join(Patient.department)
    patients = joined.filter_by(department_name=department).all()
    return render_template('home.html', departments=departments,
        patients=patients)

@app.route('/catalog/patient/new', methods=['GET','POST'])
def newPatient():
    if request.method == 'POST':
        department_name = request.form['department_name']
        department = session.query(Department).filter_by(department_name=department_name).one()
        date_of_admission = request.form['date_of_admission']
        dt = datetime.strptime(date_of_admission, "%Y-%m-%d")
        newPatient = Patient(name=request.form['name'], age=int(request.form['age']),
            notes=request.form['notes'], date_of_admission=dt, department_id=department.id)
        session.add(newPatient)
        session.commit()
        return redirect(url_for('showPatients', department=department_name))
    else:
        return render_template('newPatient.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
