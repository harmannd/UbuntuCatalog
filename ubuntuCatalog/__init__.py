from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
<<<<<<< HEAD
    return "Hello, catalog with database!"
=======
    return "Hello catalog"
>>>>>>> 016cfab41abd5519176c4fb202092ce0124e2ca9
if __name__ == "__main__":
    app.debug = True
    app.run()
