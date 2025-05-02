from flask import Flask, request, jsonify
from flask_cors import CORS 
from sudoku_solver import solve_sudoku_image9x9
from sudoku_solver import solve_sudoku_image16x16

app = Flask(__name__)
CORS(app) 

@app.route('/')
def index():
    return "Welcome to the Sudoku Solver API!"

@app.route('/solve/9x9', methods=['POST'])
def solve_9x9():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image']
    try:
        grid, solution= solve_sudoku_image9x9(image, size=9)
        return jsonify({'unsolved_grid': grid, 'solved_grid': solution})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/solve/16x16', methods=['POST'])
def solve_16x16():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image']
    try:
        solution = solve_sudoku_image16x16(image, size=16)
        return jsonify({'solution': solution})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
