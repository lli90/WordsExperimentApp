from flask import Flask, request, send_from_directory, render_template, session
from flask_cors import cross_origin
from functools import wraps
from pydub import AudioSegment
import random
import itertools
import uuid
import time
import secrets
import os
import urllib
from urllib.parse import urlparse

from config import BASE_FILE_LOCATION 
from experiment import Experiment
import attack
import utils

METHOD_NOT_ALLOWED = "Error: Method not allowed"
EXPERIMENT_NOT_FOUND = "Error: Experiment ID not found"

ALLOWED_TRIAL_TYPES = ["/visual", "/verbal"]

app = Flask(__name__, static_folder="./build/static",
            template_folder="./build/")

app.secret_key = secrets.token_urlsafe(64)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='None',
)

WORDLIST_NAME = "trustwords.csv"
CURRENT_EXP = "current_exp"

def requires_experiment_id(f):
    @wraps(f)

    def decorated_function(*args, **kwargs):
        if request.method != "GET":
                return METHOD_NOT_ALLOWED, 405

        exp_id = session.get(get_referring_endpoint(request))

        if not exp_id in session or exp_id == None:
            return EXPERIMENT_NOT_FOUND, 400

        session[CURRENT_EXP] = exp_id

        return f(*args, **kwargs)
    
    return decorated_function

def get_referring_endpoint(request):
    """
    Gets what type of trial the user has requested. 
    """
    trialType = urlparse(request.referrer).path

    # Just to stop rnd stuff being passed into the session
    # dictionary
    if not trialType in ALLOWED_TRIAL_TYPES:
        raise Exception(f"Invalid trialType provided. Referer string: \"{request.referrer}\"")

    return trialType

def get_referring_query_params(request):
    """
    Gets the query parameters of a request 
    """
    query_str = request.referrer.split("?")[-1]
    return urllib.parse.parse_qs(query_str)

def generate_audio_file(words):
    """
    Generates the audio file for set of words and returns the filename
    """
    
    duration = 0

    filePath = f"{BASE_FILE_LOCATION}audio/generated/{'_'.join(words)}.mp3"
    if not os.path.isfile(filePath):

        combined = AudioSegment.from_mp3(
            f"{BASE_FILE_LOCATION}audio/{words[0].upper()}.mp3")

        for w in words[1:]:
            a = AudioSegment.from_mp3(
                f"{BASE_FILE_LOCATION}audio/{w.upper()}.mp3")
            combined += a

        combined.export(filePath, format="mp3")
        duration = len(combined)

    return filePath.split("/")[-1], duration

@app.after_request
def after_request(response):
    """
    Code performed after the request 
    """

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Credentials
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Server'] = 'nginx'
    return response


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """
    This is used to fix Flask's compatability with the react-routing
    """
    return render_template("index.html")

@app.route('/')
def index():
    """
    Default endpoint
    """
    return render_template("index.html")

@app.route('/get_audio')
@requires_experiment_id
@cross_origin()
def get_audio():
    """
    Gets the currently active audio file
    """

    exp_id = session[CURRENT_EXP]
    exp = Experiment.from_json(session[exp_id])

    if utils.experiment_finished(exp_id):
        exp.end_experiment()
        exp.commit(session)

        return "DONE"

    exp.increment_audio_clicks()
    exp.record_audio_button_click_time()

    # Checks for an attack case
    if exp.is_attack():
        words = exp.get_current_attack_wordlist()
    else:
        words = exp.get_current_wordlist()

    fileName, fileDuration = generate_audio_file(words)

    exp.record_audio_clip_length(fileDuration)
    exp.commit(session)

    return send_from_directory(f'{BASE_FILE_LOCATION}audio/generated', fileName)

@app.route('/get_visual')
@requires_experiment_id
@cross_origin()
def get_visual_attack_words():
    """
    Gets the set of possible attack words for the visual trial
    """
        
    exp_id = session[CURRENT_EXP]
    exp = Experiment.from_json(session[exp_id])

    if utils.experiment_finished(exp_id):

        exp.end_experiment()
        exp.commit(session)

        return "DONE"

    if not exp.check_if_round_started():
        exp.record_round_start_time()
        exp.commit(session)

    attackWordlist = exp.get_current_attack_wordlist()

    if attackWordlist:
        return " ".join(attackWordlist)
    else:
        return " ".join(exp.get_current_wordlist())

@app.route('/get_words')
@requires_experiment_id
@cross_origin()
def get_words():
    """
    Gets the currently active set of words. This is the non-attack set
    """
    
    exp_id = session[CURRENT_EXP]
    exp = Experiment.from_json(session[exp_id])

    if utils.experiment_finished(exp_id):

        exp.end_experiment()
        exp.commit(session)

        return "DONE"

    if not exp.check_if_round_started():
        exp.record_round_start_time()
        exp.commit(session)

    return "  ".join(exp.get_current_wordlist())

@app.route('/new_experiment')
@cross_origin()
def new_experiment():
    """
    This end point is designed to initialise the experiment attached to a certain ID
    """

    trialType = get_referring_endpoint(request)

    if not trialType:
        return "Missing \'type\' parameter!", 400

    query_params = get_referring_query_params(request)
    
    # If they're included the program will add
    participant_id = query_params.get("Participant_id")
    is_mturk = query_params.get("MTurk")

    if not session.get(trialType):

        user_agent = request.headers.get("User-Agent")

        exp_id = str(uuid.uuid4())

        session[trialType] = exp_id

        exp = Experiment(exp_id, user_agent, trialType, participant_id, is_mturk)
        utils.gen_word_set(WORDLIST, exp)
        exp.commit(session)

        return exp_id 

    return session.get(trialType)

@app.route('/submit_result')
@requires_experiment_id
@cross_origin()
def submit_result():
    """
    Endpoint used to submit the user's response

    Required params:

    'result' should be "True" or "False"
    """

    result = request.args.get("result", None)

    if not result:
        return "Error: Missing parameter \'result\'", 400

    if not result in ["True", "False"]:
        return f"Error: Invalid value \"{result}\" for result", 400

    exp_id = session[CURRENT_EXP]
    exp = Experiment.from_json(session[exp_id])

    exp.record_response(result)
    exp.record_round_end_time()
    exp.move_to_next_round()

    exp.commit(session)

    return "OK"

@app.route('/audio_playing')
@requires_experiment_id
@cross_origin()
def audio_playing():
    """
    Endpoint contacted when the audio for the verbal trial begins playing
    """

    exp_id = session[CURRENT_EXP]
    exp = Experiment.from_json(session[exp_id])

    exp.record_audio_play_time()
    exp.commit(session)

    return "OK"

@app.route('/view_words_click')
@requires_experiment_id
@cross_origin()
def view_words_click():
    exp_id = session[CURRENT_EXP]
    exp = Experiment.from_json(session[exp_id])
    
    exp.record_view_words_click_time()
    exp.commit(session)

    return "OK"

WORDLIST = utils.load_wordlist(f"{BASE_FILE_LOCATION}data/{WORDLIST_NAME}")

if __name__ == "__main__":
    app.run()
