def auth_routes(app):

    @app.route("/")
    def home():
        return "<h1>Trekking App</h1>"
    
    @app.route("/login")
    def login():
        return "Login Page"
    
    @app.route("/register")
    def register():
        return "Register Page"