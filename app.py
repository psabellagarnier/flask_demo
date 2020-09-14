from flask import Flask, render_template, request, redirect

app = Flask(__name__)

entered_text = ''

@app.route('/')
def index():
  return render_template('form.html', outside_title='This is a title!')

@app.route('/form_action', methods=['GET', 'POST'])
def form_action():
  entered_text = request.form['form_input']
  return render_template('graph.html', input_text=entered_text)

if __name__ == '__main__':
  app.run(port=33507)
