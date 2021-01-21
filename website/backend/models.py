from sqlalchemy.ext.declarative import declared_attr
import time

from server import db
from config import NUMBER_OF_ROUNDS 

class Experiment(db.Model):

    """
    Unique experiment GUID
    """
    guid = db.Column(db.String(50), primary_key=True)

    """
    Type of trial. Currently either "visual" or "verbal".
    """
    trialType = db.Column(db.String(20))

    """
    An internal variable used to represent the current round
    """
    currentRound = db.Column(db.Integer)

    """
    The words presented to the user
    """
    visualWords = db.relationship('VisualWords', backref='experiment')

    """
    Answers provided by the user
    """
    userResponses = db.relationship('Response', backref='experiment')

    """
    The wrong words presented to the user in either a visual or verbal form
    If the element is not equal to "None" the index is the set of attack words presented visually or verbally.
    """
    attackWords = db.relationship('AttackWords', backref='experiment')

    """
    How many times the audio button was clicked in each round
    """
    audioButtonClicks = db.relationship('AudioClickTimes', backref='experiment')

    """
    Timestamps of when the audio button is clicked by the particpant
    """
    audioButtonClickTimes =  db.relationship('AudioButtonClickTimes', backref='experiment')

    """
    Timestamps of when the audio actually starts playing. 
    The audio element on the frontend will speak to
    the backend when the `onLoaded` event is triggered
    """
    audioPlayTimes = db.relationship('AudioPlayTimes', backref='experiment')

    """
    Length in milliseconds of the generated audio clip
    """
    audioClipDurations = db.relationship('AudioClipDurations', backref='experiment')

    """
    Timestamp of when the "View words" button is clicked by the participant
    """
    viewWordsClicks = db.relationship('ViewWordsClicks', backref='experiment')

    """
    Start time of the entire experiment
    """
    startTime = db.Column(db.String(20))

    """
    End time of the entire experiment
    """
    endTime = db.Column(db.String(20))

    """
    Start time for each round
    """
    roundStartTimes = db.relationship('RoundStartTimes', backref='experiment')

    """
    End time for each round
    """
    roundEndTimes = db.relationship('RoundEndTimes', backref='experiment')

    """
    User agent of the particpant
    """
    userAgent = db.Column(db.String(100))

    """
    Analytical variable for MTurk participants
    """
    isMTurk = db.Column(db.String(10), default=False)

    """
    Participant ID. This is designed to be passed from Quartics.
    """
    participantID = db.Column(db.String(100), default="")

    def __init__(self, experimentID, userAgent, trialType, participantID=False, isMTurk=False):

        self.currentRound = 0
        # self.trialType = trialType
        self.guid = experimentID

        self.trialType = trialType

        self.startTime = str(time.time())
        self.userAgent = userAgent

        self.isMTurk = isMTurk
        self.participantID = participantID

    def _word_to_list(self, words):
        return str(words).split(";")

    def is_finished(self):
        return self.currentRound >= NUMBER_OF_ROUNDS

    def move_to_next_round(self):
        self.currentRound += 1
        db.session.commit()

    def add_round(self, round):

        db.session.add(
            VisualWords(round.getWords(), experiment=self)
        )

        db.session.add(
            AttackWords(round.getAttackWords(), experiment=self)
        )

        db.session.add(
            AudioClickTimes(count=0, experiment=self)
        )

        db.session.commit()

    def record_response(self, response):

        db.session.add(
            Response(result=response, experiment=self)
        )

        db.session.commit()

    def record_round_start_time(self):

        db.session.add(
            RoundStartTimes(value=time.time(), experiment=self)
        )

        db.session.commit()

    def record_round_end_time(self):
        db.session.add(
            RoundEndTimes(value=time.time(), experiment=self)
        )

        db.session.commit()

    def get_round_number(self):
        return self.currentRound

    def get_current_wordlist(self):
        return self._word_to_list(self.visualWords[self.currentRound])

    def get_current_respose(self):
        return self._word_to_list(self.responses[self.currentRound])

    def get_current_attack_wordlist(self):
        return self._word_to_list(self.attackWords[self.currentRound])

    def increment_audio_clicks(self):
        self.audioButtonClicks[self.currentRound].count += 1
        db.session.commit()

    def record_audio_button_click_time(self):
        t = time.time()

        if len(self.audioButtonClickTimes) > self.currentRound:
            self.audioButtonClickTimes[self.currentRound].append(t)
        else:
            db.session.add(
                AudioButtonClickTimes(value=t, experiment=self)
            )

        db.session.commit()

    def record_audio_play_time(self):
        """
        Records the time when the audio begins to play.
        """
        t = time.time()

        if len(self.audioPlayTimes) > self.currentRound:
            self.audioPlayTimes[self.currentRound].append(t)
        else:
            db.session.add(
                AudioPlayTimes(value=t, experiment=self)
            )

        db.session.commit()

    def record_view_words_click_time(self):
        """
        Records when the "View words" button is clicked
        """
        db.session.add(
            ViewWordsClicks(value=time.time(), experiment=self)
        )

        db.session.commit()

    def record_audio_clip_length(self, clip_length):
        """
        TODO
        """
        if len(self.audioClipDurations) <= self.currentRound:

            db.session.add(
                AudioClipDurations(value=clip_length, experiment=self)
            )

            db.session.commit()

    def is_attack(self):
        return self.attackWords[self.currentRound].value != "NULL"

    def check_if_round_started(self):
        return not self.currentRound >= len(self.roundStartTimes)

    def end_experiment(self):

        self.endTime = str(time.time())

        db.session.commit()
        #TODO: Save to file

class StringCollection(db.Model):
    """
    Collection of generic strings
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    
    value = db.Column(db.String(20))

    def append(self, i):
        self.value += f";{i}"

    @declared_attr
    def experiment_id(cls):
        return db.Column(db.Integer, db.ForeignKey('experiment.guid'))

    def __repr__(self):
        return str(self.value)

class WordCollection(StringCollection):
    """
    Collection of words
    """
    __abstract__ = True

    def __init__(self, word_list, **kwargs):
        super().__init__(**kwargs)
        self.value = self._from_list(word_list)

    def _from_list(self, l):
        return ";".join(l)

    def _to_list(self):
        return self.value.split(";")

# String collections
class VisualWords(WordCollection):
    pass

class AttackWords(WordCollection):

    def __init__(self, word_list, **kwargs):    

        if word_list == None:
            word_list = ["NULL"]

        super().__init__(word_list, **kwargs)
        

class AudioButtonClickTimes(StringCollection):
    pass

class AudioPlayTimes(StringCollection):
    pass

class AudioClipDurations(StringCollection):
    pass

class ViewWordsClicks(StringCollection):
    pass

class RoundStartTimes(StringCollection):
    pass

class RoundEndTimes(StringCollection):
    pass

class Count(db.Model):
    """
    A variable containing a count
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    count = db.Column(db.Integer)

    @declared_attr
    def experiment_id(cls):
        return db.Column(db.Integer, db.ForeignKey('experiment.guid'))

    def __repr__(self):
        return str(self.count)

# Count models
class AudioClickTimes(Count):
    pass

class Response(db.Model):
    """
    True or False user response
    """

    id = db.Column(db.Integer, primary_key=True)

    result = db.Column(db.String(5))

    experiment_id = db.Column(
        db.Integer, 
        db.ForeignKey('experiment.guid')
    )

    def __repr__(self):
        return str(self.result)
