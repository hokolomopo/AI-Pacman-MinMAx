# Complete this class for all parts of the project

from pacman_module.game import Agent
from pacman_module.pacman import Directions
from math import inf as INF

class PacmanAgent(Agent):
    def __init__(self, args):
        """
        Arguments:
        ----------
        - `args`: Namespace of arguments from command-line prompt.
        """
        self.args = args
        self.visited = {}
        self.exp = 0
        self.pru = 0
        self.recCall = 0

    def get_action(self, state):
        """
        Given a pacman game state, returns a legal move.

        Arguments:
        ----------
        - `state`: the current game state. See FAQ and class
                   `pacman.GameState`.

        Return:
        -------
        - A legal move as defined in `game.Directions`.
        """

        action = self.minimax(state)
        print(self.exp, self.pru, self.recCall)

        return action

    def minimax(self, state):
        max = -INF
        action = Directions.STOP

        interval=[-INF,+INF]
        for s in state.generatePacmanSuccessors():

            minimax = self.minimaxrec(s[0], 1, 0, parentInterval=interval)
            self.updateInterval(interval, minimax, 0)
            if minimax != None and minimax > max : 
                max = minimax
                action = s[1]

        return action


    def minimaxrec(self, state, player, dpt=0, parentInterval=[-INF,+INF],
            lastPacmanMove=None, lastGhostMove=None):
        if state.isWin() or state.isLose():
            return state.getScore()  

        currentStateHash = self.hash_state(state, player, lastGhostMove, lastPacmanMove)

        if currentStateHash in self.visited:
            visitedNode = self.visited[currentStateHash]

            # Visited is a parent
            if visitedNode == None :
                return None

            #Visited in another branch
            dptDif = state.getScore() - visitedNode.currScore
            return visitedNode.score + dptDif
        self.recCall += 1

        successors = self.generateSuccessors(state, player, lastPacmanMove)
        
        sol = []
        self.visited[currentStateHash] = None

        interval=[-INF,+INF]

        pruned = False

        for s in successors:
            newState = s[0]
            if(player == 0):
                minimax = self.minimaxrec(newState, self.getNextPlayer(player) \
                 , dpt+1, interval, s[1], lastGhostMove)
            else :
                minimax = self.minimaxrec(newState, self.getNextPlayer(player) \
                 , dpt+1, interval, lastPacmanMove, s[1])
            if minimax is not None:
                sol.append(minimax)
                if self.shouldStop(minimax, parentInterval, player):
                    self.pru +=1
                    pruned = True
                    break
                self.updateInterval(interval, minimax, player)

        best = self.getBest(sol, player)

        if pruned or best == None:
            del self.visited[currentStateHash]
        elif best != None:
            self.exp +=1
            self.visited[currentStateHash] = Node(dpt, best, state.getScore())
        return best


    def shouldStop(self, minimax, interval, player):
        if player == 0:
            if minimax >= interval[1]:
                return True
            return False
        else:
            if minimax <= interval[0]:
                return True
            return False

    def updateInterval(self,interval, minimax, player):
        if player == 0:
            interval[0] = max(minimax, interval[0])
        else:
            interval[1] = min(minimax, interval[1])


    def generateSuccessors(self, state, player, lastMove=None):
        if player == 0:
            nextStates = state.generatePacmanSuccessors()
            if lastMove == None:
                return nextStates
            if self.canPacmanStop(nextStates, lastMove):
                nextStates.append((state, Directions.STOP))
            return nextStates
        else :
            return state.generateGhostSuccessors(1)

    def canPacmanStop(self, successors, lastPacmanMove):
        if len(successors) > 3:
            return False
        if lastPacmanMove == Directions.STOP:
            return True
        x = [item for item in successors if item[1] == lastPacmanMove]
        if len(x) == 0:
            return True
        return False


    def getBest(self, solutions, player):
        if len(solutions) == 0:
            return None
        if player == 0:
            return max(solutions)
        else :
            return min(solutions)


    def getNextPlayer(self, player):
        if player == 0:
            return 1
        else:
            return 0

    def hash_state(self, state, player, lastGhostMove):
        return (hash(state.getPacmanPosition()), hash(state.getGhostPositions()[0]),
            hash(state.getFood()), player, lastGhostMove)

class Node:
    def __init__(self, dpt, score, currScore=0):
        self.dpt = dpt
        self.score = score
        self.currScore = currScore

