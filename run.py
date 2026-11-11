"""Entry point: starts the SkyCast development server.

Run with: python run.py
"""

from skycast import create_app

app = create_app()

if __name__ == "__main__":
    #debug=True reloads the server when code changes and shows detailed errors.
    #Turn it off before a real deployment 
    app.run(debug=True)


