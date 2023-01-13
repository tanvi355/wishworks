from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# the db name here is 'property' and port number for postgresql is 5432
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@127.0.0.1:5432/property'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# class for property and its methods
class property(db.Model):
    __tablename__ = 'property_details'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(120))
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))

    # constructor
    def __init__(self, name, address, city, state):
        self.name = name
        self.address = address
        self.city = city
        self.state = state

    # an object method to represent the object
    def json_rep(self):
        return {"id":self.id, "name":self.name, "address":self.address, "city":self.city, "state":self.state}

    # method to display only the city name
    def city_rep(self):
        return {"city": self.city}


# routes for all the operations
@app.route('/')
def home():
    return "Property Management API"

# create a new property
@app.route('/create_new_property', methods=['GET', 'POST'])
def create():
    data = request.get_json()
    name = data['name']
    address = data['address']
    city = data['city']
    state = data['state']
    # create new object
    new_property = property(name, address, city, state)
    db.session.add(new_property)
    db.session.commit()

    # display all the property's details
    property_list = property.query.all()
    return {'Properties':list(x.json_rep() for x in property_list)}


# fetch a property by its city name
@app.route('/fetch_property_details', methods=['GET'])
def fetch():
    if request.method=='GET':
        # provide city name
        data = request.get_json()
        property_list_by_city = property.query.filter_by(city=data["city"])
        return {"Properties in {city}": list(x.json_rep() for x in property_list_by_city)}


# update property details
@app.route('/update_property_details', methods=['PUT', 'GET'])
def update():
    # provide property_id, property name, address, city, state
    data = request.get_json()
    property_to_update = property.query.filter_by(id=data["id"]).first()
    # if property with given ID exists
    if property_to_update:
        property_to_update.name = data["name"]
        property_to_update.address = data["address"]
        property_to_update.city = data["city"]
        property_to_update.state = data["state"]

        db.session.add(property_to_update)
        db.session.commit()

    # if property of the given id does not exist
    else:
        return f"Property of the given ID does not exist"

    # display all the property's details
    property_list = property.query.all()
    return {'Properties':list(x.json_rep() for x in property_list)}


# ADDITIONAL API ENDPOINTS
# find cities by state
@app.route('/find_cities_by_state', methods=['POST', 'GET'])
def find_cities_by_state():
    # provide state name
    data = request.get_json()
    cities_by_state = property.query.filter_by(state=data["state"])
    if len(list(cities_by_state))>0:
        return {"cities belonging to the given state are": list(x.city_rep() for x in cities_by_state)}
    else:
        return "No properties exist in the given state"



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)