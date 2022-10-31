import random

from flask import Flask, render_template, request, make_response, session
from flask_sqlalchemy import SQLAlchemy

from db_util import Database

# функция, которая вызывается при ошибке 404
def page_not_found (e):
    return ("error.html")

app = Flask(__name__)
app.secret_key = "111"
# подключение ORM - SQLAlchemy
# uri: СУБД://login:password@host:port/db_name
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://lesson:lesson@localhost:5436/lesson"
db = SQLAlchemy(app)
# регистрируем функцию, которая вызывается при указанной ошибке
app.register_error_handler(404, page_not_found)

# db = Database()


# класс-таблица films
class Films(db.Model):
    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.VARCHAR)
    rating = db.Column(db.FLOAT)
    country = db.Column(db.VARCHAR)


@app.route("/films")
def films_list():
    # переписываем запрос с помощью SQLAlchemy
    films = Films.query.all()

    country = request.args.get("country")
    context = {
        'films': films,
        'title': "FILMS",
        'country': country
    }

    return render_template("films.html", **context)


@app.route("/film/<int:film_id>")
def get_film(film_id):
    # переписываем запрос с помощью SQLAlchemy
    # в данном случае при отсутствии указанного фильма, выходит 404 ошибка
    film = db.get_or_404(Films, film_id)
    return render_template("film.html", title=film.name, film=film)


# метод для создания заметки
@app.route("/add_note", methods=['get', 'post'])
def add_note():
    if request.method == "POST":
        note = request.form.get('note')

        db.cur.execute("INSERT INTO notes(note) VALUES (%s)", (note, ))
        db.con.commit()
        return "Note was added"

    return render_template("note.html")


# метод для получения данных о рандомном числе
# здесь мы не рендерим шаблон, отдаем просто контекстк
@app.route("/get_random", methods=['get'])
def get_random():
    min_v = int(request.args.get("min", 1))
    max_v = int(request.args.get("max", 100))

    return {'randint': random.randint(min_v, max_v)}


if __name__ == '__main__':
    app.run(port=8000, debug=True)