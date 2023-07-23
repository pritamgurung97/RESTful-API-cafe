from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        dictionary = {}

        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self,column.name)

        # return dictionary

        #Using list comprehension
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")
    

## HTTP GET - Read Record
@app.route('/random')
def get_random_cafe():
    all_cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(all_cafes)
    # return f'<h1> {random_cafe.name} </h1>'
    # returning a json serialization data
    # return jsonify(
    #     cafe={
    #         'can_take_calls': random_cafe.can_take_calls,
    #         'coffee_price': random_cafe.coffee_price,
    #         'has_sockets': random_cafe.has_sockets,
    #         'has_toilets': random_cafe.has_toilet,
    #         'has_wifi': random_cafe.has_wifi,
    #         'id': random_cafe.id,
    #         'img_url': random_cafe.img_url,
    #         'location': random_cafe.location,
    #         'map_url': random_cafe.map_url,
    #         'name': random_cafe.name,
    #         'seats': random_cafe.seats
    #     })
    return jsonify(cafe=random_cafe.to_dict())


@app.route('/all')
def get_all_cafes():
    all_cafes = db.session.query(Cafe).all()

    #To give a clear view we create a list nested with the dictionary of cafes
    # cafes_list = [cafe.to_dict() for cafe in all_cafes]
    # return jsonify(cafes=cafes_list)

    return jsonify(cafes=[cafe.to_dict() for cafe in all_cafes])

@app.route('/search')
def search_by_location():
    location = request.args.get('loc')
    cafes_by_location = db.session.query(Cafe).where(Cafe.location == location).all()
    if cafes_by_location:
        return jsonify(cafe=[cafe.to_dict() for cafe in cafes_by_location])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404

@app.route('/add', methods=['POST','GET'])
def add_cafe():
    new_cafe = Cafe(
            name=request.form.get('name'),
            map_url=request.form.get('map_url'),
            img_url=request.form.get('img_url'),
            location=request.form.get('loc'),
            seats=request.form.get('seats'),
            has_toilet=bool(request.form.get('toilet')),
            has_wifi=bool(request.form.get('wifi')),
            has_sockets=bool(request.form.get('sockets')),
            can_take_calls=bool(request.form.get('calls')),
            coffee_price=request.form.get('coffee_price'),
        )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={'success': 'successfully added the new cafe.'})


@app.route('/update-price/<int:cafe_id>', methods=['GET','POST','PATCH'])
def update(cafe_id):
    cafe_to_be_edited = Cafe.query.filter_by(id=cafe_id).first()
    if cafe_to_be_edited:

        cafe_to_be_edited.coffee_price = request.args.get('new_price')
        db.session.commit()
        return jsonify(success="Successfully updated the price."), 200
    else:
        return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404





## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record
@app.route('/delete/<cafe_id>', methods=['GET','POST','DELETE','PATCH'])
def delete(cafe_id):
    cafe_to_be_deleted = Cafe.query.filter_by(id=cafe_id).first()
    if cafe_to_be_deleted:
        api_key = 'hello'
        api_key_user = request.args.get('api-key')
        if api_key_user == api_key:
            db.session.delete(cafe_to_be_deleted)
            db.session.commit()
            return jsonify(success="The cafe has been successfully deleted from the database."), 200
        else:
            return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api_key."), 403
    else:
        return jsonify(error="Sorry a cafe with that id was not found in the database."), 404



if __name__ == '__main__':
    app.run(debug=True)
