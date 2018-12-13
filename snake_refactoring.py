# Includes
import pygame
import random
import numpy as np
import math

###--- Inputs for the run ---###
screen_width, screen_height = 1200, 800 #Set the screen size
set_tick = 2 # Set the tick number. Higher equal faster snake.
X, Y = 25, 25 # Grid size, must be symmertical.
DEBUG = False # debug
###---Input End---###

class Snake():
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y
        self.sub_Q = False
        self.point = 0
        self.apple_amount = 0
        self.move = [1,0]
        self.current = [4,4]
        self.iter_matrix = [[1,0],[-1,0],[0,1],[0,-1]]
        self.whole = [[4,4],[3,4],[2,4]]
        self.best_moves = []
        self.back_up_move = []
        self.got_apple = False
        self.apple = [2,2] #self.get_apple_placement() 
        self.fitness = 0
        self.fitness_since_last_apple = 0
        self.Q_matrix = self.new_Q_matrix()
        self.opt_matrix(self.Q_matrix, self.apple[0], self.apple[1])
        self.sub_Q_wayout = []
        self.escape_routes = 0
        self.future_snake = []
        self.future_matrix = self.new_Q_matrix()
        self.future_room = 0
        self.warning = False          

    def new_Q_matrix(self):
        '''Returns a X*Y 2-dimensional matrix filled with -1s'''
        return(np.full((X, Y), -1))

    def update_Q_matrix(self):
        '''Creates a new Q matrix and sents it to be optimized'''
        self.Q_matrix = self.new_Q_matrix()
        self.opt_matrix(self.Q_matrix, self.apple[0], self.apple[1])
    
    def opt_matrix(self, matrix, gX, gY, get_longest=False, apple=False, future_snake=False):
        '''Gets a relevant matrix and finds steps to [gx, gy]'''
        if apple is True:
            self.escape_routes = 0
        matrix[gX][gY] = 0
        iterated_list = [[gX, gY]]
        new_iterated_list = []
        longest_snake = 0
        while len(iterated_list) > 0:
            for i in iterated_list:
                for iter in self.iter_matrix:
                    c_X, c_Y = i[0]+iter[0], i[1]+iter[1]
                    if self.check_inbounds(c_X, c_Y) is True: # Check that new values are within bounds
                        if get_longest is True and [c_X,c_Y] in self.whole: # Try to to get best way out if sub_Q is true
                            if self.whole.index([c_X, c_Y]) > longest_snake:
                                self.sub_Q_wayout = [i[0], i[1]]
                                longest_snake = self.whole.index([c_X, c_Y])
                        if [c_X,c_Y] not in self.whole and matrix[c_X][c_Y] != 0: # Check that they are not within snake and not within apple
                            if matrix[c_X][c_Y] == -1 and future_snake is False: # If the cell is not yet filled out, add a new value to it
                                matrix[c_X][c_Y] = matrix[i[0]][i[1]] + 1
                                if matrix[c_X][c_Y] == 1 and apple is True:
                                    self.escape_routes += 1
                                new_iterated_list.append([c_X, c_Y])
                            if matrix[c_X][c_Y] == -1 and future_snake is True and [c_X, c_Y] not in self.future_snake:
                                matrix[c_X][c_Y] = matrix[i[0]][i[1]] + 1
                                new_iterated_list.append([c_X, c_Y])
            iterated_list = new_iterated_list
            new_iterated_list = []

    def get_possible_moves(self):
        '''Populates self.best_moves and self.back_up_moves.'''
        self.calc_future_snake()
        self.best_moves, self.back_up_moves = [], [] # Empty best moves and back up moves list
        for iter in self.iter_matrix: # Which move gives the lowest Q matrix cell value
            s_X, s_Y = self.current[0]+iter[0], self.current[1]+iter[1]
            if self.check_inbounds(s_X, s_Y) is True:
                    if [s_X,s_Y] not in self.whole and self.Q_matrix[s_X][s_Y] != -1: # Check that they are not within the snake
                        self.best_moves.append([iter[0],iter[1],self.Q_matrix[s_X][s_Y]])
                    elif [s_X,s_Y] not in self.whole and self.Q_matrix[s_X][s_Y] == -1:
                        self.back_up_moves.append([iter[0],iter[1]])
        if self.sub_Q is False and self.warning is False:
            self.best_moves = sorted(self.best_moves, key=lambda x: x[2])
        elif self.warning is True:
            self.best_moves = sorted(self.best_moves, key=lambda x: x[2], reverse=True)
        else:
            self.best_moves = sorted(self.best_moves, key=lambda x: x[2], reverse=True)

    def check_inbounds(self, s_X, s_Y):
        if s_X > -1 and s_X < X and s_Y > -1 and s_Y < Y:
            return True
        else:
            return False

    def calc_future_snake(self):
        n_X, n_Y = self.current[0], self.current[1]
        self.future_snake = []
        self.future_matrix = self.new_Q_matrix()
        self.future_room = 0
        future_best_move = []
        for i in range(0,30):
            future_best_move = []
            for iter in self.iter_matrix:
                m_X, m_Y = n_X+iter[0], n_Y+iter[1]
                if self.check_inbounds(m_X, m_Y) is True and [m_X, m_Y] not in self.whole and [m_X, m_Y] not in self.future_snake:
                    future_best_move.append([self.Q_matrix[m_X, m_Y], m_X, m_Y])
            future_best_move = sorted(future_best_move, key=lambda x: x[0])
            if future_best_move != []:
                self.future_snake.append([future_best_move[0][1],future_best_move[0][2]])
                n_X, n_Y = future_best_move[0][1], future_best_move[0][2]
                if [future_best_move[0][1],future_best_move[0][2]] == self.apple:  
                    self.opt_matrix(self.future_matrix,self.apple[0], self.apple[1], future_snake=True)
                    for i in range(0,X):
                        for y in range(0,Y):
                            if self.future_matrix[i][y] > 0:
                                self.future_room += 1
                    #print(self.future_room)
                    if self.future_room != 0 and self.future_room < 30:
                        self.warning = True
                    else:
                        self.warning = False
                    break
            else:
                break
              
    def set_best_move(self):
        '''Gets the best possible move for the snake.'''
        if len(self.best_moves) > 0:
            self.sub_Q = False
            self.warning = False
            decided_move = [self.best_moves[0][0], self.best_moves[0][1]]
        elif len(self.back_up_moves) > 0:
            self.sub_Q = True
            self.opt_matrix(self.Q_matrix, self.current[0], self.current[1], get_longest=True)
            self.Q_matrix = self.new_Q_matrix()
            self.opt_matrix(self.Q_matrix, self.sub_Q_wayout[0], self.sub_Q_wayout[1])
            self.get_possible_moves()
            if len(self.best_moves) > 0:
                decided_move = [self.best_moves[0][0], self.best_moves[0][1]]
        else:
            decided_move = self.move # Let the snake die.
        return(decided_move)

    def iterate(self):
        self.current = [self.current[0]+self.move[0],self.current[1]+self.move[1]]
        if self.got_apple is False:
            self.whole = self.whole[:-1]
        else:
            self.got_apple = False
        self.whole.insert(0,self.current)
        self.fitness += 1
        self.fitness_since_last_apple +=1

    def get_apple_placement(self):
        apple = []
        for i in range(0, X):
            for j in range(0, Y):
                apple.append([i,j])
        for place in self.whole:
            apple.remove(place)
        return(random.choice(apple))

    def check_apple(self):
        if self.apple == self.current:
            self.apple_amount += 1
            self.apple = self.get_apple_placement()
            self.point += 1000
            self.got_apple = True
            self.fitness_since_last_apple = 0

    def check_game_over(self):
        if self.current[0] > X-1 or self.current[0] < 0:
            return(False)
        elif self.current[1] > Y-1 or self.current[1] < 0:
            return(False)
        elif self.current in self.whole[1:]:
            return(False)
        elif self.fitness_since_last_apple > 300:
            return(False)
        else:
            return(True)

