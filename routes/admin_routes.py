def admin_routes(app):

    @app.route("/admin")
    def admin():
        return "<h1>Admin Dashboard</h1>"