import os
s = 40
Q_table = []
st = 0
death = 0
record = 1
run = True

# snake
# ----------------------------------------------
class Snake:
    def __init__(self):
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
        apple_pos = (rd(s), rd(s))
        while apple_pos in self.body:
            apple_pos = (rd(s), rd(s))
        self.apple = apple_pos
    
    def move(self):
        if self.pos == self.apple:
            self.create_apple()
        else:
            self.draw_(self.body.pop(), c=(0,0,0))
        self.body.insert(0,self.pos)
    
    def take_action(self, st):
        return Q_table[st].index(max(Q_table[st]))
    
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
    
    def step(self, at):
        self.pos = tuple(map(sum, zip(self.pos, self.actions[at])))
        x, y = self.pos
        self.find_relative_pos()
        if x < 0 or x >= s or y < 0 or y >= s or (x,y) in self.body:
            self.is_dead = True
        elif self.life == 0:
            self.is_dead = True
        elif self.pos == self.apple:
            self.life = 500
        qt = int("{0:b}".format(self.r_pos) + self.find_context(), 2)
        return qt
    
    def find_state(self):
        a = "{0:b}".format(self.r_pos)
        b = self.find_context()
        res = a + b
        #print("r_pos: ", self.r_pos, "context: ", b)
        return  int(res,2)
    
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
    
    def draw_(self, t, c=(255,255,255)):
        fill(c[0], c[1], c[2])
        if t[0] < 40 and t[1] < 40: 
            rect(t[0] * 10, t[1] * 10, 10, 10)
    
    def draw_head(self):
        fill(0,0,255)
        if self.pos[0] < 40 or self.pos[1] < 40:
            circle(self.pos[0] * 10 + 5, self.pos[1] * 10 + 5, 5)
            
    def draw_apple(self):
        self.draw_(self.apple, (255,0,0))

    def draw_reset(self):
        for part in self.body:
            self.draw_(part, c=(0,0,0))
        self.draw_(self.apple, c=(0,0,0))

# tools
# ----------------------------------------------
def rd(max):
    return int(random(0,max))

def reset_Q_table():
        qt = []
        for i in range(128):
            qt.append([0] * 4)
        return qt

def fill_Q_table():
    qt = []
    f = open("./saves/Q_table_2.txt", "r")
    for line in f.readlines():
        weights = line.split(",")
        qt.append([float(x) for x in weights])
    f.close()
    return qt

def update_text(x, nb):
    fill(87,89,93)
    noStroke()

    if x == 1:
        rect(s * 11.8, 40, 29, 11)
        fill(255,255,255)
        text(str(nb), s * 12, 50)
    elif x == 2:
        rect(s * 11.8, 60, 29, 11)
        fill(255,255,255)
        text(str(nb), s * 12, 70)
    else:
        rect(s * 11.8, 80, 329, 11)
        fill(255,255,255)
        text(str(nb), s * 12, 90)
    stroke(0)

# Processing
# ----------------------------------------------
snake = Snake()
def setup():
    size(s * 15, s * 10)
    background(0,0,0)
    # info part
    fill(87,89,93)
    rect(s * 10, 0, 200, 400)
    fill(255,255,255)
    text("Length:", s * 10.5, 50)
    text("1", s * 12, 50)
    text("Deaths:", s * 10.5, 70)
    text("0", s * 12, 70)
    text("Record:", s* 10.5, 90)
    text("0", s * 12, 90)

    global Q_table
    Q_table = fill_Q_table()
    st = snake.find_state()
    frameRate(10)
    
def draw():
    if run:
        global snake
        global st
        if snake.is_dead:
            global record
            if len(snake.body) > record:
                record = len(snake.body)
                update_text(3, record)
            snake.draw_reset()
            snake = Snake()
            st = snake.find_state()
            global death
            death += 1
            update_text(2, death)
        
        at = snake.take_action(st)       
        st = snake.step(at)
        snake.move()
        for part in snake.body:
            snake.draw_(part)
        snake.draw_head()
        snake.draw_apple()
        update_text(1, len(snake.body))

def keyPressed():
    if key == 'p':
        global run
        run = not run
    
