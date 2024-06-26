import pygame
import math
from queue import PriorityQueue


WIDTH = 600
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Algorithm Visualization")

# COLOR CONSTANTS
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE =(255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

#main visualization tool

class Spot: #defining the node system
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        
        self.color = WHITE
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows
        
    def get_pos(self):
        return self.row, self.col  #setting up the board and the coordinate system (y, x)
    
    def is_closed(self):
        return self.color == RED #has the 'spot' already been looked at?
    
    def is_open(self):
        return self.color == GREEN #is the 'spot' in the open set?
    
    def is_barrier(self):
        return self.color == BLACK #can the 'spot' be visited? i.e barrier or not
    
    def is_start(self):
        return self.color == ORANGE #is the 'spot' the starting node?

    def is_end(self):
        return self.color == TURQUOISE #is the 'spot' the ending node?
    
    def reset(self):
         self.color = WHITE #resets the board.
    
    #instead of knowing the state of the node, the following methods change the state of the node within the given parameters
    def make_closed(self):
        self.color = RED 
    
    def make_open(self):
        self.color = GREEN 
    
    def make_barrier(self):
        self.color = BLACK 
    
    def make_start(self):
        self.color = ORANGE 

    def make_end(self):
        self.color = TURQUOISE
    
    def make_path(self):
        self.color = PURPLE

    def draw(self,win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid): #checks to see if the 'neighbours' of the current node are barriers or not 
        self.neighbours = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): #DOWN
            self.neighbours.append(grid[self.row + 1][self.col])
            
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): #UP
            self.neighbours.append(grid[self.row - 1][self.col])
            
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): #RIGHT
            self.neighbours.append(grid[self.row][self.col + 1])
            
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): #LEFT
            self.neighbours.append(grid[self.row ][self.col - 1])
            
    def __lt__(self, other):
        return False

def h(n1, n2): #manhattan ditance (heuristic function)
    x1, y1 = n1
    x2, y2 = n2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(cameFrom, current, draw): #reconstructs the final path after running the algorithm
    while current in cameFrom:
        current = cameFrom[current]
        current.make_path()
        draw()

def algorithm(draw, grid, start, end): #main A* algorithm. (See attached paper for complete breakdown/analysis)
    count = 0
    openSet = PriorityQueue()
    openSet.put((0, count, start))
    cameFrom = {}
    gScore = {spot: float("inf") for row in grid for spot in row}
    gScore[start] = 0
    fScore = {spot: float("inf") for row in grid for spot in row}
    fScore[start] = h(start.get_pos(), end.get_pos())
    
    opensetHash = {start}
    while not openSet.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit() 

        current = openSet.get()[2]
        opensetHash.remove(current)
        
        if current == end:
            reconstruct_path(cameFrom, end , draw)
            end.make_end()
            return True
        
        for neighbour in current.neighbours:
            tempGScore = gScore[current] + 1
            
            if tempGScore < gScore[neighbour]:
                cameFrom[neighbour] = current
                gScore[neighbour] = tempGScore
                fScore[neighbour] = tempGScore + h(neighbour.get_pos(), end.get_pos())
                if neighbour not in opensetHash:
                    count += 1
                    openSet.put((fScore[neighbour], count, neighbour))
                    opensetHash.add(neighbour)
                    neighbour.make_open()
                    
        draw()
        if current != start:
            current.make_closed()

    return False

def make_grid(rows, width): #fun begins
        grid = []
        gap = width // rows
        for i in range(rows):
            grid.append([])
            for j in range(rows):
                spot = Spot(i, j, gap, rows)
                grid[i].append(spot)
                
        return grid

def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):   
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))

def draw(win, grid, rows, width):
    win.fill(WHITE)
    
    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()
    
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos
    
    row = y // gap
    col = x // gap
    
    return row, col


def main(win, width):
    ROWS = 50 
    grid = make_grid(ROWS, width)
    
    start = None
    end = None
    
    run = True
    started = False
    
    while run:
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if started:
                continue
            
            if pygame.mouse.get_pressed()[0]: #LEFT click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()
                    
            elif pygame.mouse.get_pressed()[2]: #RIGHT click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
                elif event.key == pygame.K_r:
                    pygame.quit()
                elif event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbours(grid)
                    
                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)
    pygame.quit()
    
main(WIN, WIDTH)

