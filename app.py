from flask import (
    Flask, render_template,
    url_for, redirect, request,
    session,abort,jsonify
)
from uuid import uuid4
from instagram_bot import *
from models.sql_server_orm import *
from question_shortener import questionShortener
from werkzeug.exceptions import BadRequest
import os
import soundfile as sf
import av
import speech_recognition as sr
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = uuid4().hex
user_section = dict()
user_is_login = dict()

UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'wav','mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def recognize_speech_from_wav(wav_path: str) -> str:
    recognizer = sr.Recognizer()
    try:
        with sf.SoundFile(wav_path) as audio_file:
            logging.info(f"Processing file - Sample rate: {audio_file.samplerate}, Channels: {audio_file.channels}")

        with sr.AudioFile(wav_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language='fa-IR')

        logging.info(f"Recognized text: {text}")
        return text
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"
    except Exception as e:
        return f"An error occurred: {str(e)}"

def convert_webm_to_wav(input_file_path, output_file_path):
    input_container = av.open(input_file_path)
    output_container = av.open(output_file_path, 'w')

    stream = output_container.add_stream('pcm_s16le')

    for frame in input_container.decode(audio=0):
        for packet in stream.encode(frame):
            output_container.mux(packet)

    for packet in stream.encode(None):
        output_container.mux(packet)

    input_container.close()
    output_container.close()


@app.route('/',methods=['GET', 'POST'])
@app.route('/index',methods=['GET', 'POST'])
@app.route('/home',methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        # return redirect('/questions')
        if user_is_login.get(request.remote_addr,None):
            return redirect('/questions')
        return redirect('/login')
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    context = {}
    if request.method == 'POST':
        session['Email'] = request.form['username']
        if user_detail := search_user(session['Email']):
            passwd = request.form['password']
            result = user_detail.get('password',None)
            if result and verify_password(result,passwd):
                user_is_login[request.remote_addr] = True
                return redirect('/questions')
            else:
                context['error'] = 'رمز اشتباه است'
        else:
            context['error'] = 'اکانتی با این اطلاعات یافت نشد'

    return render_template('login.html', **context)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    context = {}
    if request.method == 'POST':
        email = request.form['email']
        instagram = request.form['instagram-id']
        if not search_user(email) :
            passwd = request.form['password']
            rePasswd = request.form['repeat-password']
            if passwd == rePasswd and len(passwd) > 8:
                create_user(email,instagram,passwd)
                return redirect('/login')
            else:
                context['error'] = 'رمز باید بیشتر از 8 حرف باشد'
        else:
            context['error'] = 'این ایمیل موجود میباشد'
    return render_template('signup.html',**context)


@app.route('/forget',methods=['GET','POST'])
def forget():
    print(0)
    code = str(uuid4())[:5]
    if request.method == "POST":
        if 'answer-code' not in session:
            username = request.form['email']
            print(1)
            username = search_user(username)['instagram_id']
            cl = start(INSTAGRAM_USERNAME,INSTAGRAM_PASSWORD)
            user_id = str(find_user_id(cl,username))
            if user_id:
                send_direct_from_specific_comment(cl, list_of_users=[user_id], ANSWER=code)
                user_section[request.remote_addr] = code
                session['answer-code'] = True
                return render_template('forget.html', TEXT='کد را وارد کنید')
        else:
            print(2)
            input_code = request.form['email']
            if input_code == user_section[request.remote_addr]:
                session['Email'] = request.form['email']
                return redirect('/questions')
            else:
                return redirect('/login')

    return render_template('forget.html',TEXT='ایمیل')

@app.route('/search', methods=['GET'])
def searchQuestion():
    query = request.args.get('query')
    print("this is query: ", query.encode('utf-8'))
    if query:
        filtered_question = search_question(query)
    else:
        filtered_question = get_questions()
    return render_template('questions.html', questions=filtered_question)


@app.route('/questions' ,methods=['GET', 'POST'])
def questions():
    if request.method == "POST":
        if question := request.form['question']:
            title = questionShortener(question)
            add_question(title,question,session['Email'])
    Questions = get_questions()
    return render_template('questions.html',questions=Questions)


@app.route('/questions/<int:question_id>', methods=['GET', 'POST'])
def question_detail(question_id):
    if request.method == 'POST':
        if 'ratingValue' in request.form and request.form['ratingValue']:
            rate = request.form.get('rate')
            user_id = request.form.get('usernameValue')
            add_rating(rate, question_id, user_id)
            return redirect(request.referrer)
        if 'answer' in request.form:
            answer = request.form['answer']
            try:
                add_answer(question_id, session.get('Email', 'unknown'), answer)
                return redirect(f'/questions/{question_id}')
            except BadRequest:
                return redirect(f'/questions/{question_id}')

    Questions = get_questions()
    question_keys = [item[-1] for item in Questions]
    question_dict = dict(zip(question_keys, Questions))
    isAdmin = question_dict[question_id][-2] == session.get('Email', '')
    answers = get_answers(question_id)
    return render_template('question_detail.html',
                           question=question_dict[question_id],
                           answers=answers,
                           question_id=question_id,
                           isAdmin=True)

@app.route('/topUsers',methods=['GET'])
def topUsers():
    users = get_top_users()
    return render_template('topUsers.html',users=users)

@app.route('/myProfile',methods=['GET','POST'])
def myProfile():
    return render_template('myProfile.html')

@app.route("/logout" ,methods=['GET'])
def logout():
    session.pop("Email", None)
    user_is_login.pop(request.remote_addr, None)
    return render_template('home.html')

@app.route('/voice', methods=["GET", "POST"])
def voice():
    if request.method == 'POST':
        if 'path' in session:
            text = recognize_speech_from_wav(session['path'])
            session.pop('path', None)
            Questions = get_questions()
            return render_template('questions.html',questions=Questions,
                                   question_data = text)

        else:
            if 'audio' not in request.files:
                return jsonify({"error": "No audio file in request"}), 400

            audio = request.files['audio']
            if audio.filename == '':
                return jsonify({"error": "No selected file"}), 400

            secure_path = str(uuid4())

            filename = secure_filename(f'{secure_path}.webm')
            webm_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio.save(webm_path)

            wav_filename = secure_filename(f'{secure_path}.wav')
            wav_path = os.path.join(app.config['UPLOAD_FOLDER'], wav_filename)

            convert_webm_to_wav(webm_path, wav_path)

            session['path'] = wav_path
            os.remove(webm_path)

            return jsonify({"message": "Audio uploaded successfully"}), 200

    return render_template('voice.html')


if __name__ == '__main__':
    # app.run(port=3000)
    app.run(debug=True)