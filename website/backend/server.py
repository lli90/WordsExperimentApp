from flask import Flask, request, send_from_directory, render_template, session
from flask_sqlalchemy import SQLAlchemy
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
import json
import collections
from urllib.parse import urlparse

from config import BASE_FILE_LOCATION
import attack
import utils
import logging
import polly_numbers
from mutagen.mp3 import MP3


logging.basicConfig(
    filename='backend.log',
    filemode='a',
    format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s'
)

METHOD_NOT_ALLOWED = "Error: Method not allowed"
EXPERIMENT_NOT_FOUND = "Error: Experiment ID not found"

ALLOWED_TRIAL_TYPES = ["/visual", "/verbal"]

app = Flask(__name__, static_folder="./build/static",
            template_folder="./build/")

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///experiment.db"
app.secret_key = secrets.token_urlsafe(64)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='None',
)

app.logger.setLevel(logging.DEBUG)

db = SQLAlchemy(app)

from models import *

WORDLIST_NAME = "trustwords.csv"

def requires_experiment_id(f):
    @wraps(f)

    def decorated_function(*args, **kwargs):

        if request.method != "GET":
            app.logger.debug(f"Invalid request method: {request.method}")
            return METHOD_NOT_ALLOWED, 405

        exp_id = session.get(get_referring_endpoint(request))

        if exp_id == None:
            app.logger.debug(f"Experiment ID was not found")
            return EXPERIMENT_NOT_FOUND, 400

        session["current_exp"] = exp_id

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
        app.logger.debug(f"Invalid trialType extracted: {trialType} - {request.referrer}")
        raise Exception(f"Invalid trialType provided. Referrer string: \"{request.referrer}\"")

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

    app.logger.debug(f"Generating audio file for: {str(words)}")

    filepath = polly_numbers.get_audio_clip(words)

    duration = MP3(filepath).info.length

    return filepath.split("/")[-1], duration

def get_experiment_from_db(exp_id):
    return Experiment.query.filter_by(guid=exp_id).first()

def save_exp_to_json(exp):
    """
    Saves an experiment model to JSON
    """

    def iterable(arg):
        return (
            isinstance(arg, collections.Iterable)
            and not isinstance(arg, str)
        )

    variables = []
    for v in dir(exp):
        if not callable(getattr(exp, v)) and not v.startswith("_"):
            variables.append(v)

    variables.remove("query")
    variables.remove("metadata")
    variables.remove("registry")


    json_out = {}
    for v in variables:

        var = exp.__dict__[v]

        # If iterable
        if iterable(var):

            val = []
            for x in var:
                val.append(str(x))
        # If not iterable
        else:
            val = var

        json_out.update({v: val})

    filePath = f"{BASE_FILE_LOCATION}results/{str(exp.trialType)}-{str(exp.guid)}.json"

    with open(filePath, 'w') as f:
        f.write(json.dumps(json_out))

@app.after_request
def after_request(response):
    """
    Code performed after the request
    """

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Credentials
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Server'] = 'nginx'
    return response

def finish_experiment(exp):
    app.logger.debug("Experiment has finished!")
    exp.end_experiment()
    save_exp_to_json(exp)
    #delete the server side session.  If left session[trial_type] remains defined (via the cookie?)
    session.clear()

    return "DONE"

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
    exp_id = session["current_exp"]
    exp = get_experiment_from_db(exp_id)

    if exp.is_finished():
        return finish_experiment(exp)

    exp.increment_audio_clicks()
    exp.record_audio_button_click_time()

    # Checks for an attack case
    if exp.is_attack():
        app.logger.debug("Attack round!")
        words = exp.get_current_attack_wordlist()
    else:
        words = exp.get_current_wordlist()

    filename, fileDuration = generate_audio_file(words)

    exp.record_audio_clip_length(fileDuration)

    return send_from_directory(f'{BASE_FILE_LOCATION}audio/generated', filename)

@app.route('/get_visual')
@requires_experiment_id
@cross_origin()
def get_visual_attack_words():
    """
    Gets the set of possible attack words for the visual trial
    """

    exp_id = session["current_exp"]
    exp = get_experiment_from_db(exp_id)

    if exp.is_finished():
        return finish_experiment(exp)

    if not exp.check_if_round_started():
        exp.record_round_start_time()

    attackWordlist = exp.get_current_attack_wordlist()

    if attackWordlist != ["NULL"]:
        app.logger.debug(f"Word: {attackWordlist}")
        return "\n".join(attackWordlist)
    else:
        app.logger.debug(f"Word: {exp.get_current_wordlist()}")
        return "\n".join(exp.get_current_wordlist())

@app.route('/get_words')
@requires_experiment_id
@cross_origin()
def get_words():
    """
    Gets the currently active set of words. This is the non-attack set
    """
    exp_id = session["current_exp"]
    exp = get_experiment_from_db(exp_id)

    if exp.is_finished():
        return finish_experiment(exp)

    if not exp.check_if_round_started():
        exp.record_round_start_time()

    return "\n ".join(exp.get_current_wordlist())

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

    similarity_type = query_params.get("SimType")

    if similarity_type:
        similarity_type = similarity_type[0]

    app.logger.debug(f"initial similarity_type: {similarity_type}.")

    if similarity_type != 'phon' and similarity_type != 'orth':
        similarity_type = 'phon'

    # If they're included the program will add
    participant_id = query_params.get("Participant_id")
    if participant_id:
        participant_id = participant_id[0]

    recruit_source = query_params.get("RecruitSource")
    if recruit_source:
        recruit_source = recruit_source[0]

    app.logger.debug(f"Participant ID: {participant_id}.")
    app.logger.debug(f"similarity_type: {similarity_type}.")
    app.logger.debug(f"Recruitment Source: {recruit_source}.")

    user_agent = request.headers.get("User-Agent")

    exp_id = str(uuid.uuid4())
    app.logger.debug(f"Experiment found: {exp_id} - {trialType}")

    session[trialType] = exp_id

    exp = Experiment(exp_id, user_agent, trialType, similarity_type, participant_id, recruit_source)
    utils.gen_word_set(WORDLIST, exp, similarity_type)

    return exp_id

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

    exp_id = session["current_exp"]
    exp = get_experiment_from_db(exp_id)

    exp.record_response(result)
    exp.record_round_end_time()
    exp.move_to_next_round()

    return "OK"

@app.route('/audio_playing')
@requires_experiment_id
@cross_origin()
def audio_playing():
    """
    Endpoint contacted when the audio for the verbal trial begins playing
    """

    exp_id = session["current_exp"]
    exp = get_experiment_from_db(exp_id)

    exp.record_audio_play_time()

    return "OK"

@app.route('/view_words_click')
@requires_experiment_id
@cross_origin()
def view_words_click():
    exp_id = session["current_exp"]
    exp = get_experiment_from_db(exp_id)

    exp.record_view_words_click_time()

    return "OK"

WORDLIST = utils.load_wordlist(f"{BASE_FILE_LOCATION}data/{WORDLIST_NAME}")

if __name__ == "__main__":
    app.run()
