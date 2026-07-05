def user_routes(app):

    @app.route("/user")
    def user():
        return "<h1>User Dashboard</h1>"