def render(snake):
    SCREEN.fill((0, 0, 0))
    myfont = pygame.font.SysFont("monospace", 20)
    label = myfont.render("Warning: " + str(snake.warning) +" Points: "+ str(snake.point) +" Fitness: " +str(snake.fitness) +"  FSLA:  " + str(snake.fitness_since_last_apple), 1, (255,255,0))
    SCREEN.blit(label, (20, 20))
    pygame.draw.rect(SCREEN, (255, 0, 0),(100+snake.apple[0]*30, 100+snake.apple[1]*20, 30, 20)) # Draw apple
    for i in range(0, X):
        for j in range(0, Y):
            if DEBUG is True and snake.sub_Q is True: # Display the Q matrix. ONLY DEBUG. Can make model slow!
                if snake.Q_matrix[i, j] == -1:
                    pygame.draw.rect(SCREEN, (180, 180, 100),(100+i*30, 100+j*20, 30, 20))
                if [i, j] == snake.sub_Q_wayout: # Draw the way out of the sub Q system
                    pygame.draw.rect(SCREEN, (50, 50, 220),(100+i*30, 100+j*20, 30, 20))
            if DEBUG is True and snake.sub_Q is False:
                if [i, j] in snake.future_snake and [i, j] != [snake.apple[0], snake.apple[1]]: #Draw the future
                    pygame.draw.rect(SCREEN, (100, 100, 100),(100+i*30, 100+j*20, 30, 20))
            pygame.draw.rect(SCREEN, (255, 255, 255),(100+i*30, 100+j*20, 30, 20),1) #Draw grid
            if [i,j] in snake.whole and [i,j] not in snake.current: #Draw snake body
                pygame.draw.rect(SCREEN, (255, 255, 255),(100+i*30, 100+j*20, 30, 20))
            if [i,j] == snake.current: #Draw snake head
                pygame.draw.rect(SCREEN, (34, 139, 34),(100+i*30, 100+j*20, 30, 20))
            
    pygame.display.flip()

if __name__ == "__main__": #Main program
    pygame.init() 
    clock = pygame.time.Clock()
    clock.tick(40)
    SCREEN = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('Snake game') # Set the title of the window
    for i in range(0,2): # Run X amounts of times
        do_again = True
        snake=Snake(X, Y)
        while do_again is True:
            render(snake)
            for event in pygame.event.get(): # Manual input
                if event.type == pygame.QUIT:
                    done = True
            ''' 
            ## For manual input:
                pygame.event.pump()
                for i in range(0, 30):
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT] and snake.move[0] == 0:
                        snake.move = [-1,0]
                    if keys[pygame.K_RIGHT] and snake.move[0] == 0:
                        snake.move = [1,0]
                    if keys[pygame.K_UP] and snake.move[1] == 0:
                        snake.move = [0,-1]
                    if keys[pygame.K_DOWN] and snake.move[1] == 0:
                        snake.move = [0,1]
            '''
            
            snake.get_possible_moves()
            snake.move = snake.set_best_move()
            snake.check_apple()
            snake.iterate()
            snake.check_apple()
            if DEBUG is True:
                pass
            snake.update_Q_matrix()
            do_again = snake.check_game_over()
            if do_again is False:
                pygame.time.delay(1000)
        print("Game over. Score: " + str(snake.point))