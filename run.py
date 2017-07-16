from app import ChaosWG
from models import init_database, create_tables, insert_testdata

if __name__ == '__main__':
    app = ChaosWG(__name__)

    db = init_database(app)
    create_tables(db)
    # insert_testdata(db)
    app.run(debug=True)
