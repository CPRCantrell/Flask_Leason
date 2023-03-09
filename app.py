from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from dotenv import load_dotenv
from os import environ

load_dotenv()

# Create App instance
app = Flask(__name__)

# Add DB URI from .env
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('SQLALCHEMY_DATABASE_URI')

# Registering App w/ Services
db = SQLAlchemy(app)
ma = Marshmallow(app)
api = Api(app)
CORS(app)
Migrate(app, db)

# Models  -- plans out database
class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    make = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer)

    def __repr__(self) -> str:
        return f'{self.year} {self.make} {self.model}'

# Schemas -- translate into JSON (interpreter between languages)
class CarSchema(ma.Schema):
    class Meta:
        fields = ("id", "make", "model", "year")

car_schema = CarSchema()
cars_schema = CarSchema(many=True)

# Resources
class CarListResource(Resource):
    def get(self):
        return cars_schema.dump(Car.query.all())

    def post(self):
        add_car = Car(make=request.json['make'],model=request.json['model'],year=request.json['year'])
        db.session.add(add_car)
        db.session.commit()
        return car_schema.dump(add_car), 201

class CarResourse(Resource):
    def get(self, car_id):
        return car_schema.dump(Car.query.get_or_404(car_id))

    def delete(self, car_id):
        car_from_db = Car.query.get_or_404(car_id)
        db.session.delete(car_from_db)
        db.session.commit()
        return '', 204

    def put(self, car_id):
        car_from_db = Car.query.get_or_404(car_id)

        if 'make' in request.json:
            car_from_db.make = request.json['make']
        if 'model' in request.json:
            car_from_db.model = request.json['model']
        if 'year' in request.json:
            car_from_db.year = request.json['year']

        db.session.commit()
        return car_schema.dump(car_from_db)


# Routes
api.add_resource(CarListResource, '/api/cars')
api.add_resource(CarResourse, '/api/cars/<int:car_id>')
