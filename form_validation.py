from typing import Tuple
from forms import PuzzleInputForm

def validate_input(form: PuzzleInputForm) -> Tuple[bool, PuzzleInputForm]:
    # Check if the sum of the numbers is equal to the target
    valid = True
    numbers = [
        form.number1,
        form.number2,
        form.number3,
        form.number4,
        form.number5,
        form.number6,
    ]
    for number in numbers:
        if number.data < 1:
            valid = False
            number.errors.append('Number must be greater than 0')
        if number.data > 100:
            valid = False
            number.errors.append('Number must be less than 100')

    if form.target.data < 100:
        valid = False
        form.target.errors.append('Target must be greater than 100')
    if form.target.data > 999:
        valid = False
        form.target.errors.append('Target must be less than 999')
    if form.min_runtime.data < 1:
        valid = False
        form.min_runtime.errors.append('Max runtime must be greater than 0')
    if form.min_runtime.data > 300:
        valid = False
        form.min_runtime.errors.append('Max runtime must be less than 300')
    return (valid, form)
