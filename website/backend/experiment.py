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

        AudioButtonClickTimes
            - Timestamps of when the audio button is clicked by the particpant

        AudioPlayTimes
            - Timestamps of when the audio actually starts playing. 
            
              The audio element on the frontend will speak to
              the backend when the `onLoaded` event is triggered

        AudioClipDurations
            - Length in milliseconds of the generated audio clip

        ViewWordsClicks
            - Timestamp of when the "View words" button is clicked by the participant

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
        self.AudioButtonClickTimes = []
        self.AudioPlayTimes = []
        self.AudioClipDurations = []

        self.ViewWordsClicks = []

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

        if len(self.AudioButtonClickTimes) > self.CurrentRound:
            self.AudioButtonClickTimes[self.CurrentRound].append(t)
        else:
            self.AudioButtonClickTimes.append([t])

    def record_audio_play_time(self):
        """
        Records the time when the audio begins to play.
        """
        t = time.time()

        if len(self.AudioPlayTimes) > self.CurrentRound:
            self.AudioPlayTimes[self.CurrentRound].append(t)
        else:
            self.AudioPlayTimes.append([t])

    def record_view_words_click_time(self):
        """
        Records when the "View words" button is clicked
        """
        self.ViewWordsClicks.append(time.time())

    def record_audio_clip_length(self, length):
        if len(self.AudioClipDurations) < self.CurrentRound:
            self.AudioClipDurations.append(length)

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
    def __vars__():
        """
        Gets a list of all of the variables available in the object
        """

        variables = []
        exp = Experiment(None, None, None)
        for v in dir(exp):
            if not callable(getattr(exp, v)) and not v.startswith("__"):
                variables.append(v)

        return variables

    @staticmethod
    def from_json(dictionary):
        """
        Loads a json dictionary into the class
        """

        variables = Experiment.__vars__()
        
        exp = Experiment(None, None, None)

        for v in variables:
            exp.__dict__[v] = dictionary[v]

        return exp