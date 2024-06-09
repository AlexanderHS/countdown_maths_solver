import logging
import os
from typing import List, Tuple
from flask import Flask, render_template, request

# Importing the necessary modules
from forms import PuzzleInputForm
from form_validation import validate_input
from models import SolveState
from solutions import get_solutions


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

app.config['SECRET_KEY'] = 'dfgkjndfkgjs'

@app.route('/', methods=['GET', 'POST'])
def base_url():
    solutions: List[SolveState] = None
    form: PuzzleInputForm = PuzzleInputForm()
    if form.validate_on_submit():
        validalidation_result: Tuple[bool, PuzzleInputForm] = validate_input(form)
        valid = validalidation_result[0]
        form = validalidation_result[1]
        if valid:
            solutions: List[SolveState] = get_solutions(form, stop_after_seconds=form.min_runtime.data)
            result=f'Found {solutions[0].formula_str()} in {form.min_runtime.data} seconds!'
        else:
            result='The input form is invalid!'
    else:
        result = ''
    form_elements = [
        form.number1,
        form.number2,
        form.number3,
        form.number4,
        form.number5,
        form.number6,
        form.target,
        form.min_runtime,
    ]
    template_data = {
        'form': form,
        'form_elements': form_elements,
        'title': 'Home',
        'result': result,
        'solutions': solutions
    }
    return render_template('index.html', **template_data)

if __name__ == "__main__":

    # PRODUCTION ENVIRONMENT
    if os.name == "posix":
        #app.run(host='0.0.0.0', port=8099, debug=True)
        from waitress import serve
        serve(app, host="0.0.0.0", port=8045)
    # TESTING ENVIRONMENT
    if os.name == "nt":
        app.run(host='0.0.0.0', port=8045, debug=True)