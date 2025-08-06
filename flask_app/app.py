from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', title='欢迎使用 Flask Web 应用')

if __name__ == '__main__':
    app.run(debug=True)
