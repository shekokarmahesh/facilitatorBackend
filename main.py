from flask import Flask
from routes.auth_routes import auth_routes
from routes.facilitator_routes import facilitator_routes
from routes.offerings_routes import offerings_routes

app = Flask(__name__)

# Register blueprints
app.register_blueprint(auth_routes)
app.register_blueprint(facilitator_routes)
app.register_blueprint(offerings_routes)

if __name__ == "__main__":
    app.run(debug=True)


