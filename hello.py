import datetime
import json
import random

from flask import Flask, render_template, request, make_response, session, redirect, url_for

# инициализируем приложение
# из документации:
#     The flask object implements a WSGI application and acts as the central
#     object.  It is passed the name of the module or package of the
#     application.  Once it is created it will act as a central registry for
#     the view functions, the URL rules, template configuration and much more.
from db_util import Database

app = Flask(__name__)

# нужно добавить секретный код - только с ним можно менять данные сессии
app.secret_key = "111"

# необходимо добавлять, чтобы время сессии не ограничивалось закрытием браузера
app.permanent_session_lifetime = datetime.timedelta(days=365)

# инициализация класса с методами для работы с БД
db = Database()

# дальше реализуем методы, которые мы можем выполнить из браузера,
# благодаря указанным относительным путям


# метод для создания куки
@app.route("/add_cookie")
def add_cookie():
    resp = make_response("Add cookie")
    resp.set_cookie("test", "val")
    return resp


# метод для удаления куки
@app.route("/delete_cookie")
def delete_cookie():
    resp = make_response("Delete cookie")
    resp.set_cookie("test", "val", 0)


# реализация визитов
@app.route("/visits")
def visits():
    visits_count = session['visits'] if 'visits' in session.keys() else 0
    session['visits'] = visits_count + 1

    return f"Количество визитов: {session['visits']}"


# удаление данных о посещениях
@app.route("/delete_visits")
def delete_visits():
    session.pop('visits')
    return "ok"


# метод, который возвращает список фильмов по относительному адресу /films
@app.route("/films")
def films_list():
    # получаем GET-параметр country (Russia/USA/French
    country = request.args.get("country")
    rating = request.args.get("rating")

    if not rating:
        rating = 0
    if country:
        films = db.execute(f"select * from films where country='{country}' and rating>='{rating}'")
    else:
        films = db.execute(f"select * from films where rating>='{rating}'")

    # формируем контекст, который мы будем передавать для генерации шаблона
    context = {
        'films': films,
        'title': "FILMS",
        'country': country
    }

    # возвращаем сгенерированный шаблон с нужным нам контекстом
    return render_template("films.html", **context)


@app.route("/film/<int:film_id>")
def get_film(film_id):
    id_films = db.execute(f"select * from films")
    for ind in id_films:
        if ind['id'] == film_id:
            film = db.execute(f"select * from films where id='{film_id}'")
            return render_template("film.html", title=film['name'], film=film)

    return render_template("error.html", error="Такого фильма не существует в системе")


@app.route('/new_film', methods=['GET'])
def my_form():
    return render_template('new_film.html')
@app.route('/new_film', methods=['POST'])
def new_film():
    ids = db.execute(f'SELECT id FROM films')
    id = ids[-1]['id'] + 1
    name = request.form['name']
    rating = request.form.get('rating')
    country = request.form['country']
    db.insert(f"INSERT INTO films (id, name, rating, country) VALUES({id}, '{name}', {rating}, '{country}')")
    return render_template("new_film.html")


@app.route('/change_mode', methods=['GET', 'POST'])
def change_mode():
    if request.method == "POST":
        resp = make_response(redirect(url_for('films_list'), 302))
        userInput = request.form.get("userInput")
        if userInput == 'True':
            resp.set_cookie('theme', 'dark')
        else:
            resp.set_cookie('theme', 'light')
        return resp
    return render_template('theme.html')


@app.route('/get_random', methods=['GET'])
def get_random():
    ids = db.execute(f'SELECT id FROM films')
    id = ids[-1]['id']
    idit = random.randint(0, id)
    film = db.execute(f"select * from films where id = {idit}")
    print(film)
    return {'randint': [film['name'], film['rating'], film['country']]}


@app.route('/get_film', methods=['GET'])
def get_random_film():
    return render_template('random_film.html')


if __name__ == "__main__":
    app.run(debug=True)
