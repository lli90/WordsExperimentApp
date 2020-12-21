import time
from config import BASE_FILE_LOCATION
import json


class Experiment:
    """
    Experiment object.

    Current values:

        TrialType
            - Type of trial. Currently either "visual" or "verbal".

        CurrentRound
            - An internal variable used to represent the current round

        ExperimentID
            - GUID used to link to a user

        VisualWords
            - The words presented to the user

        Responses
            - Answers provided by the user

        AttackWords
            - If the element is not equal to "None" the index is the set of attack words presented visually or verbally.

        AudioButtonClicks
            - How many times the audio button was clicked in each round

        AudioButtonTimes
            - Timestamps of every audio button click

        StartTime
            - Start time of the entire experiment

        RoundStartTimes
            - Start time for each round

        RoundEndTimes
            - End time for each round

        EndTime
            - End time of the entire experiment

        UserAgent
            - User agent of the particpant

        IsMTurk
            - Analytical variable for MTurk participants

        ParticipantID
            - Participant ID. This is designed to be passed from Quartics.

    """

    def __init__(self, experimentID, userAgent, trialType, participantID=None, isMTurk=None):

        self.CurrentRound = 0

        self.TrialType = trialType
        self.ExperimentID = experimentID
        self.VisualWords = []
        self.Responses = []

        self.AttackWords = []
        self.AudioButtonClicks = []
        self.AudioButtonTimes = []

        self.StartTime = time.time()
        self.RoundStartTimes = []
        self.RoundEndTimes = []
        self.EndTime = None

        self.UserAgent = userAgent

        self.IsMTurk = isMTurk
        self.ParticipantID = participantID


    def commit(self, session):
        session[self.ExperimentID] = self.to_json()

    def move_to_next_round(self):
        self.CurrentRound += 1

    def add_round(self, round):
        self.VisualWords.append(round.getWords())
        self.AttackWords.append(round.getAttackWords())
        self.AudioButtonClicks.append(0)

    def record_response(self, response):
        self.Responses.append(response)

    def record_round_start_time(self):
        self.RoundStartTimes.append(time.time())

    def record_round_end_time(self):
        self.RoundEndTimes.append(time.time())

    def get_round_number(self):
        return self.CurrentRound

    def get_current_wordlist(self):
        return self.VisualWords[self.CurrentRound]

    def get_current_respose(self):
        return self.Responses[self.CurrentRound]

    def get_current_attack_wordlist(self):
        return self.AttackWords[self.CurrentRound]

    def increment_audio_clicks(self):
        self.AudioButtonClicks[self.CurrentRound] += 1

    def record_audio_button_click_time(self):
        t = time.time()

        if len(self.AudioButtonTimes) > self.CurrentRound:
            self.AudioButtonTimes[self.CurrentRound].append(t)
        else:
            self.AudioButtonTimes.append([t])

    def is_attack(self):
        return self.AttackWords[self.CurrentRound] != None

    def check_if_round_started(self):
        return not self.CurrentRound >= len(self.RoundStartTimes)

    def end_experiment(self):
        self.EndTime = time.time()
        self.save()
    
    def to_json(self):
        return self.__dict__

    def save(self):
        with open(f"{BASE_FILE_LOCATION}results/{self.TrialType}-{self.ExperimentID}.json", "w") as f:
            f.write(json.dumps(self.to_json()))

    @staticmethod
    def from_json(dictionary):
        
        exp = Experiment(None, None, None)

        exp.TrialType           = dictionary["TrialType"]
        exp.CurrentRound        = dictionary["CurrentRound"]
        exp.ExperimentID        = dictionary["ExperimentID"]
        exp.VisualWords         = dictionary["VisualWords"]
        exp.Responses           = dictionary["Responses"]
        exp.AttackWords         = dictionary["AttackWords"]
        exp.AudioButtonClicks   = dictionary["AudioButtonClicks"]
        exp.AudioButtonTimes    = dictionary["AudioButtonTimes"]
        exp.StartTime           = dictionary["StartTime"]
        exp.RoundStartTimes     = dictionary["RoundStartTimes"]
        exp.RoundEndTimes       = dictionary["RoundEndTimes"]
        exp.EndTime             = dictionary["EndTime"]
        exp.UserAgent           = dictionary["UserAgent"]
        exp.IsMTurk             = dictionary["IsMTurk"]
        exp.ParticipantID       = dictionary["ParticipantID"]

        return exp