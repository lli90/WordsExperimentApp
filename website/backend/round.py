class Round:

    _words = []
    _attackWords = []

    def __init__(self, words, attackWords=None):
        self._words = words
        self._attackWords = attackWords

    def getWords(self):
        return self._words

    def getAttackWords(self):
        return self._attackWords

    def isAttackRound(self):
        return self._attackWords != None