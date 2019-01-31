from flask import Flask, Response, request, jsonify
app = Flask(__name__)

@app.route('/interact', methods=['POST'])
def main():
	question = request.form['question']
	return ""

if __name__ == "__main__":
    app.run(port=8000)
