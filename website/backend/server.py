from flask import Flask, request, send_from_directory, render_template, session
from flask_cors import cross_origin
from pydub import AudioSegment
import random
import itertools
import uuid
import time
import secrets
import os
import urllib

from config import BASE_FILE_LOCATION 
from experiment import Experiment
import attack
import utils

METHOD_NOT_ALLOWED = "Error: Method not allowed"
EXPERIMENT_NOT_FOUND = "Error: Experiment ID not found"

ALLOWED_TRIAL_TYPES = ["visual", "verbal"]

app = Flask(__name__, static_folder="./build/static",
            template_folder="./build/")

app.secret_key = secrets.token_urlsafe(64)

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='None',
)


WORDLIST_NAME = "trustwords.csv"

def get_referring_endpoint(request):
    referrer_last = request.referrer.split("/")[-1]
    trialType = referrer_last.split("?")[0]

    # Just to stop rnd stuff being passed into the session
    # dictionary
    if not trialType in ALLOWED_TRIAL_TYPES:
        raise Exception(f"Invalid trialType provided. Referer string: \"{request.referrer}\"")

    return trialType

def get_reffering_query_params(request):
    query_str = request.referrer.split("?")[-1]
    return urllib.parse.parse_qs(query_str)

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    return response

# This is used to fix Flask's compatability with the react-routing
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_audio')
@cross_origin()
def get_audio():
    """
    Gets the currently active audio file
    """

    if request.method != "GET":
        return METHOD_NOT_ALLOWED, 400

    exp_id = session.get(get_referring_endpoint(request))

    if not exp_id in session:
        return EXPERIMENT_NOT_FOUND, 400

    exp = Experiment.from_json(session[exp_id])

    if utils.experiment_finished(exp_id):
        exp.end_experiment()
        session[exp_id] = exp.to_json()

        # TODO: Make more unique
        return "DONE"

    # Increments and saves changes
    exp.increment_audio_clicks()
    exp.record_audio_button_click_time()
    session[exp_id] = exp.to_json()

    # Checks for an attack case
    if exp.is_attack():
        words = exp.get_current_attack_wordlist()
    else:
        words = exp.get_current_wordlist()

    filePath = f"{BASE_FILE_LOCATION}audio/generated/{'_'.join(words)}.mp3"
    if not os.path.isfile(filePath):

        combined = AudioSegment.from_mp3(
            f"{BASE_FILE_LOCATION}audio/{words[0].upper()}.mp3")

        for w in words[1:]:
            a = AudioSegment.from_mp3(
                f"{BASE_FILE_LOCATION}audio/{w.upper()}.mp3")
            combined += a

        combined.export(filePath, format="mp3")

    return send_from_directory(f'{BASE_FILE_LOCATION}audio/generated', filePath.split("/")[-1])

@app.route('/get_visual')
@cross_origin()
def get_visual_attack_words():
    """
    Gets the set of possible attack words for the visual trial
    """

    if request.method != "GET":
        return METHOD_NOT_ALLOWED, 400
        
    exp_id = session.get(get_referring_endpoint(request))

    if not exp_id in session:
        return EXPERIMENT_NOT_FOUND, 400

    exp = Experiment.from_json(session[exp_id])

    if utils.experiment_finished(exp_id):

        exp.end_experiment()
        session[exp_id] = exp.to_json()

        # TODO: Make more unique. Put in a global variable
        return "DONE"

    if not exp.check_if_round_started():
        exp.record_round_start_time()
        session[exp_id] = exp.to_json()

    attackWordlist = exp.get_current_attack_wordlist()

    if attackWordlist:
        return " ".join(attackWordlist)
    else:
        return " ".join(exp.get_current_wordlist())

@app.route('/get_words')
@cross_origin()
def get_words():
    """
    Gets the currently active set of words. This is the non-attack set
    """
    
    if request.method != "GET":
        return METHOD_NOT_ALLOWED, 400

    exp_id = session.get(get_referring_endpoint(request))

    if not exp_id in session:
        return EXPERIMENT_NOT_FOUND, 400

    exp = Experiment.from_json(session[exp_id])

    if utils.experiment_finished(exp_id):

        exp.end_experiment()
        session[exp_id] = exp.to_json()

        # TODO: Turn this into a more unique string
        return "DONE"

    if not exp.check_if_round_started():
        exp.record_round_start_time()
        session[exp_id] = exp.to_json()

    return "  ".join(Experiment.from_json(session[exp_id]).get_current_wordlist())

@app.route("/get_id")
@cross_origin()
def get_id():
    trialType = get_referring_endpoint(request)
    # return session.get(trialType)
    return "DEPRECATED"

@app.route('/new_experiment')
@cross_origin()
def new_experiment():
    """
    This end point is designed to initialise the experiment attached to a certain ID
    """

    trialType = get_referring_endpoint(request)

    if not trialType:
        return "Missing \'type\' parameter!", 400

    query_params = get_reffering_query_params(request)
    
    participant_id = query_params.get("Participant_id")
    is_mturk = query_params.get("MTurk")

    if not session.get(trialType):

        user_agent = request.headers.get("User-Agent")

        exp_id = str(uuid.uuid4())

        session[trialType] = exp_id
        session[exp_id] = Experiment(exp_id, user_agent, trialType, participant_id, is_mturk).to_json()

        exp = Experiment.from_json(session[exp_id])
        utils.gen_word_set(WORDLIST, exp)
        session[exp_id] = exp.to_json()

        return exp_id 

    return session.get(trialType)

@app.route('/submit_result')
@cross_origin()
def submit_result():
    """
    Endpoint used to submit the user's response

    Required params:

    'result' should be "ACCEPT" or "DECLINE"
    """

    if not request.method == "GET":
        return METHOD_NOT_ALLOWED, 400

    result = request.args.get("result", None)

    if not result:
        return "Error: Missing parameter \'result\'", 400

    if not result in ["True", "False"]:
        return f"Error: Invalid value \"{result}\" for result", 400

    exp_id = session.get(get_referring_endpoint(request))

    if not exp_id in session:
        return "Error: No experiment found!", 400

    exp = Experiment.from_json(session[exp_id])
    exp.record_response(result)
    exp.record_round_end_time()
    exp.move_to_next_round()
    session[exp_id] = exp.to_json()

    # TODO: More unique response?
    return "OK"


WORDLIST = utils.load_wordlist(f"{BASE_FILE_LOCATION}data/{WORDLIST_NAME}")

if __name__ == "__main__":
    app.run()
