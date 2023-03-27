from flask import Flask,render_template
app = Flask(__name__)

@app.route('/get_figure')
def hello_world():
    # return 'Hello World!'
    name = '张先生您好!!'
    return render_template('hello.html', name=name)
if __name__ == '__main__':
    app.run(debug=True)