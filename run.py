from app import create_app
from models import init_database, create_tables, insert_testdata

if __name__ == '__main__':
    app = create_app()

    db = init_database(app)
    create_tables(db)
    # insert_testdata(db)
    app.run(debug=True)
