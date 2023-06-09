from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int(validate=validate.Range(min=1900, max=2030))
    rating = fields.Int()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):

    def get(self):
        movies = Movie.query

        if (genre_id := request.args.get('genre_id')) and (director_id := request.args.get('director_id')):
            movies = movies.filter(Movie.genre_id == genre_id, Movie.director_id == director_id)

        elif genre_id := request.args.get('genre_id'):
            movies = movies.filter(Movie.genre_id == genre_id)

        elif director_id := request.args.get('director_id'):
            movies = movies.filter(Movie.director_id == director_id)

        return movies_schema.dump(movies.all()), 200


    def post(self):
        data = request.json
        movies = Movie(**data)
        db.session.add(movies)
        db.session.commit()
        return "", 201


@movie_ns.route('/<int:id>')
class MovieView(Resource):

    def get(self, id):
        movie = Movie.query.get(id)
        return movie_schema.dump(movie), 200

    def put(self, id):
        movie = Movie.query.get(id)
        req = request.json

        movie.title = req.get('title')
        movie.description = req.get('description')
        movie.trailer = req.get('trailer')
        movie.year = req.get('year')
        movie.rating = req.get('rating')

        db.session.add(movie)
        db.session.commit()

        return "", 204


    def patch(self, id):
        movie = Movie.query.get(id)
        req = request.json

        if title := request.args.get('title'):
            movie.title = title

        if description := req.get('description'):
            movie.description = description

        if trailer := req.get('trailer'):
            movie.trailer = trailer

        if year := req.get('year'):
            movie.year = year

        if rating := req.get('rating'):
            movie.rating = rating

        db.session.add(movie)
        db.session.commit()

        return "", 204


    def delete(self, id):
        Movie.query.filter(Movie.id == id).delete()
        db.session.commit()
        return '', 204


@director_ns.route('/')
class DirectorsViews(Resource):

    def post(self):
        data = request.json
        director = Director(**data)
        db.session.add(director)
        db.session.commit()
        return "", 201


@director_ns.route('/<int:id>')
class DirectorView(Resource):

    def put(self, id):
        data = request.json
        director = Director.query.filter(Director.id == id).one()
        director.name = data.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204


    def patch(self, id):
        director = Director.query.get(id)
        data = request.json
        if data.get("name"):
            director.name = data.get("name")
        db.session.add(director)
        return "", 204


    def delete(self, id):
        director = Director.query.filter(Director.id == id).one()
        db.session.delete(director)
        db.session.commit()

        return '', 204


@genre_ns.route('/')
class GenresViews(Resource):

    def post(self):
        data = request.json
        genre = Genre(**data)
        db.session.add(genre)
        db.session.commit()
        return "", 201


@genre_ns.route('/<int:id>')
class GenreView(Resource):

    def put(self, id):
        data = request.json
        genre = Genre.query.filter(Genre.id == id).one()
        genre.name = data.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204


    def patch(self, id):
        genre = Genre.query.get(id)
        data = request.json
        if data.get('name'):
            genre.name = data.get("name")
        db.session.add(genre)
        return "", 204


    def delete(self, id):
        Genre.query.filter(Genre.id == id).delete()
        db.session.commit()
        return "", 204

if __name__ == '__main__':
    app.run(debug=True)