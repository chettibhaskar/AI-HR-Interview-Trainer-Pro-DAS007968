from flask import Flask, render_template, request, session
from hr_trainer_pro import ProHRTrainer
import os

app = Flask(__name__)
app.secret_key = "das007968_pro"
trainer = ProHRTrainer()

@app.route('/', methods=['GET','POST'])
def index():
    result = None
    question_data = None
    if request.method == 'POST':
        company = request.form.get('company','Google')
        q_text = request.form.get('question','')
        response = request.form.get('response','')
        cat = request.form.get('category','behavioral')

        if response:
            result = trainer.analyze_response(q_text, response, company)
            question_data = {'q': q_text, 'cat': cat, 'company': company}
        else:
            # Generate new mock interview
            qs = trainer.get_random_questions(company, 5)
            session['mock_qs'] = qs
            return render_template('index.html', mock_questions=qs, company=company)

    return render_template('index.html', result=result, q_data=question_data)

@app.route('/mock')
def mock():
    qs = trainer.get_random_questions("Google", 5)
    return render_template('index.html', mock_questions=qs, company="Google")

if __name__ == '__main__':
    app.run(debug=True, port=5000)