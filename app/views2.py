encoding ='utf-8'
from flask import render_template, request, redirect, flash, url_for, make_response, session
from app.models2 import Category, Todo, ScoreWeight, db, Student
from app import app
import pandas as pd
import io
from urllib.parse import quote

import json
from app.scripts import forms
from app.scripts import helpers


# db.create_all()


@app.route('/', methods=['GET', 'POST'])
def login():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if form.validate():
                if helpers.credentials_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Login successful'})
                return json.dumps({'status': 'Invalid user/pass'})
            return json.dumps({'status': 'Both fields required'})
        return render_template('login.html', form=form)
    # user = helpers.get_user()
    # return render_template('home.html', user=user)
    # db.create_all()
    return redirect(url_for('list_all'))
    # return render_template('home.html', categories=Category.query.all(),
    #     students=Student.query.all(),
    #     scoreweights=ScoreWeight.query.all(),
    #     todos=Todo.query.all())


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


# -------- Signup ---------------------------------------------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = helpers.hash_password(request.form['password'])
            email = request.form['email']
            if form.validate():
                if not helpers.username_taken(username):
                    helpers.add_user(username, password, email)
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Signup successful'})
                return json.dumps({'status': 'Username taken'})
            return json.dumps({'status': 'User/Pass required'})
        return render_template('login.html', form=form)
    return redirect(url_for('login'))


# -------- Settings ---------------------------------------------------------- #
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            email = request.form['email']
            helpers.change_user(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))


################################3####################################
@app.route('/list_all')
def list_all():
    db.create_all()
    return render_template(
        'list2.html',
        categories=Category.query.all(),
        students=Student.query.all(),
        scoreweights=ScoreWeight.query.all(),
        todos=Todo.query.all(),    #join(Priority).order_by(Priority.value.desc())
    )


@app.route('/student_single/<name_student>')
def student_single(name_student):
    student_test = Student.query.filter_by(name=name_student).first()
    todos_student = Todo.query.filter_by(student=student_test).all()
    scores = {}
    categories = Category.query.all()
    score_all = 0
    for category in categories:
        score = 0
        todos = Todo.query.filter_by(student=student_test, category=category)
        for todo in todos:
            score += todo.scoreweight.value
            score_all += todo.scoreweight.value
        scores[category.name] = score
    scores["All"] = score_all
    return render_template(
        'student-single.html',
        todos=todos_student,
        categories=Category.query.all(),
        student=student_test,
        scoreweights=ScoreWeight.query.all(),
        scores=scores
    )


@app.route('/student_single/<name_student>/<category_in>')
def student_single_category(name_student, category_in):
    student_test = Student.query.filter_by(name=name_student).first()
    category_test = Category.query.filter_by(name=category_in).first()
    todos_student_category = Todo.query.filter_by(student=student_test, category=category_test).all()
    scores = {}
    categories = Category.query.all()
    score_all = 0
    for category in categories:
        score = 0
        todos = Todo.query.filter_by(student=student_test, category=category)
        for todo in todos:
            score += todo.scoreweight.value
            score_all += todo.scoreweight.value
        scores[category.name] = score
    scores["All"] = score_all
    return render_template(
        'student-single.html',
        todos=todos_student_category,
        categories=Category.query.all(),
        student=student_test,
        scoreweights=ScoreWeight.query.all(),
        scores=scores
    )


@app.route('/student_single/<name_student>/')
def student_download(name_student):
    student_test = Student.query.filter_by(name=name_student).first()
    dict_w = {}
    categories = Category.query.all()
    score_all = 0
    length_max = 0
    dict_w["姓名"] = [name_student]
    for category in categories:
        score = 0
        content = []
        todos = Todo.query.filter_by(student=student_test, category=category)
        for todo in todos:
            content += [todo.description]
            score += todo.scoreweight.value
            score_all += todo.scoreweight.value
        dict_w[category.name] = content
        dict_w["score_"+category.name] = [score]
        length_max = max(length_max, len(content))
    dict_w["ScoreAll"] = [score_all]

    for key0 in dict_w.keys():
        length0 = len(dict_w[key0])
        if length0 < length_max:
            dict_w[key0] += [""] * (length_max - length0)

    df = pd.DataFrame(dict_w)
    out = io.BytesIO()
    writer = pd.ExcelWriter(out, engine="xlsxwriter")
    df.to_excel(excel_writer=writer, index=False, sheet_name="{}".format(name_student))
    writer.save()
    writer.close()
    response = make_response(out.getvalue())
    basename = "{}.xlsx".format(name_student)
    response.headers["Content-Disposition"] = \
        "attachment;" \
        "filename*=UTF-8''{utf_filename}".format(
            utf_filename=quote(basename.encode('utf-8'))
        )
    return response

