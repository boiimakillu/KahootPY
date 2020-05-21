from pymitter import EventEmitter
from .src import token
from .src import Assets
from .src import WSHandler
from .src import ChallengeHandler
from .src import consts

class client(EventEmitter):
    def __init__(self,proxies,options):
        self._wsHandler = None
        self.token = None
        self.sessionID = None
        self.name = None
        self.team = []
        self.quiz = None
        self.totalScore = 0
        self.gamemode = None
        self.hasTwoFactorAuth = False
        self.usesNamerator = False
        self.cid = ""
        self.proxies = proxies
        self.loggingMode = False
        self.joined = False
        self.options = {
            ChallengeAutoContinue: True,
            ChallengeGetFullScore: False
        }.update(options)
    async def reconnect():
        if self.sessionID and this.cid and this._wsHandler and this._wsHandler.ws.open:
            if self.sessionID[0] == "0":
                return False
            try:
                content = await token.resolve(self.sessionID,self.proxies)
            except ConnectError:
                return False
            self.gamemode = content.gamemode or "classic"
            self.hasTwoFactorAuth = content.hasTwoFactorAuth or False
            self.usesNamerator = content.namerator or False
            self.token = content.resolvedToken
            self._wsHandler = WSHandler(self.sessionID,self.token,self)
            _defineListeners(self,self._wsHandler)
            return True
    async def join(pin,name,team):
        if not pin or not name:
            return False
        self.sessionID = pin
        self.name = name
        self.team = team
        try:
            content = await token.resolve(self.sessionID,self.proxies)
        except ConnectError:
            return False
        self.gamemode = content.gamemode or "classic"
        self.hasTwoFactorAuth = content.hasTwoFactorAuth or False
        self.usesNamerator = content.namerator or False
        self.token = content.resolvedToken
        self._wsHandler = WSHandler(self.sessionID,self.token,self)
        _defineListeners(self,self._wsHandler)
    async def answer2Step(steps):
        await self._wsHandler.send2Step(steps)
    async def answerQuestion(id,question,secret):
        if not question:
            question = self.quiz.currentQuestion
        self._wsHandler.sendSubmit(id,question,secret)
    async def leave():
        await self._wsHandler.leave()
    async def sendFeedback(fun=1,learning=1,recommend=1,overall=5):
        await self._wsHandler.sendFeedback(fun,learning,recommend,overall)
    def next():
        if self.gamemode == "challenge":
            self._wsHandler.next()
            return True
        return False
def _defineListeners(client,socket):
    def errorHandle(e):
        client.emit("handshakeFailed",e)
    def invalidNameHandle():
        client.emit("invalidName")
    def TwoFailHandle():
        client.emit("2StepFail")
    def TwoSuccessHandle():
        client.emit("2StepSuccess")
    def TwoHandle():
        client.emit("2Step")
    def ReadyHandle():
        client.login(client.name,client.team)
    def JoinHandle():
        client.emit("ready")
        client.emit("joined")
        if client.hasTwoFactorAuth:
            client.emit("2Step")
    def QuizDataHandle(quizInfo):
        client.quiz = Assets.Quiz(quizInfo.name,quizInfo.type,quizInfo.qCount,client,quizInfo.totalQ,quizInfo.quizQuestionAnswers,quizInfo)
        client.emit("quizStart")
        client.emit("quiz")
    def QuizUpdateHandle(updateInfo):
        client.quiz.currentQuestion = Assets.Question(updateInfo,client)
        client.emit("question",client.quiz.currentQuestion)
    def QuestionEndHandle(endInfo):
        e = Assets.QuestionEndEvent(endInfo,client)
        client.totalScore = e.total
        client.emit("questionEnd",e)
    def QuizEndHandle():
        client.emit("quizEnd")
        client.emit("disconnect")
    def QuestionStartHandle():
        try:
            client.emit("questionStart",client.quiz.currentQuestion)
        except JoinMidGameError as e:
            # likely joined during quiz
            pass
    def QuestionSubmitHandle(message):
        e = Assets.QuestionSubmitEvent(message,client)
        client.emit("questionSubmit",e)
    def FinishTextHandle(data):
        e = Assets.FinishTextEvent(data)
        client.emit("finishText",e)
    def FinishHandle(data):
        e = Assets.QuizFinishEvent(data,client)
        client.emit("finish",e)
    def FeedbackHandle():
        client.emit("feedback")
    socket.on("error",errorHandle)
    socket.on("invalidName",invalidNameHandle)
    socket.on("2StepFail",TwoFailHandle)
    socket.on("2StepSuccess",TwoSuccessHandle)
    socket.on("2Step",TwoHandle)
    socket.on("ready",ReadyHandle)
    socket.on("joined",JoinHandle)
    socket.on("quizData",QuizDataHandle)
    socket.on("quizUpdate",QuizUpdateHandle)
    socket.on("questionEnd",QuestionEndHandle)
    socket.on("quizEnd",QuizEndHandle)
    socket.on("questionStart",QuestionStartHandle)
    socket.on("questionSubmit",QuestionSubmitHandle)
    socket.on("finishText",FinishTextHandle)
    socket.on("finish",FinishHandle)
    socket.on("feedback",FeedbackHandle)
