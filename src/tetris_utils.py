from recordclass import recordclass
Stack = recordclass('Stack', 'timer lines')

# class fire is a data structure representing how many lines will be added to the current field at how many steps from the current step
# steps count once when a mino lands
class fire:
    def __init__(self):
        self.stacks = []
    def __repr__(self):
        ret = ''
        for stack in self.stacks:
            ret += 'timer: %r lines: %r\n' % (stack.timer, stack.lines)
        return ret
    
    def __len__(self):
        return sum([stack.lines for stack in self.stacks])

    def add(self, num):
        self.stacks.append(Stack(timer=5, lines=num))

    # decrement every timer and remove the stack whose timer is 0
    # return the number of lines which are about to added to field
    def countdown(self):
        numLines = 0
        for stack in self.stacks:
            stack.timer -= 1
            if stack.timer == 0:
                numLines += stack.lines
        
        self.stacks = [stack for stack in self.stacks if stack.timer > 0]
        return numLines
    # return number of fires remaining
    # return 0 if sending fire number is less than accumulated fire
    def subtract(self, num):
        for stack in self.stacks:
            if stack.lines < num:
                stack.lines -= num
                num = -1 * stack.lines
            else:
                stack.lines -= num
                num = 0
                break
        # remove stack whose lines is <= 0
        self.stacks = [stack for stack in self.stacks if stack.lines > 0]

        return num