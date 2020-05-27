import os

from app import create_app
from app.model import db


app = create_app(os.getenv('SERVER_ENV') or 'dev')
app.run()

@app.cli.command()
def initdb():
    print('were')
    db.drop_all()
    db.create_all()
