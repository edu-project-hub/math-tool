from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    # Register Blueprints
    from blueprints.tree import tree_bp
    from blueprints.math import math_bp
    from blueprints.dice import dice_bp
    app.register_blueprint(tree_bp)
    app.register_blueprint(math_bp)
    app.register_blueprint(dice_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
