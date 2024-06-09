from flask_wtf import FlaskForm 
from wtforms import DecimalField, IntegerField, RadioField, SelectField, StringField, SubmitField, TextAreaField, FileField 

class PuzzleInputForm(FlaskForm):
    target = IntegerField('Target', default=568)
    number1 = IntegerField('Number 1', default=75)
    number2 = IntegerField('Number 2', default=25)
    number3 = IntegerField('Number 3', default=9)
    number4 = IntegerField('Number 4', default=2)
    number5 = IntegerField('Number 5', default=9)
    number6 = IntegerField('Number 6', default=4)
    min_runtime = IntegerField('Minimum Runtime secs', default=5)
    submit = SubmitField('Solve')