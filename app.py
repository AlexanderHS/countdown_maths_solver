import datetime
import logging
import os
from typing import List, Tuple, Optional
from flask import Flask, render_template, request
from flask.typing import ResponseReturnValue

# Importing the necessary modules
from forms import PuzzleInputForm
from form_validation import validate_input
from models import SolveState
from solutions import get_solutions


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

app.config["SECRET_KEY"] = "dfgkjndfkgjs"


@app.route("/", methods=["GET", "POST"])
def base_url() -> ResponseReturnValue:
    solutions: Optional[List[SolveState]] = None
    form: PuzzleInputForm = PuzzleInputForm()
    result: str = ""
    if form.validate_on_submit():
        validalidation_result: Tuple[bool, PuzzleInputForm] = validate_input(form)
        valid: bool = validalidation_result[0]
        form = validalidation_result[1]
        if valid:
            start_time = datetime.datetime.now()
            numbers: List[int] = [
                form.number1.data,
                form.number2.data,
                form.number3.data,
                form.number4.data,
                form.number5.data,
                form.number6.data,
            ]
            target: int = form.target.data
            solutions = get_solutions(
                numbers=numbers, target=target, stop_after_seconds=form.min_runtime.data
            )
            end_time = datetime.datetime.now()
            time_elapsed = end_time - start_time
            result = f"Found {solutions[0].formula_str() if solutions else ''} in {time_elapsed.total_seconds()} seconds!"
        else:
            result = "The input form is invalid!"
    else:
        result = ""
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
        "form": form,
        "form_elements": form_elements,
        "title": "Countdown Numbers Game Solver",
        "result": result,
        "solutions": solutions,
    }
    return render_template("index.html", **template_data)


if __name__ == "__main__":

    # Use waitress for production, otherwise, use the Flask development server
    if os.name == "posix":
        from waitress import serve

        serve(app, host="0.0.0.0", port=8045)
    else:
        app.run(host="0.0.0.0", port=8045, debug=True)