@app.route('/<name>')
def list_todos(name):
    category = Category.query.filter_by(name=name).first()
    todos = Todo.query.filter_by(category=category).all()
    return render_template(
        'list2.html',
        todos=todos,
        categories=Category.query.all(),
        students=Student.query.all(),
        scoreweights=ScoreWeight.query.all(),
    )


@app.route('/new-task', methods=['GET', 'POST'])
def new():
    if request.method == 'POST':  # 发给服务器
        student = Student.query.filter_by(id=request.form['student']).first()
        category = Category.query.filter_by(id=request.form['category']).first()
        scoreweight = ScoreWeight.query.filter_by(id=request.form['scoreweight']).first()
        #todo = Todo(category=category, priority=priority, description=request.form['description'])
        todo = Todo(
            student=student, category=category, scoreweight=scoreweight, description=request.form['description']
        )
        db.session.add(todo)
        db.session.commit()
        return redirect(url_for('list_all'))
    else:
        return render_template(
            'new-task2.html',
            page='new-task',
            students=Student.query.all(),
            categories=Category.query.all(),
            scoreweights=ScoreWeight.query.all(),
        )


@app.route('/<int:todo_id>', methods=['GET', 'POST'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if request.method == 'GET':
        return render_template(
            'new-task2.html',
            todo=todo,
            categories=Category.query.all(),
            students=Student.query.all(),
            scoreweights=ScoreWeight.query.all()
        )
    else:
        category = Category.query.filter_by(id=request.form['category']).first()
        student = Student.query.filter_by(id=request.form['student']).first()
        description = request.form['description']
        scoreweight = ScoreWeight.query.filter_by(id=request.form["scoreweight"]).first()
        todo.category = category
        todo.student = student
        todo.scoreweight = scoreweight
        todo.description = description
        db.session.commit()
        return redirect('/')


@app.route('/new-category', methods=['GET', 'POST'])
def new_category():
    if request.method == 'POST':
        category = Category(name=request.form['category'])
        db.session.add(category)
        db.session.commit()
        return redirect('/')
    else:
        return render_template(
            'new-category.html',
            page='new-category.html')


@app.route('/new-student', methods=['GET', 'POST'])
def new_student():
    if request.method == 'POST':
        student = Student(name=request.form['student'])
        db.session.add(student)
        db.session.commit()
        return redirect('/')
    else:
        return render_template(
            'new-student.html',
            page='new-student.html')


@app.route('/new-scoreweight', methods=['GET', 'POST'])
def new_scoreweight():
    if request.method == 'POST':
        scoreweight = ScoreWeight(value=request.form['scoreweight'])
        db.session.add(scoreweight)
        db.session.commit()
        return redirect('/')
    else:
        return render_template(
            'new-scoreweight.html',
            page='new-scoreweight.html')


@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
def edit_category(category_id):
    category = Category.query.get(category_id)
    if request.method == 'GET':
        return render_template(
            'new-category.html',
            category=category
        )
    else:
        category_name = request.form['category']
        category.name = category_name
        db.session.commit()
        return redirect('/')


@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    student = Student.query.get(student_id)
    if request.method == 'GET':
        return render_template(
            'new-student.html',
            student=student
        )
    else:
        student_name = request.form['student']
        student.name = student_name
        db.session.commit()
        return redirect('/')


@app.route('/delete-category/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    if request.method == 'POST':
        category = Category.query.get(category_id)

        flash('You have deleted this category for all students.')
        db.session.delete(category)
        db.session.commit()
        return redirect('/')


@app.route('/delete-student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    if request.method == 'POST':
        student = Student.query.get(student_id)
        flash('You have deleted all the dataset about {}'.format(student.name))
        db.session.delete(student)
        db.session.commit()
        return redirect('/')


@app.route('/delete-todo/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    if request.method == 'POST':
        todo = Todo.query.get(todo_id)
        db.session.delete(todo)
        db.session.commit()
        return redirect('/')
