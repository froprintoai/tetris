from collections import namedtuple

Stack = namedtuple('Stack', ['timer', 'lines'])

class fire:
    def __init_(self):
        self.stacks = []
    def add(self, num):
        self.stacks.append(Stack(timer=5, lines=num))
    def count(self):
        numLines = 0
        for stack in self.stacks:
            stack.timer -= 1
            if stack.timer == 0:
                numLines += stack.lines
        return numLines