import datetime
import json

from flask import Flask, render_template, request, make_response, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# инициализируем приложение
# из документации:
#     The flask object implements a WSGI application and acts as the central
#     object.  It is passed the name of the module or package of the
#     application.  Once it is created it will act as a central registry for
#     the view functions, the URL rules, template configuration and much more.
from db_util import Database
# функция, которая вызывается при ошибке 404
def page_not_found (e):
    return ("error.html")


app = Flask(__name__)
# нужно добавить секретный код - только с ним можно менять данные сессии
app.secret_key = "111"
# подключение ORM - SQLAlchemy
# uri: СУБД://login:password@host:port/db_name
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://lesson:lesson@localhost:5436/lesson"
db = SQLAlchemy(app)
# регистрируем функцию, которая вызывается при указанной ошибке
app.register_error_handler(404, page_not_found)

# необходимо добавлять, чтобы время сессии не ограничивалось закрытием браузера
app.permanent_session_lifetime = datetime.timedelta(days=365)

# db = Database()

# класс-таблица films
class Films(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.VARCHAR)
    rating = db.Column(db.FLOAT)
    country = db.Column(db.VARCHAR)


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
    # переписываем запрос с помощью SQLAlchemy
    # в данном случае при отсутствии указанного фильма, выходит 404 ошибка
    film = db.get_or_404(Films, film_id)
    return render_template("film.html", title=film.name, film=film)

@app.route('/new_film', methods=['GET'])
def my_form():
    return render_template('new_film.html')
@app.route('/new_film', methods=['POST'])
def new_film():
    id = request.form['id']
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


if __name__ == "__main__":
    app.run(debug=True)
