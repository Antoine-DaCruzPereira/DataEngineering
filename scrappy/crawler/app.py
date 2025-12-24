from flask import Flask

# On importe les "Blueprints" qu'on vient de créer
from routes.main import bp as main_bp
from routes.stats import bp as stats_bp
from routes.export import bp as export_bp

app = Flask(__name__)

# On enregistre les routes dans l'application
app.register_blueprint(main_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(export_bp)

if __name__ == '__main__':
    # Le port 5001 comme d'habitude
    app.run(debug=True, port=5001)