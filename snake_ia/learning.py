import os
import numpy as np
from argparse import ArgumentParser

# snake
# ----------------------------------------------
class Snake:
    def __init__(self, s=40):
        self.s = s
        self.pos = (rd(s), rd(s))
        self.body = [self.pos]
        self.create_apple()
        self.find_relative_pos()
        self.is_dead = False
        self.life = 500 # snake's life 
        
        self.actions = [
                        [-1, 0], # Left
                        [0, -1], # Up
                        [1, 0], # Right
                        [0, 1] #Down
                        ]
    
    def create_apple(self):
        apple_pos = (rd(self.s), rd(self.s))
        while apple_pos in self.body:
            apple_pos = (rd(self.s), rd(self.s))
        self.apple = apple_pos
    
    def move(self):
        if self.pos == self.apple:
            self.create_apple()
        else:
            self.body.pop()
        self.body.insert(0,self.pos)
    
    def take_action(self, st, epsilon=0):
        if np.random.random_sample() < epsilon:
            #select a random action
            return np.random.randint(4)
        else:
            # exploit action from Q_table
            global Q_table
            return np.argmax(Q_table, axis=1)[st]
    
    def relative_reward(self, at):
        if at == 0 and (self.r_pos == 0 or self.r_pos == 3 or self.r_pos == 5):
            return 10
        elif at == 1 and (self.r_pos == 0 or self.r_pos == 1 or self.r_pos == 2):
            return 10
        elif at == 2 and (self.r_pos == 2 or self.r_pos == 4 or self.r_pos == 7):
            return 10
        elif at == 3 and (self.r_pos == 5 or self.r_pos == 6 or self.r_pos == 7):
            return 10
        return -10
    
    def step(self, at, s):
        self.pos = tuple(map(sum, zip(self.pos, self.actions[at])))
        x, y = self.pos
        self.find_relative_pos()
        reward = 0
        if x < 0 or x >= s or y < 0 or y >= s or (x,y) in self.body:
            self.is_dead = True
            reward = -100
        elif self.life == 0:
            self.is_dead = True
        elif self.pos == self.apple:
            reward = 100
            self.life = 500
        else:
            self.life -= 1
            reward = self.relative_reward(at)
        qt = int("{0:b}".format(self.r_pos) + self.find_context(), 2)
        return qt, reward
    
    def find_state(self):
        return  int("{0:b}".format(self.r_pos) + self.find_context(),2)
    
    def find_relative_pos(self):
        x = self.apple[0] - self.pos[0]
        y = self.apple[1] - self.pos[1]
        if y < 0:
            if x < 0:
                self.r_pos = 0
            elif x > 0:
                self.r_pos = 2
            else:
                self.r_pos = 1
        elif y > 0:
            if x < 0:
                self.r_pos = 5
            elif x > 0:
                self.r_pos = 7
            else:
                self.r_pos = 6
        elif x < 0:
            self.r_pos = 3
        else:
            self.r_pos = 4
            
    def find_context(self): 
        """
        return the index of the corresponding state in the Q_table
        """
        context = ["0"] * 4
        x = self.pos[0]
        y = self.pos[1]
        if (x-1, y) in self.body:
            context[0] = "1"
        if (x, y-1) in self.body:
            context[1] = "1"
        if (x+1, y) in self.body:
            context[2] = "1"
        if (x, y+1) in self.body:
            context[3] = "1"
        return "".join(context)
    
# tools
# ----------------------------------------------
def rd(max):
    return np.random.randint(max)

def reset_Q_table(s):
    global Q_table
    Q_table = np.zeros((128, 4))

def fill_Q_table(path):
    print("Loading Q_table from " + path + "...")
    global Q_table
    Q_table = np.loadtxt(path, delimiter=",")
    

def save_Q_table():
    nb = len(os.listdir("./saves"))
    name = "./saves/Q_table_" + str(nb) +".txt"
    print("Saving Q_table into " + name)
    np.savetxt(name, Q_table, delimiter=',')

# Main
# ----------------------------------------------

Q_table = np.array(0)

def train(path=None, s=40, step=10000000):
    i = 0
    record = 1
    snake = Snake()
    global Q_table
    if path:
        fill_Q_table(path)
    else:
        reset_Q_table(s)
    st = snake.find_state()
    print("Training...")
    while(i < step):
        if i % 1000000 == 0:
            print("step: " + str(i))
        if snake.is_dead:
            if len(snake.body) > record:
                record = len(snake.body)
            snake = Snake()
            st = snake.find_state()
        
        at = snake.take_action(st, 0.2)      
        stp1, r = snake.step(at,s)
        
        # update Q function
        atp1 = snake.take_action(stp1, 0.0)
        Q_table[st][at] = Q_table[st][at] + 0.1*(r + 0.9*Q_table[stp1][atp1] - Q_table[st][at])
        st = stp1
        snake.move()
        i += 1
    print("Training done !\nMax length: " + str(record))
    save_Q_table()

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-p", "--path", nargs='?', default=None, help="path to weights")
    p = parser.parse_args()
    
    train(p.path)