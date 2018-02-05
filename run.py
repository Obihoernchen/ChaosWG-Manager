# This should be used for development/debugging purposes only
# Use a proper WSGI server for production use

from chaoswg import app

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
