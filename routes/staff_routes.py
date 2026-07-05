def staff_routes(app):

    @app.route("/staff")
    def staff():
        return "<h1>Staff Dashboard</h1>"