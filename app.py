from flask import Flask, render_template, request, redirect, send_from_directory
from utils import load_all_stories, extract_text_from_docx
from query_engine import embed_stories, find_best_story, refine_query
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'stories'
ALLOWED_EXTENSIONS = {'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

story_db = load_all_stories()
story_db, story_matrix, vectorizer = embed_stories(story_db)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        user_query = request.form['user_query']
        refined_query = refine_query(user_query)
        best_story, score = find_best_story(refined_query, story_db, story_matrix, vectorizer)
        return render_template('result.html', story=best_story, score=round(score, 2), query=user_query)
    return render_template('query.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global story_db, story_matrix, vectorizer
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(path)
            story_db = load_all_stories()
            story_db, story_matrix, vectorizer = embed_stories(story_db)
            return redirect('/')
    return render_template('upload.html')

@app.route('/admin')
def admin():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('admin.html', stories=files)

@app.route('/delete/<filename>')
def delete_story(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(path):
        os.remove(path)
    return redirect('/admin')

if __name__ == '__main__':
    app.run(debug=True)
