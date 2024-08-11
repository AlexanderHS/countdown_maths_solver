from typing import Tuple
from forms import PuzzleInputForm

MAX_TIME = 90

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

    if form.target.data < 1:
        valid = False
        form.target.errors.append('Target must be greater than 0')
    if form.target.data > 999:
        valid = False
        form.target.errors.append('Target must be less than 999')
    if form.min_runtime.data < 1:
        valid = False
        form.min_runtime.errors.append('Max runtime must be greater than 0')
    if form.min_runtime.data > MAX_TIME:
        valid = False
        form.min_runtime.errors.append(f'Runtime must be less than {MAX_TIME} seconds. Thems the rules!')
    return (valid, form)
