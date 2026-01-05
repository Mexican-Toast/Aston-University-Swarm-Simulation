import pygame
import math
import random
import heapq

pygame.init()

#Defining colours
BLACK = (0, 0, 0) #grid border
GREY = (120, 120, 120) #roads 4
WHITE = (255, 255, 255) #defealt
RED = (255, 0, 0) #building 1
GREEN = (0, 255, 0) #rubble 3
DARK_GREEN = (1, 120, 1) 
LIGHT_BLUE = (0, 200, 255) #flooded [3]
BLUE = (0, 0, 255) #deep water 5
YELLOW = (235, 222, 52) #collapsed building 2

###Input variables for start screen###
grid_size_input = 15 #default value
num_survivors_input = 10 #default value
search_type_input = 2 #default value
multiple_L1s_input = 3 #default value
multiple_L2s_input = 3 #default value

###Setting up the display###
#Grid size with same width and height (amount of cells)
GRID_SIZE = grid_size_input

#The screen scales with the grid size
screen_width = 52.222 * GRID_SIZE
screen_height = 52.222 * GRID_SIZE
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Flood Rescue Simulation")
screen.fill((WHITE))  #Filling the screen white

###Setting up the 2D grid###
#Cell size
CELL_SIZE = screen_width // GRID_SIZE
#Generate 2D grid
grid = [[None for i in range(GRID_SIZE)] for i in range(GRID_SIZE)]

#UAV location on generate
UAV_x_location = None
UAV_y_location = None

###Environment functions###
def environment():
    ###The different terrain types###
    def terrain_building():
        ID = 1
        survivor_visable = False
        survivor_navigable = False
        flooded = False
        L1_navigable = False
        
        #The list inside the list is for things placed on the map
        #The list inside the list has 5 posistions in total and the first 3 are for survivors, L1s, and L2s. The
        # L1 and L2 postitions can also be lists themselves for when there are multiple of them. The fouth
        # position is for the exit (E).
        #I think the last position is for marking if the cell has been visited. Not 100% sure? if so then it is 
        # not currently being used
        terrain_settings = [ID, survivor_visable, survivor_navigable, flooded,
                            L1_navigable, [None, [], [], None, None]]
        return terrain_settings

    def terrain_collapsed_building():
        ID = 2
        survivor_visable = False
        survivor_navigable = False
        flooded = False
        L1_navigable = True
        
        terrain_settings = [ID, survivor_visable, survivor_navigable, flooded,
                            L1_navigable, [None, [], [], None, None]]
        return terrain_settings

    def terrain_rubble():
        ID = 3
        survivor_visable = False
        survivor_navigable = True
        flooded = False
        L1_navigable = True
        
        terrain_settings = [ID, survivor_visable, survivor_navigable, flooded,
                            L1_navigable, [None, [], [], None, None]]
        return terrain_settings

    def terrain_road():
        ID = 4
        survivor_visable = True
        survivor_navigable = True
        flooded = False
        L1_navigable = True
        
        terrain_settings = [ID, survivor_visable, survivor_navigable, flooded,
                            L1_navigable, [None, [], [], None, None]]
        return terrain_settings

    def terrain_deep_water():
        ID = 5
        survivor_visable = True
        survivor_navigable = False
        flooded = False
        L1_navigable = True
        
        terrain_settings = [ID, survivor_visable, survivor_navigable, flooded,
                            L1_navigable, [None, [], [], None, None]]
        return terrain_settings

    ###Terrain functions###
    #Picks a random terrain type from the fist 3 IDs
    def terrain_picker():
        terrain_IDs = [1, 2, 3]
        selected_ID = random.choice(terrain_IDs)
        
        if selected_ID == 1:
            return terrain_building()
        elif selected_ID == 2:
            return terrain_collapsed_building()
        elif selected_ID == 3:
            return terrain_rubble()

    #Generates the river, roads, and then random terrain from the first 3 IDs
    def terrain_generator():        
        #determining the amount of roads on the x axis
        x_road_num = random.randrange(1, GRID_SIZE - int(GRID_SIZE / 1.9))
        x_roads = []
        for i in range(x_road_num):
            x_roads.append((random.randrange(1, GRID_SIZE + 1)) - 1)
        
        #determining the amount of roads on the y axis
        y_road_num = random.randrange(0, GRID_SIZE - int(GRID_SIZE / 1.5))
        y_roads = []
        if y_road_num != 0:
            for i in range(y_road_num):
                y_roads.append(random.randrange(1, GRID_SIZE + 1))
        
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                #Determines the terrain types
                if y == int(GRID_SIZE / 2) + 1 or y == int(GRID_SIZE / 2) - 1:
                    grid[x][y] = terrain_road()
                elif x in x_roads:
                    grid[x][y] = terrain_road()
                elif y == int(GRID_SIZE / 2):
                    grid[x][y] = terrain_deep_water()
                elif y in y_roads:
                    grid[x][y] = terrain_road()
                else:
                    grid[x][y] = terrain_picker()
    #running the function
    terrain_generator()
    
    ###Placement functions###
    
    #IMPORTANT!#
    #grid[?][?][?][?] works by the first 2 [] being the coordinates so grid[x][y] or grid[12][2] as a specific 
    #example. The next [] represents which terrain setting is being used or edited so for example [3] is the is
    #flooded tile setting. If the 3rd [] is [5] then a fourth [] is need which is for representing what is inside
    #the tile like survivors or UAVs.
    
    #Generates survivors
    def survivors_generator():
        num_survivors = num_survivors_input  #Number of survivors from settings
        for i in range(num_survivors):
            #Randomly select coordinates until a suitable cell is found
            while True:
                x = random.randint(0, GRID_SIZE - 1)
                y = random.randint(0, GRID_SIZE - 1)
                if dijkstra((x, y), None, grid, 3, None): #checks if there is a route to a road
                    if grid[x][y][0] != 5: #makes sure survivors don't spawn in the river
                        #Has to be not in the below line, otherwise preventing survivors from spawning on the edges won't work!
                        #Unusual if put has to be structure this way
                        if not ((x == 0 or x == GRID_SIZE - 1) or (y == 0 or y == GRID_SIZE - 1)) or grid[x][y][0] != 4: #no spawning on roads that are on the border of the environment.
                            if grid[x][y][5][0] != "S": #and not spawning on top of existing survivors
                                grid[x][y][5][0] = "S" #adds survivor to the cell
                                grid[x][y][4] = True #makes sure that the terrain the survivor is on is navigable to the L1
                                grid[x][y][2] = True #makes sure that the terrain the survivor is on is navigable to the survivor
                                break #stop the loop
    survivors_generator()
    
    #Generates the L1 and the L2 at the edge of the grid on a road
    def L1_and_L2_generator(l1_amount, l2_amount):
        while True:
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            #If statement to determine if at edge of grid and on road
            if grid[x][y][0] == 4 and ((x == 0 or x == GRID_SIZE - 1) or (y == 0 or y == GRID_SIZE - 1)):
                global UAV_x_location
                UAV_x_location = x
                global UAV_y_location
                UAV_y_location = y

                if l1_amount == 1:
                    grid[x][y][5][1] = 1 #adds L1 to the cell
                else:
                    for L1_id in range(l1_amount):
                        grid[x][y][5][1].append(L1_id) #adds the list of L1s to the cell
                
                if l2_amount == 1:
                    grid[x][y][5][2] = 2 #adds L2 to the cell
                else:
                    for l2_id in range(l2_amount):
                        grid[x][y][5][2].append(l2_id) #adds the list of L1s to the cell
                print("The cell value after L1s and L2s have been generated: " + str(grid[x][y]))
                break
    L1_and_L2_generator(multiple_L1s_input, multiple_L2s_input)

#Generates the flooding in the map
def flood_sim():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if grid[x][y][3]:
                #Checks if the cell should no longer be flooded based on a 30% chance
                    if random.random() < 0.3:
                        #Go to previous state
                        grid[x][y] = (grid[x][y][0], grid[x][y][1], grid[x][y][2], False, grid[x][y][4], grid[x][y][5])
            else:
                #Checks that the L1 is not there
                #print("Flood sim check: what is grid[x][y][5][1]?", grid[x][y][5][1])
                if (grid[x][y][5][1] != 1 and multiple_L1s_input == 1) or not (grid[x][y][5][1] and multiple_L1s_input > 1):
                    #Checks if the terrain type is suitable for flooding
                    #print("Passed check")
                    if grid[x][y][0] in [1, 2, 3, 4]:
                        #Checks if the cell should be flooded based on a 5% chance
                        if random.random() < 0.05:
                            #Sets the cell as flooded and not navigable for survivors
                            #(Where ther is grid in setting the settings of the terrain, it means its the same as before)
                            grid[x][y] = (grid[x][y][0], grid[x][y][1], grid[x][y][2], True, grid[x][y][4], grid[x][y][5])

###Dijkstra's algorithm###
#Dijkstra_type is used to decide how to use the function, L1 when going to survivor (1) 
# and surviror viseversa (2)
#Checking if survivor has a route to a road when placed (3)
#Checking if the L2 is doing a random search (4)
#Checking if the L2 is the dijkstra search (5)
#For the input of the unvisited cells the grid can just be used as it's all unvisited
def dijkstra(start, end, grid, dijkstra_type, unvisited_cells):
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]  #possible movement: down, up, right, left
    distance = {start: 0} #is only ever 1 (all cells have the same distance between them) (may change)
    visited = set()
    previous = {}
    queue = [(0, start)]
    while queue:
        dist, current = heapq.heappop(queue)

        if not dijkstra_type == 5: #this is the default path maker
            if current == end: #if at the end then returns the path
                path = []
                while current in previous:
                    path.append(current)
                    current = previous[current]
                path.append(start)
                return path[::-1] #this returns the path in reverse for the correct order
        else: #this is the path maker for taking unvisited cells into account
            if current in unvisited_cells: #if the current cell is unvisited, returns the path
                path = []
                while current in previous:
                    path.append(current)
                    current = previous[current]
                path.append(start)
                return path[::-1] #this returns the path in reverse for the correct order
        
        if current in visited:
            continue

        visited.add(current)
        
        #IGNORE distance, not currently being used
        if dijkstra_type == 1: #when it needs to be done with L1 navigable in mind
            for dx, dy in directions:
                #Add the difference in x and y to the current coords
                new_x, new_y = current[0] + dx, current[1] + dy
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and grid[new_x][new_y][4]: #!!!This line is the line that changes the most between the dijkstra types
                    #New variable to hold the new distance
                    new_distance = distance[current] + 1
                    if (new_x, new_y) not in distance or new_distance < distance[(new_x, new_y)]:
                        distance[(new_x, new_y)] = new_distance
                        previous[(new_x, new_y)] = current
                        #Adds the new distance and new current (coords) into the queue to be processed into a path
                        heapq.heappush(queue, (new_distance, (new_x, new_y)))
        elif dijkstra_type == 2: #when it needs to be done with survivor navigable in mind
            for dx, dy in directions:
                new_x, new_y = current[0] + dx, current[1] + dy
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and grid[new_x][new_y][2]:
                    new_distance = distance[current] + 1
                    if (new_x, new_y) not in distance or new_distance < distance[(new_x, new_y)]:
                        distance[(new_x, new_y)] = new_distance
                        previous[(new_x, new_y)] = current
                        heapq.heappush(queue, (new_distance, (new_x, new_y)))
        elif dijkstra_type == 3: #when it needs to find if the is a route to a road when a survivor is placed
            for dx, dy in directions:
                new_x, new_y = current[0] + dx, current[1] + dy
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and grid[new_x][new_y][2]:  #checks if the cell is navigable fo survivors
                    new_distance = distance[current] + 1
                    if (new_x, new_y) not in distance or new_distance < distance[(new_x, new_y)]:
                        distance[(new_x, new_y)] = new_distance
                        heapq.heappush(queue, (new_distance, (new_x, new_y)))
                        if grid[current[0]][current[1]][0] == 4:  #checks if the current cell is a road
                            return True
        elif dijkstra_type == 4: #when it needs the L2 to search for a survivor
            for dx, dy in directions:
                new_x, new_y = current[0] + dx, current[1] + dy
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE: #allows movement to any cell
                    new_distance = distance[current] + 1
                    if (new_x, new_y) not in distance or new_distance < distance[(new_x, new_y)]:
                        distance[(new_x, new_y)] = new_distance
                        previous[(new_x, new_y)] = current
                        heapq.heappush(queue, (new_distance, (new_x, new_y)))
        elif dijkstra_type == 5: #when it needs the L2 to search for a survivor without knowing the end
            for dx, dy in directions:
                new_x, new_y = current[0] + dx, current[1] + dy
                if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE: #allows movement to any cell
                    new_distance = distance[current] + 1
                    if (new_x, new_y) not in distance or new_distance < distance[(new_x, new_y)]:
                        distance[(new_x, new_y)] = new_distance
                        previous[(new_x, new_y)] = current
                        heapq.heappush(queue, (new_distance, (new_x, new_y)))

    return None #happens when failed to do any previous return

#Function is to find if a survivor is in a adjacent cell
def survivor_adjacent(cell, mode):
    x, y = cell
    #Checks all adjacent cells
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            #Skip the current cell we are on
            if dx == 0 and dy == 0:
                continue
            new_x, new_y = x + dx, y + dy
            #Checks if the adjacent cell is within the grid boundaries
            if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                #Checks the mode of the function
                #Returns true
                if mode == 1:
                    #Checks if there is a survivor in the adjacent cell
                    if grid[new_x][new_y][5][0] == "S":
                        return True
                #Returns coords of the survivor
                elif mode == 2:
                    #Checks if there is a survivor in the adjacent cell
                    if grid[new_x][new_y][5][0] == "S":
                        return (new_x, new_y)
    return False #returns this when failing to do the if statements

###Drawing###
#Draw the grid
def draw_grid():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            ###Cell colours###
            #Determines base on if flooded or not
            if grid[x][y][3] == True:
                colour = BLUE #previously LIGHT_BLUE
            #Determines colour based on terrain type ID (being the [0] part)
            elif grid[x][y][0] == 1:
                colour = RED
            elif grid[x][y][0] == 2:
                colour = YELLOW
            elif grid[x][y][0] == 3:
                colour = GREEN
            elif grid[x][y][0] == 4:
                colour = GREEN #previously GREY
            elif grid[x][y][0] == 5:
                colour = BLUE

            #Draw the cell and its borders
            pygame.draw.rect(screen, colour, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, BLACK, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
            
            ###Render text###
            #Survivors
            if grid[x][y][5][0] == "S":
                text = font.render(f'S', True, BLACK)  #render the survivor
                text_rect = text.get_rect(topleft = (x * CELL_SIZE + 2, y * CELL_SIZE + 2))  #put in top left
                screen.blit(text, text_rect)  #blit text onto the screen
            
            #L1
            #When there are multiple L1s. This is needed otherwise when there is only one L1 the sim is running then the len if will cause an error
            if multiple_L1s_input > 1:
                if len(grid[x][y][5][1]) > 1:
                    text = small_font.render(f'L1s: ' + str(len(grid[x][y][5][1])), True, BLACK)  #render the L1
                    text_rect = text.get_rect(topright = (x * CELL_SIZE + CELL_SIZE - 2, y * CELL_SIZE + 2))  #put in top right
                    screen.blit(text, text_rect)  #blit text onto the screen
                elif grid[x][y][5][1] == 1 or grid[x][y][5][1]: #checks if it equals 1 or if it is a non empty list
                    text = font.render(f'L1', True, BLACK)  #render the L1
                    text_rect = text.get_rect(topright = (x * CELL_SIZE + CELL_SIZE - 2, y * CELL_SIZE + 2))  #put in top right
                    screen.blit(text, text_rect)  #blit text onto the screen
                    
                    #When there is only one L1 in the sim
            elif grid[x][y][5][1] == 1 or grid[x][y][5][1]: #checks if it equals 1 or if it is a non empty list
                text = font.render(f'L1', True, BLACK)  #render the L1
                text_rect = text.get_rect(topright = (x * CELL_SIZE + CELL_SIZE - 2, y * CELL_SIZE + 2))  #put in top right
                screen.blit(text, text_rect)  #blit text onto the screen
            
            #L2
            #When there are multiple L2s. This is needed otherwise when there is only one L2 the sim is running then the len if will cause an error
            if multiple_L2s_input > 1:
                if len(grid[x][y][5][2]) > 1:
                    text = small_font.render(f'L2s: ' + str(len(grid[x][y][5][2])), True, BLACK)  #render the L2 with the amount there is in the cell
                    text_rect = text.get_rect(bottomleft = (x * CELL_SIZE + 2, y * CELL_SIZE + CELL_SIZE - 2 - (small_font_size / 2)))  #put in bottom left
                    screen.blit(text, text_rect)  #blit text onto the screen
                elif grid[x][y][5][2] == 2 or grid[x][y][5][2]: #checks if it equals 2 or if it is a non empty list
                    text = font.render(f'L2', True, BLACK)  #render the L2
                    text_rect = text.get_rect(bottomleft = (x * CELL_SIZE + 2, y * CELL_SIZE + CELL_SIZE - 2))  #put in bottom left
                    screen.blit(text, text_rect)  #blit text onto the screen
                    
                    #When there is only one L2
            elif grid[x][y][5][2] == 2 or grid[x][y][5][2]: #checks if it equals 2 or if it is a non empty list
                text = font.render(f'L2', True, BLACK)  #render the L2
                text_rect = text.get_rect(bottomleft = (x * CELL_SIZE + 2, y * CELL_SIZE + CELL_SIZE - 2))  #put in bottom left
                screen.blit(text, text_rect)  #blit text onto the screen
            
            #Exit
            if grid[x][y][5][3] == "E":
                text = font.render(f'E', True, BLACK)  #render the exit
                text_rect = text.get_rect(bottomright = (x * CELL_SIZE + CELL_SIZE - 2, y * CELL_SIZE + CELL_SIZE - 2))  #put in bottom left
                screen.blit(text, text_rect)  #blit text onto the screen

#Draw the start screen
def draw_start():
    ###Background###
    #This is needed to get rid of deleted number when typing
    screen.fill((WHITE))
    
    ###Render information text###
    #The title
    text = font.render(f'Flood drone rescue simulation', True, BLACK)
    text_rect = text.get_rect(midtop = (screen_width // 2, 10))
    screen.blit(text, text_rect)
    
    #Key information
    text = font.render(f'Key Infomation:', True, BLACK)
    text_rect = text.get_rect(topleft = (20, 50))
    screen.blit(text, text_rect)
    
    #What is in the cells
    text = font.render(f'L1 is layer 1 UAV, L2 is layer 2 UAV, E is exit, S is survivor', True, BLACK)
    text_rect = text.get_rect(topleft = (20, 80))
    screen.blit(text, text_rect)
    
    #Different kinds of cells
    text = font.render(f'L2 UAV can navigate on any cell', True, BLACK)
    text_rect = text.get_rect(topleft = (20, 110))
    screen.blit(text, text_rect)
    
    ###Draw example cells with text###
    pygame.draw.rect(screen, RED, (20, 140, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, BLACK, (20, 140, CELL_SIZE, CELL_SIZE), 1)
    
    text = font.render(f'= Red, not navigable to either L1 or survivors', True, BLACK)
    text_rect = text.get_rect(topleft = (80, 150))
    screen.blit(text, text_rect)
    
    pygame.draw.rect(screen, YELLOW, (20, 190, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, BLACK, (20, 190, CELL_SIZE, CELL_SIZE), 1)
    
    text = font.render(f'= Yellow, navigable to L1 but not survivors', True, BLACK)
    text_rect = text.get_rect(topleft = (80, 200))
    screen.blit(text, text_rect)
    
    pygame.draw.rect(screen, GREEN, (20, 240, CELL_SIZE, CELL_SIZE))
    pygame.draw.rect(screen, BLACK, (20, 240, CELL_SIZE, CELL_SIZE), 1)
    
    text = font.render(f'= Green, navigable to either L1 or survivors', True, BLACK)
    text_rect = text.get_rect(topleft = (80, 250))
    screen.blit(text, text_rect)
    
    pygame.draw.rect(screen, BLUE, (20, 290, CELL_SIZE, CELL_SIZE)) #previously LIGHT_BLUE
    pygame.draw.rect(screen, BLACK, (20, 290, CELL_SIZE, CELL_SIZE), 1)
    
    text = font.render(f'= Water, navigable to L1 but not survivors', True, BLACK)
    text_rect = text.get_rect(topleft = (80, 300))
    screen.blit(text, text_rect)
    
    ###Render user inputs###
    text = font.render(f'User inputs:', True, BLACK)
    text_rect = text.get_rect(topleft = (20, 400))
    screen.blit(text, text_rect)
    
    text = font.render(f'Grid size = ' + grid_size_temp, True, BLACK)
    text_rect = text.get_rect(topleft = (20, 440))
    screen.blit(text, text_rect)
    
    text = font.render(f'Number of survivors = ' + num_survivors_temp, True, BLACK)
    text_rect = text.get_rect(topleft = (20, 480))
    screen.blit(text, text_rect)
    
    text = font.render(f'What type of search for survivors will be used = ' + search_type_temp, True, BLACK)
    text_rect = text.get_rect(topleft = (20, 520))
    screen.blit(text, text_rect)
    
    text = font.render(f'(1 for omniscient L1 closest search, 2 for random L2 search and', True, BLACK)
    text_rect = text.get_rect(topleft = (20, 540))
    screen.blit(text, text_rect)
    
    text = font.render(f'3 for L2 lawnmower search)', True, BLACK)
    text_rect = text.get_rect(topleft = (20, 560))
    screen.blit(text, text_rect)
    
    text = font.render(f'Number of L1s = ' + multiple_L1s_temp, True, BLACK)
    text_rect = text.get_rect(topleft = (20, 600))
    screen.blit(text, text_rect)
    
    text = font.render(f'Number of L2s = ' + multiple_L2s_temp, True, BLACK)
    text_rect = text.get_rect(topleft = (20, 640))
    screen.blit(text, text_rect)
    
    ###Render controls text###
    #Switch input text
    text = font.render(f'Press enter to switch inputs', True, BLACK)
    text_rect = text.get_rect(midbottom = (screen_width // 2, 725))
    screen.blit(text, text_rect)
    
    #Start simulation text
    text = font.render(f'Press space to start the simulation', True, BLACK)
    text_rect = text.get_rect(midbottom = (screen_width // 2, 780))
    screen.blit(text, text_rect)

#Draw the end screen
def draw_end():
    ###Background###
    #This is needed to get rid the last drawn frame of the sim
    screen.fill((WHITE))
    
    ###Render infomation text###
    #The title
    text = font.render(f'Flood drone rescue simulation', True, BLACK)
    text_rect = text.get_rect(midtop = (screen_width // 2, 10))
    screen.blit(text, text_rect)
    
    text = font.render(f'Statistics', True, BLACK)
    text_rect = text.get_rect(midtop = (screen_width // 2, 30))
    screen.blit(text, text_rect)
    
    #Key information
    text = font.render(f'Key Infomation:', True, BLACK)
    text_rect = text.get_rect(topleft = (20, 80))
    screen.blit(text, text_rect)
    
    #Grid size
    text = font.render(f'Grid size = ' + str(grid_size_input), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 120))
    screen.blit(text, text_rect)
    
    #Num of survivors
    text = font.render(f'Number of survivors = ' + str(num_survivors_input), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 160))
    screen.blit(text, text_rect)
    
    #Search type
    if search_type_input == 1:
        text = font.render(f'Search type = Omnscient', True, BLACK)
        text_rect = text.get_rect(topleft = (20, 200))
        screen.blit(text, text_rect)
    elif search_type_input == 2:
        text = font.render(f'Search type = Random', True, BLACK)
        text_rect = text.get_rect(topleft = (20, 200))
        screen.blit(text, text_rect)
    else:
        text = font.render(f'Search type = Lawnmower', True, BLACK)
        text_rect = text.get_rect(topleft = (20, 200))
        screen.blit(text, text_rect)
    
    #Amount of L1s
    text = font.render(f'Number of L1s = ' + str(multiple_L1s_input), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 240))
    screen.blit(text, text_rect)
    
    #Amount of L2s
    text = font.render(f'Number of L2s = ' + str(multiple_L2s_input), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 280))
    screen.blit(text, text_rect)
    
    ###Render stats text###
    #Stats
    text = font.render(f'Stats:', True, BLACK)
    text_rect = text.get_rect(topleft = (20, 320))
    screen.blit(text, text_rect)
    
    #Time taken to find and save all survivors
    text = font.render(f'Time taken to find and save all survivors (in cycles of the sim)', True, BLACK)
    text_rect = text.get_rect(topleft = (20, 360))
    screen.blit(text, text_rect)
    
    text = font.render(f' = ' + str(time_2_find_and_save_all_survivors_temp), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 380))
    screen.blit(text, text_rect)
    
    #Average time taken to find and save all survivors
    text = font.render(f'Average time taken to find and save all survivors (in cycles)', True, BLACK)
    text_rect = text.get_rect(topleft = (20, 420))
    screen.blit(text, text_rect)
    
    text = font.render(f' = ' + str(time_2_find_and_save_all_survivors_average), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 440))
    screen.blit(text, text_rect)
    
    '''
    #Cells to find
    #Cells taken to find the first survivor
    text = font.render(f'Cells taken to find the first survivor = ' + str(cells_2_find_first_survivor), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 280))
    screen.blit(text, text_rect)
    
    #Cells taken to find the last survivor
    text = font.render(f'Cells taken to find the last survivor = ' + str(cells_2_find_last_survivor), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 320))
    screen.blit(text, text_rect)
    
    #Average cells to find a survivor
    text = font.render(f'Cells taken on average to find a survivor = ' + str(cells_average_2_find_survivor), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 360))
    screen.blit(text, text_rect)
    
    #Cells taken to find all survivors
    text = font.render(f'Cells taken to find all survivors = ' + str(cells_2_find_all_survivors), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 400))
    screen.blit(text, text_rect)
    
    #Cells to save
    #Cells taken to save the first survivor
    text = font.render(f'Cells taken to reach and save the first survivor = ' + str(cells_2_save_first_survivor), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 440))
    screen.blit(text, text_rect)
    
    #Cells taken to save the last survivor
    text = font.render(f'Cells taken to reach and save the last survivor = ' + str(cells_2_save_last_survivor), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 480))
    screen.blit(text, text_rect)
    
    #Average cells to save a survivor
    text = font.render(f'Cells taken on average to reach and save a survivor = ' + str(cells_average_2_save_survivor), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 520))
    screen.blit(text, text_rect)
    
    #Cells taken to save all survivors
    text = font.render(f'Cells taken to save all survivors = ' + str(cells_2_save_all_survivors), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 560))
    screen.blit(text, text_rect)
    
    #Time to save
    #Time taken to save the first survivor
    text = font.render(f'Time taken to reach and save the first survivor = ' + str(time_2_save_first_survivor), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 600))
    screen.blit(text, text_rect)
    
    #Time taken to save the last survivor
    text = font.render(f'Time taken to reach and save the last survivor = ' + str(time_2_save_last_survivor), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 640))
    screen.blit(text, text_rect)
    
    #Average time to save a survivor
    text = font.render(f'Time taken on average to reach and save a survivor = ' + str(time_average_2_save_survivor), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 680))
    screen.blit(text, text_rect)
    
    #Time taken to save all survivors
    text = font.render(f'Time taken to save all survivors = ' + str(time_2_save_all_survivors), True, BLACK)
    text_rect = text.get_rect(topleft = (20, 720))
    screen.blit(text, text_rect)
    '''
    
    ###Render controls text###
    #New simulation text
    text = font.render(f'Press enter to start a new simulation', True, BLACK)
    text_rect = text.get_rect(midbottom = (screen_width // 2, 740))
    screen.blit(text, text_rect)
    
    #End simulation text
    text = font.render(f'Press space to end the simulation', True, BLACK)
    text_rect = text.get_rect(midbottom = (screen_width // 2, 780))
    screen.blit(text, text_rect)

####The Main game loop####
###Setting up variables for the loop###
running = True #whilst true the simulation will continue to run
clock = pygame.time.Clock() #keeps track of time

font = pygame.font.Font(None, 36) #setting up font and font size
small_font_size = 18
small_font = pygame.font.Font(None, small_font_size) #setting up font and font size

#Store L1, exit, and L2 coordinates
L1_coords = None
Exit = None
L2_coords = None

#Store the closest survivor to the L1
closest_survivor = None
closest_distance = float('inf')

#Survivor location for L2 searches
L2_survivor = None

#Store all the survivor locations that have been found
survivors_found_locations = []

#Stores of the L2s that are attending to a survivor
L2s_attending = []

#Store the next cells for L1s and L2s
next_cell = None #this is for L1s, named like this due to the next cell variable previously being for both kinds of drones
L2_next_cell = None

#Indexes to keep track of the current node in the shortest path
#L1 indexes
if multiple_L1s_input > 1:
    to_survivor_path_index = []
    for L1_id in range(multiple_L1s_input):
        to_survivor_path_index.append(0)
else:
    to_survivor_path_index = 0

if multiple_L1s_input > 1:
    to_exit_path_index = []
    for L1_id in range(multiple_L1s_input):
        to_exit_path_index.append(0)
else:
    to_exit_path_index = 0

if multiple_L1s_input > 1:
    to_survivor_with_a_survivor_path_index = []
    for L1_id in range(multiple_L1s_input):
        to_survivor_with_a_survivor_path_index.append(0)
else:
    to_survivor_with_a_survivor_path_index = 0
#L2 indexes
if multiple_L2s_input > 1: #when there are multiple L2s create an index for each of them
    random_search_index = []
    for L2_id in range(multiple_L2s_input):
        random_search_index.append(0)
else: #else just set the variable to contain the index
    random_search_index = 0

if multiple_L2s_input > 1: #when there are multiple L2s create an index for each of them
    lawnmower_search_index = []
    for L2_id in range(multiple_L2s_input):
        lawnmower_search_index.append(0)
else: #else just set the variable to contain the index
    lawnmower_search_index = 0

#Path initialisation
#This isn't required when there is only one L1
if multiple_L1s_input > 1:
    shortest_path_to_exit = []
    for L1_id in range(multiple_L1s_input):
        shortest_path_to_exit.append(None)

if multiple_L1s_input > 1:
    to_closest_survivor_path = []
    for L1_id in range(multiple_L1s_input):
        to_closest_survivor_path.append(None)

#L1 Main Loop path categorisation
#This isn't required when there is only one L1
#0 means that the L1 is going to their target survivor whilst guiding, 1 means the L1 is returning to the exit, and 2 means that the L1 is moving to their target survivor
if multiple_L1s_input > 1:
    L1_movement_type = []
    for L1_id in range(multiple_L1s_input):
        L1_movement_type.append(2) #initialised as going to target survivor

##Variables for changing the parameters in the start screen##
#This is for text inputs at the start
user_input = ""
grid_size_temp = str(grid_size_input)
num_survivors_temp = str(num_survivors_input)
search_type_temp = str(search_type_input)
multiple_L1s_temp = str(multiple_L1s_input)
multiple_L2s_temp = str(multiple_L2s_input)
start_input = 1

##Variables to contain stats for the end screen##
time_2_find_and_save_all_survivors = 0
time_2_find_and_save_all_survivors_temp = 0
all_times_2_find_and_save_all_survivors = []
time_2_find_and_save_all_survivors_average = 0
''' These variables are no longer needed
#L2 distance to survivor
cells_2_find_first_survivor = 0
cells_2_find_last_survivor = 0
cells_2_find_survivors = []
cells_average_2_find_survivor = 0
cells_2_find_all_survivors = 0

#L1 distance to survivor
cells_2_save_first_survivor = 0
cells_2_save_last_survivor = 0
cells_2_save_survivors = []
cells_average_2_save_survivor = 0
cells_2_save_all_survivors = 0

#L1 time to survivor
time_2_save_first_survivor = 0
time_2_save_last_survivor = 0
time_2_save_survivors = []
time_average_2_save_survivor = 0
time_2_save_all_survivors = 0
'''

##Variables for end screen calculations##
#This is also keeping track of how many survivors have been saved and how many are being guided#
current_num_survivors = 10 #default of 10
if multiple_L1s_input > 1: #when there are multiple L1s
    num_guiding_survivors = []
    for L1_id in range(multiple_L1s_input):
        num_guiding_survivors.append(0) #default of 0
else: #when there is only one L1
    num_guiding_survivors = 0 #default of 0

#Only for end screen
''' Calculations for stats no longer needed
if multiple_L2s_input > 1: #when there are multiple L2s create an index for each of them
    L2_cells_travelled = []
    for L2_id in range(multiple_L2s_input):
        L2_cells_travelled.append(0)
else: #else just set the variable to contain the index
    L2_cells_travelled = 0

if multiple_L2s_input > 1: #when there are multiple L2s create an index for each of them
    L2_cells_travelled_for_last_survivor = []
    for L2_id in range(multiple_L2s_input):
        L2_cells_travelled_for_last_survivor.append(0)
else: #else just set the variable to contain the index
    L2_cells_travelled_for_last_survivor = 0

if multiple_L1s_input > 1:
    L1_cells_travelled = []
    for L1_id in range(multiple_L1s_input):
        L1_cells_travelled.append(0)
else:
    L1_cells_travelled = 0

if multiple_L1s_input > 1:
    L1_cells_travelled_for_last_survivor = []
    for L1_id in range(multiple_L1s_input):
        L1_cells_travelled_for_last_survivor.append(0)
else:
    L1_cells_travelled_for_last_survivor = 0

if multiple_L1s_input > 1:
    L1_time_travelled = []
    for L1_id in range(multiple_L1s_input):
        L1_time_travelled.append(0)
else:
    L1_time_travelled = 0

if multiple_L1s_input > 1:
    L1_time_travelled_for_last_survivor = []
    for L1_id in range(multiple_L1s_input):
        L1_time_travelled_for_last_survivor.append(0)
else:
    L1_time_travelled_for_last_survivor = 0

#For averages calculations
current_survivor = 0

if multiple_L1s_input > 1:
    L1_current_survivor = []
    for L1_id in range(multiple_L1s_input):
        L1_current_survivor.append(0)
else:
    L1_current_survivor = 0

if multiple_L2s_input > 1: #when there are multiple L2s create an index for each of them
    L2_cells_travelled_to_next_survivor = []
    for L2_id in range(multiple_L2s_input):
        L2_cells_travelled_to_next_survivor.append(0)
else: #else just set the variable to contain the index
    L2_cells_travelled_to_next_survivor = 0

if multiple_L1s_input > 1:
    L1_cells_travelled_to_next_survivor = []
    for L1_id in range(multiple_L1s_input):
        L1_cells_travelled_to_next_survivor.append(0)
else:
    L1_cells_travelled_to_next_survivor = 0

if multiple_L1s_input > 1:
    L1_time_travelled_to_next_survivor = []
    for L1_id in range(multiple_L1s_input):
        L1_time_travelled_to_next_survivor.append(0)
else:
    L1_time_travelled_to_next_survivor = 0
'''

##Booleans##
#Boolean to detirmine whether to show the start screen
start_screen = True
#Boolean to determine whether to show the end screen
end_screen = False
#Boolean to determine whether simulation is on
simulation = False
#Boolean to determine whether is going to towards target survivor
if multiple_L1s_input > 1: #when there are multiple L1s
    going_to_target = []
    for L1_id in range(multiple_L1s_input):
        going_to_target.append(True)
else: #when there is only one L1
    going_to_target = True
#Boolean to determine whether the L2s are searching
if multiple_L2s_input > 1: #when there is multiple L2s
    searching = []
    for L2_id in range(multiple_L2s_input):
        searching.append(True)
else: #when there is only 1 L1
    searching = True

##Main Loop##
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        ###Registering key presses###
        elif event.type == pygame.KEYDOWN:
            ###Key presses for the start screen###
            if start_screen:
                #When spacebar is pressed execute this code and go to simulation
                if event.key == pygame.K_SPACE:
                    ##Switch off the start screen##
                    start_screen = False
                    
                    ##Assigning the inputs from the user inputs in the start screen##
                    grid_size_input = int(grid_size_temp) #sets the value of input to temp
                    num_survivors_input = int(num_survivors_temp)
                    current_num_survivors = int(num_survivors_temp)
                    search_type_input = int(search_type_temp)
                    current_survivor = int(num_survivors_temp)
                    multiple_L1s_input = int(multiple_L1s_temp)
                    multiple_L2s_input = int(multiple_L2s_temp)
                    
                    ##Grid related##
                    #Grid size with same width and height (amount of cells)
                    GRID_SIZE = grid_size_input
                    
                    font = pygame.font.Font(None, int(540/GRID_SIZE)) #setting up the font size
                    small_font_size = int((540/GRID_SIZE)/2)
                    small_font = pygame.font.Font(None, small_font_size) #setting up font and font size
                    
                    screen.fill((WHITE))  #Filling the screen white
                    
                    #Cell size
                    CELL_SIZE = screen_width // GRID_SIZE
                    #Generate 2D grid
                    grid = [[None for i in range(GRID_SIZE)] for i in range(GRID_SIZE)]
                    
                    ##Multiple UAV variables that need to be redone when the amount of UAVs changes##
                    #Indexes to keep track of the current node in the shortest path
                    #L1 indexes
                    if multiple_L1s_input > 1:
                        to_survivor_path_index = []
                        for L1_id in range(multiple_L1s_input):
                            to_survivor_path_index.append(0)
                    else:
                        to_survivor_path_index = 0

                    if multiple_L1s_input > 1:
                        to_exit_path_index = []
                        for L1_id in range(multiple_L1s_input):
                            to_exit_path_index.append(0)
                    else:
                        to_exit_path_index = 0

                    if multiple_L1s_input > 1:
                        to_survivor_with_a_survivor_path_index = []
                        for L1_id in range(multiple_L1s_input):
                            to_survivor_with_a_survivor_path_index.append(0)
                    else:
                        to_survivor_with_a_survivor_path_index = 0
                    #L2 indexes
                    if multiple_L2s_input > 1: #when there are multiple L2s create an index for each of them
                        random_search_index = []
                        for L2_id in range(multiple_L2s_input):
                            random_search_index.append(0)
                    else: #else just set the variable to contain the index
                        random_search_index = 0

                    if multiple_L2s_input > 1: #when there are multiple L2s create an index for each of them
                        lawnmower_search_index = []
                        for L2_id in range(multiple_L2s_input):
                            lawnmower_search_index.append(0)
                    else: #else just set the variable to contain the index
                        lawnmower_search_index = 0

                    #Path initialisation
                    #This isn't required when there is only one L1
                    if multiple_L1s_input > 1:
                        shortest_path_to_exit = []
                        for L1_id in range(multiple_L1s_input):
                            shortest_path_to_exit.append(None)

                    if multiple_L1s_input > 1:
                        to_closest_survivor_path = []
                        for L1_id in range(multiple_L1s_input):
                            to_closest_survivor_path.append(None)

                    #L1 Main Loop path categorisation
                    #This isn't required when there is only one L1
                    #0 means that the L1 is going to their target survivor whilst guiding, 1 means the L1 is returning to the exit, and 2 means that the L1 is moving to their target survivor
                    if multiple_L1s_input > 1:
                        L1_movement_type = []
                        for L1_id in range(multiple_L1s_input):
                            L1_movement_type.append(2) #initialised as going to target survivor
                    
                    #This is also keeping track of how many survivors have been saved and how many are being guided#
                    if multiple_L1s_input > 1: #when there are multiple L1s
                        num_guiding_survivors = []
                        for L1_id in range(multiple_L1s_input):
                            num_guiding_survivors.append(0) #default of 0
                    else: #when there is only one L1
                        num_guiding_survivors = 0 #default of 0
                    
                    #Boolean to determine whether is going to towards target survivor
                    if multiple_L1s_input > 1: #when there are multiple L1s
                        going_to_target = []
                        for L1_id in range(multiple_L1s_input):
                            going_to_target.append(True)
                    else: #when there is only one L1
                        going_to_target = True
                    #Boolean to determine whether the L2s are searching
                    if multiple_L2s_input > 1: #when there is multiple L2s
                        searching = []
                        for L2_id in range(multiple_L2s_input):
                            searching.append(True)
                    else: #when there is only 1 L1
                        searching = True
                    
                    ##Generate the environment##
                    environment()
                    
                    ##Find whats located in the environment##
                    #Find where the L1 starts
                    for x in range(GRID_SIZE):
                        for y in range(GRID_SIZE):
                            #print("What does grid[x][y][5][1] equal? " + str(grid[x][y][5][1]))
                            if grid[x][y][5][1] == 1 or grid[x][y][5][1]:  #check for the L1 being either a 1 or a non empty list
                                if multiple_L1s_input > 1: #when there is more than 1 L1
                                    L1_coords = []
                                    print("Amount of L1s: ", multiple_L1s_input)
                                    for L1_id in range(multiple_L1s_input):
                                        L1_coords.append([(x, y), L1_id]) #set the L1 coords for every L1 along with the L1 id
                                        print("L1_coords when multiple: ", L1_coords)
                                else: #when then is only 1 L1
                                    print("Amount of L1s: ", multiple_L1s_input)
                                    L1_coords = (x, y) #set L1 coords
                                    print("L1_coords when singular: ", L1_coords)
                                
                                Exit = (x, y) #set exit coords
                                grid[x][y][5][3] = "E" #add the exit to the cell settings so it can be drawn
                                
                                if multiple_L2s_input > 1: #when there is more than 1 L2
                                    L2_coords = []
                                    print("Amount of L2s: ", multiple_L2s_input)
                                    for L2_id in range(multiple_L2s_input):
                                        L2_coords.append([(x, y), L2_id]) #set the L2 coords for every L2 along with the L2 id
                                        print("L2_coords when multiple: ", L2_coords)
                                else: #when there is only 1 L2
                                    print("Amount of L2s: ", multiple_L2s_input)
                                    L2_coords = (x, y) #set L2 coords
                                    print("L2_coords when singular: ", L2_coords)
                                break
                        #if L1_coords:
                            #print("Break activates")
                            #break
                    
                    ##Search type variable recieving the value from the user input##
                    #1 = closest survivor search (omniscient), 2 = random L2 search, 3 = dijkstra L2 search
                    search_type = search_type_input

                    #Boolean to deterimine if L2 is searching or not
                    if search_type == 1:
                        searching = False
                    #else:
                    #    searching = True
                    
                    #Find the closest survivor to the L1 and/or set up assignments variable
                    if multiple_L1s_input > 1: #when there are multiple L1s in the sim
                        print("Start of multiple L1 closest survivor")
                        #A list of all the available survivors
                        available_survivors = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if grid[x][y][5][0] == "S"]
                        print("Survivors available for rescue: " + str(available_survivors))
                        assignments = [] #an empty list for storing assigned survivor locations with the L1 asigned to it
                        if search_type == 1: #when omniscient search
                            switch = None #to make sure that available survivors and assignments are only used when needed
                            
                            for L1_id in range(multiple_L1s_input):
                                for x in range(GRID_SIZE):
                                    for y in range(GRID_SIZE):
                                        #Check if there is a survivor and that it is an available one and makes sur the the current L1 isnt occupied else where
                                        #print("Is the if statement working? grid[x][y][5][0] (" + str(grid[x][y][5][0]) + ") == 'S' and " + str((x, y)) + " is in " + str(available_survivors))# + " and is L1_id " + str(L1_id) + " is inside assignments is " + str(any(L1_id not in sublist for sublist in assignments)) + " where assignments is " + str(assignments))
                                        if grid[x][y][5][0] == "S" and (x, y) in available_survivors:
                                            print("The L1 coords: " + str(L1_coords))
                                            distance = math.sqrt((x - L1_coords[L1_id][0][0])**2 + (y - L1_coords[L1_id][0][1])**2)  #euclidean distance
                                            print("The distance is and the closest distance is: " + str(distance) + " < " + str(closest_distance))
                                            if distance < closest_distance:
                                                closest_survivor = (x, y)
                                                closest_distance = distance
                                                switch = True #enabling available_survivors and assignments to be used
                                print("Switch: " + str(switch))
                                if switch:
                                    print("Switch activated")
                                    closest_distance = float('inf')
                                    available_survivors.remove(closest_survivor)
                                    assignments.append(closest_survivor) #don't need to append the L1 id as the index already acts as it
                                    switch = False
                        
                        else: #when it is any other search type
                            for L1_id in range(multiple_L1s_input):
                                assignments.append(None) #this is for just setting up the assignments variable and doesn't have anything to do with finding the closest survivor in this case
                        
                    else: #when there is only 1 L1 in the sim
                        for x in range(GRID_SIZE):
                            for y in range(GRID_SIZE):
                                if grid[x][y][5][0] == "S":  #check if there is a survivor
                                    distance = math.sqrt((x - L1_coords[0])**2 + (y - L1_coords[1])**2)  #euclidean distance
                                    if distance < closest_distance:
                                        closest_survivor = (x, y)
                                        closest_distance = distance
                    
                    ##Dijkstra algorithms##
                    if search_type == 1:
                        #Dijkstra for omniscient/full coverage search
                        if multiple_L1s_input > 1: #when there are multiple L1s
                            to_closest_survivor_path = []
                            for L1_id in range(multiple_L1s_input):
                                #Dijkstra from L1 to closest survivor (this is the default)
                                print("L1 id: " + str(L1_id))
                                print("L1 coords: " + str(L1_coords[L1_id][0]))
                                print("Assignments: " + str(assignments))
                                print("Survivor assiged to the current L1: " + str(assignments[L1_id]))
                                to_closest_survivor_path.append(dijkstra(L1_coords[L1_id][0], assignments[L1_id], grid, 1, None))
                                print("Omniceint paths: " + str(to_closest_survivor_path))
                        else: #when there is only 1 L1
                            #Dijkstra from L1 to closest survivor (this is the default)
                            to_closest_survivor_path = dijkstra(L1_coords, closest_survivor, grid, 1, None)
                            #print(to_closest_survivor_path)
                    
                    elif search_type == 2:
                        #Dijkstra for random search
                        if multiple_L2s_input > 1: #when there is more than 1 
                            random_search = []
                            for L2_id in range(multiple_L2s_input):
                                random_location = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                                print("L2 coords[L2_id][0]: ", L2_coords[L2_id][0], " random location: ", random_location)
                                random_search.append(dijkstra(L2_coords[L2_id][0], random_location, grid, 4, None))
                                print("Random search with multiple L2s: ", random_search)
                        else: #when there is only 1 L2
                            random_location = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                            random_search = dijkstra(L2_coords, random_location, grid, 4, None)
                            print("Random search with one L2: ", random_search)
                    
                    elif search_type == 3:
                        #Dijkstra for Lawnmower search which is for searching the grid
                        if multiple_L2s_input > 1: #when there is more than 1 L2
                            lawnmower_search = []
                            unvisited_cells = []
                            
                            for L2_id in range(multiple_L2s_input):
                                print(L2_id)
                                print((GRID_SIZE/multiple_L2s_input)*(L2_id+1))
                                #The unvisted cells are constructed for each L2 to have their own area to search. The Y coord is divided between the different L2s.
                                unvisited_cells.append([(x, y) for x in range(GRID_SIZE) for y in range(int((GRID_SIZE/multiple_L2s_input)*(L2_id)), int((GRID_SIZE/multiple_L2s_input)*(L2_id+1)))])
                                print("The L2 " + str(L2_id) + " id has these unvisited cells " + str(unvisited_cells[L2_id]))
                                lawnmower_search.append(dijkstra(L2_coords[L2_id][0], None, grid, 5, unvisited_cells[L2_id]))
                                print("Lawnmower search with multiple L2: ", lawnmower_search)
                            
                        else: #when there is only 1 L2
                            unvisited_cells = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
                            lawnmower_search = dijkstra(L2_coords, None, grid, 5, unvisited_cells)
                            print("Lawnmower search with one L2: ", lawnmower_search)
                    
                    #!End of code that executes when space is pressed!#
                        
                ###Taking inputs from the user###
                #This section happens before the code that executes via the spacebar above
                if start_input == 1: #grid size input
                    if event.key == pygame.K_RETURN: #moving on to the next input
                        user_input = ""
                        start_input = 2
                    elif event.key == pygame.K_BACKSPACE: #removing whats been inputted
                        user_input = user_input[:-1]
                        grid_size_temp = grid_size_temp[:-1]
                    else: #typing
                        user_input += event.unicode
                        grid_size_temp += event.unicode
                        print("User input: " + str(user_input))
                
                elif start_input == 2: #number of survivors input
                    if event.key == pygame.K_RETURN: #moving on to the next input
                        user_input = ""
                        start_input = 3
                    elif event.key == pygame.K_BACKSPACE: #removing whats been inputted
                        user_input = user_input[:-1]
                        num_survivors_temp = num_survivors_temp[:-1]
                    else: #typing
                        user_input += event.unicode
                        num_survivors_temp += event.unicode
                        print("User input: " + str(user_input))
                
                elif start_input == 3: #search type input
                    if event.key == pygame.K_RETURN: #moving on to the next input
                        user_input = ""
                        start_input = 4
                    elif event.key == pygame.K_BACKSPACE: #removing whats been inputted
                        user_input = user_input[:-1]
                        search_type_temp = search_type_temp[:-1]
                    else: #typing
                        user_input += event.unicode
                        search_type_temp += event.unicode
                        print("User input: " + str(user_input))
                
                elif start_input == 4: #search type input
                    if event.key == pygame.K_RETURN: #moving on to the next input
                        user_input = ""
                        start_input = 5
                    elif event.key == pygame.K_BACKSPACE: #removing whats been inputted
                        user_input = user_input[:-1]
                        multiple_L1s_temp = multiple_L1s_temp[:-1]
                    else: #typing
                        user_input += event.unicode
                        multiple_L1s_temp += event.unicode
                        print("User input: " + str(user_input))
                
                elif start_input == 5: #search type input
                    if event.key == pygame.K_RETURN: #moving on to the next input
                        user_input = ""
                        start_input = 1
                    elif event.key == pygame.K_BACKSPACE: #removing whats been inputted
                        user_input = user_input[:-1]
                        multiple_L2s_temp = multiple_L2s_temp[:-1]
                    else: #typing
                        user_input += event.unicode
                        multiple_L2s_temp += event.unicode
                        print("User input: " + str(user_input))
            
            ###Key presses for the end screen###
            elif end_screen:
                #When space key is pressed at the end screen end the sim
                if event.key == pygame.K_SPACE:
                    pygame.quit()
                if event.key == pygame.K_RETURN: #restart the sim
                    ##Switch off the end screen##
                    end_screen = False
                    
                    ##Stats##
                    time_2_find_and_save_all_survivors = 0 #reset back to 0
                    
                    ##Assigning the inputs from the user inputs in the start screen##
                    grid_size_input = int(grid_size_temp) #sets the value of input to temp
                    num_survivors_input = int(num_survivors_temp)
                    current_num_survivors = int(num_survivors_temp)
                    search_type_input = int(search_type_temp)
                    current_survivor = int(num_survivors_temp)
                    
                    ##Reset all the indexes for the new run
                    #L1 indexes
                    if multiple_L1s_input > 1:
                        to_survivor_path_index = []
                        for L1_id in range(multiple_L1s_input):
                            to_survivor_path_index.append(0)
                    else:
                        to_survivor_path_index = 0

                    if multiple_L1s_input > 1:
                        to_exit_path_index = []
                        for L1_id in range(multiple_L1s_input):
                            to_exit_path_index.append(0)
                    else:
                        to_exit_path_index = 0

                    if multiple_L1s_input > 1:
                        to_survivor_with_a_survivor_path_index = []
                        for L1_id in range(multiple_L1s_input):
                            to_survivor_with_a_survivor_path_index.append(0)
                    else:
                        to_survivor_with_a_survivor_path_index = 0
                    #L2 indexes
                    if multiple_L2s_input > 1: #when there are multiple L2s create an index for each of them
                        random_search_index = []
                        for L2_id in range(multiple_L2s_input):
                            random_search_index.append(0)
                    else: #else just set the variable to contain the index
                        random_search_index = 0

                    if multiple_L2s_input > 1: #when there are multiple L2s create an index for each of them
                        lawnmower_search_index = []
                        for L2_id in range(multiple_L2s_input):
                            lawnmower_search_index.append(0)
                    else: #else just set the variable to contain the index
                        lawnmower_search_index = 0
                    
                    ##Grid related##
                    #These are needed for the endscreen one as without it returns to default values
                    #Grid size with same width and height (amount of cells)
                    GRID_SIZE = grid_size_input
                    
                    font = pygame.font.Font(None, int(540/GRID_SIZE)) #setting up the font size
                    small_font_size = int((540/GRID_SIZE)/2)
                    small_font = pygame.font.Font(None, small_font_size) #setting up font and font size
                    
                    screen.fill((WHITE))  #Filling the screen white
                    
                    #Cell size
                    CELL_SIZE = screen_width // GRID_SIZE
                    #Generate 2D grid
                    grid = [[None for i in range(GRID_SIZE)] for i in range(GRID_SIZE)]
                    
                    ##Generate the environment##
                    environment()
                    
                    ##Scrub all old UAVs and exit from the previous run##
                    #Find where the L1 starts
                    print("UAV_x_location is", UAV_x_location)
                    print("UAV_y_location is", UAV_y_location)
                    for x in range(GRID_SIZE):
                        for y in range(GRID_SIZE):
                            if x != UAV_x_location and y != UAV_y_location:
                                if grid[x][y][5][1] == 1 or grid[x][y][5][1]: #check for the L1 being either a 1 or a non empty list
                                    grid[x][y][5][1] = [] #remove any L1s from this space
                                elif grid[x][y][5][2] == 2 or grid[x][y][5][2]: #check for the L2 being either a 1 or a non empty list
                                    grid[x][y][5][2] = [] #remove any L2s from this space
                                elif grid[x][y][5][3] == "E": #check for old exit
                                    grid[x][y][5][3] = None
                    
                    ##Find whats located in the environment##
                    #Find where the L1 starts
                    for x in range(GRID_SIZE):
                        for y in range(GRID_SIZE):
                            print("x =", x, "and y =", y)
                            print("What does grid[x][y][5][1] equal? " + str(grid[x][y][5][1]))
                            if grid[x][y][5][1] == 1 or grid[x][y][5][1]: #check for the L1 being either a 1 or a non empty list
                                if multiple_L1s_input > 1: #when there is more than 1 L1
                                    L1_coords = []
                                    print("Amount of L1s: ", multiple_L1s_input)
                                    for L1_id in range(multiple_L1s_input):
                                        L1_coords.append([(x, y), L1_id]) #set the L1 coords for every L1 along with the L1 id
                                        print("L1_coords when multiple: ", L1_coords)
                                else: #when then is only 1 L1
                                    print("Amount of L1s: ", multiple_L1s_input)
                                    L1_coords = (x, y) #set L1 coords
                                    print("L1_coords when singular: ", L1_coords)
                                
                                Exit = (x, y) #set exit coords
                                grid[x][y][5][3] = "E" #add the exit to the cell settings so it can be drawn
                                
                                if multiple_L2s_input > 1: #when there is more than 1 L2
                                    L2_coords = []
                                    print("Amount of L2s: ", multiple_L2s_input)
                                    for L2_id in range(multiple_L2s_input):
                                        L2_coords.append([(x, y), L2_id]) #set the L2 coords for every L2 along with the L2 id
                                        print("L2_coords when multiple: ", L2_coords)
                                else: #when there is only 1 L2
                                    print("Amount of L2s: ", multiple_L2s_input)
                                    L2_coords = (x, y) #set L2 coords
                                    print("L2_coords when singular: ", L2_coords)
                                break
                        #if L1_coords:
                            #print("Break activates")
                            #break
                    
                    ##Search type variable recieving the value from the user input##
                    #1 = closest survivor search (omniscient), 2 = random L2 search, 3 = dijkstra L2 search
                    search_type = search_type_input

                    #Boolean to deterimine if L2 is searching or not
                    if search_type == 1:
                        searching = False
                    #else:
                    #    searching = True
                    
                    #Find the closest survivor to the L1 and/or set up assignments variable
                    if multiple_L1s_input > 1: #when there are multiple L1s in the sim
                        print("Start of multiple L1 closest survivor")
                        #A list of all the available survivors
                        available_survivors = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if grid[x][y][5][0] == "S"]
                        print("Survivors available for rescue: " + str(available_survivors))
                        assignments = [] #an empty list for storing assigned survivor locations with the L1 asigned to it
                        if search_type == 1: #when omniscient search
                            switch = None #to make sure that available survivors and assignments are only used when needed
                            
                            for L1_id in range(multiple_L1s_input):
                                for x in range(GRID_SIZE):
                                    for y in range(GRID_SIZE):
                                        #Check if there is a survivor and that it is an available one and makes sur the the current L1 isnt occupied else where
                                        #print("Is the if statement working? grid[x][y][5][0] (" + str(grid[x][y][5][0]) + ") == 'S' and " + str((x, y)) + " is in " + str(available_survivors))# + " and is L1_id " + str(L1_id) + " is inside assignments is " + str(any(L1_id not in sublist for sublist in assignments)) + " where assignments is " + str(assignments))
                                        if grid[x][y][5][0] == "S" and (x, y) in available_survivors:
                                            print("The L1 coords: " + str(L1_coords))
                                            distance = math.sqrt((x - L1_coords[L1_id][0][0])**2 + (y - L1_coords[L1_id][0][1])**2)  #euclidean distance
                                            print("The distance is and the closest distance is: " + str(distance) + " < " + str(closest_distance))
                                            if distance < closest_distance:
                                                closest_survivor = (x, y)
                                                closest_distance = distance
                                                switch = True #enabling available_survivors and assignments to be used
                                print("Switch: " + str(switch))
                                if switch:
                                    print("Switch activated")
                                    closest_distance = float('inf')
                                    available_survivors.remove(closest_survivor)
                                    assignments.append(closest_survivor) #don't need to append the L1 id as the index already acts as it
                                    switch = False
                        
                        else: #when it is any other search type
                            for L1_id in range(multiple_L1s_input):
                                assignments.append(None) #this is for just setting up the assignments variable and doesn't have anything to do with finding the closest survivor in this case
                        
                    else: #when there is only 1 L1 in the sim
                        for x in range(GRID_SIZE):
                            for y in range(GRID_SIZE):
                                if grid[x][y][5][0] == "S":  #check if there is a survivor
                                    distance = math.sqrt((x - L1_coords[0])**2 + (y - L1_coords[1])**2)  #euclidean distance
                                    if distance < closest_distance:
                                        closest_survivor = (x, y)
                                        closest_distance = distance
                    
                    ##Dijkstra algorithms##
                    if search_type == 1:
                        #Dijkstra for omniscient/full coverage search
                        if multiple_L1s_input > 1: #when there are multiple L1s
                            to_closest_survivor_path = []
                            for L1_id in range(multiple_L1s_input):
                                #Dijkstra from L1 to closest survivor (this is the default)
                                print("L1 id: " + str(L1_id))
                                print("L1 coords: " + str(L1_coords[L1_id][0]))
                                print("Assignments: " + str(assignments))
                                print("Survivor assiged to the current L1: " + str(assignments[L1_id]))
                                to_closest_survivor_path.append(dijkstra(L1_coords[L1_id][0], assignments[L1_id], grid, 1, None))
                                print("Omniceint paths: " + str(to_closest_survivor_path))
                        else: #when there is only 1 L1
                            #Dijkstra from L1 to closest survivor (this is the default)
                            to_closest_survivor_path = dijkstra(L1_coords, closest_survivor, grid, 1, None)
                            #print(to_closest_survivor_path)
                    
                    elif search_type == 2:
                        #Dijkstra for random search
                        if multiple_L2s_input > 1: #when there is more than 1 
                            random_search = []
                            for L2_id in range(multiple_L2s_input):
                                random_location = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                                print("L2 coords[L2_id][0]: ", L2_coords[L2_id][0], " random location: ", random_location)
                                random_search.append(dijkstra(L2_coords[L2_id][0], random_location, grid, 4, None))
                                print("Random search with multiple L2s: ", random_search)
                        else: #when there is only 1 L2
                            random_location = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                            random_search = dijkstra(L2_coords, random_location, grid, 4, None)
                            print("Random search with one L2: ", random_search)
                    
                    elif search_type == 3:
                        #Dijkstra for Lawnmower search which is for searching the grid
                        if multiple_L2s_input > 1: #when there is more than 1 L2
                            lawnmower_search = []
                            unvisited_cells = []
                            
                            for L2_id in range(multiple_L2s_input):
                                print(L2_id)
                                print((GRID_SIZE/multiple_L2s_input)*(L2_id+1))
                                #The unvisted cells are constructed for each L2 to have their own area to search. The Y coord is divided between the different L2s.
                                unvisited_cells.append([(x, y) for x in range(GRID_SIZE) for y in range(int((GRID_SIZE/multiple_L2s_input)*(L2_id)), int((GRID_SIZE/multiple_L2s_input)*(L2_id+1)))])
                                print("The L2 " + str(L2_id) + " id has these unvisited cells " + str(unvisited_cells[L2_id]))
                                lawnmower_search.append(dijkstra(L2_coords[L2_id][0], None, grid, 5, unvisited_cells[L2_id]))
                                print("Lawnmower search with multiple L2: ", lawnmower_search)
                            
                        else: #when there is only 1 L2
                            unvisited_cells = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)]
                            lawnmower_search = dijkstra(L2_coords, None, grid, 5, unvisited_cells)
                            print("Lawnmower search with one L2: ", lawnmower_search)
                    
                    #!End of code that executes when enter is pressed!#

    ###Start screen###
    if start_screen:        
        draw_start()
    
    ###End screen###
    elif end_screen:        
        draw_end()
    
    ###Simulation###
    else:        
        flood_sim()
        draw_grid()
        
        ###L2 searching for a survivor###
        #The L2 searching section was previously in an if which was previously: if searching
        #print("Survivors: " + str(current_num_survivors))
        #print("Guiding: " + str(num_guiding_survivors))
        #print("Next L2 Cell: " + str(L2_next_cell)) #this will only work when there is 1 L2
        
        ###Random search###
        if search_type == 2:
            if multiple_L2s_input > 1: #when there is more than 1 L2
                if multiple_L1s_input > 1: #when there is more than 1 L1
                    print("--Start of multi L2 random search (with multiple L1s):")
                    for L2_id in range(multiple_L2s_input):
                        print("Random search for loop:")
                        ##If the L2 is adjacent to a survivor##
                        #Checks to see if L2 is adjacent to a survivor and that survivor isn't being guided by an L1
                        print("survivor_adjacent(L2_coords[L2_id][0], 2):", survivor_adjacent(L2_coords[L2_id][0], 2))
                        print("L1_coords:", L1_coords)
                        if survivor_adjacent(L2_coords[L2_id][0], 1) and survivor_adjacent(L2_coords[L2_id][0], 2) not in (L1_id for L1_id, _ in L1_coords):#any(L1 != survivor_adjacent(L2_coords[L2_id][0], 2) for sublist in L1_coords for L1 in sublist):# and (survivor_adjacent(L2_coords[L2_id][0], 2) not in survivors_found_locations): #first [] is for selecting the current specific L2 and then the next [] is for selecting the coords
                            #if L2_id in L2s_attending:
                            #    continue
                            print("Is searching true for L2", L2_id, "true:", searching[L2_id])
                            if searching[L2_id]:
                                #Update dijkstra for L1 so it goes to this survivor
                                #print("L2 coords: " + str(L2_coords))
                                #The L2_coords[L2_id][0] is making sure that only the coordinates are selected for the survivor adjacent function.
                                for L1_id in range(multiple_L1s_input): #loop for how many L1s there are
                                    print("Does L1", L1_id, "at cell", L1_coords[L1_id][0], "==", Exit, "and the of survivors being guided is", num_guiding_survivors[L1_id], "== 0 and", to_closest_survivor_path[L1_id], "== None and", survivor_adjacent(L2_coords[L2_id][0], 2), "is not in", assignments)
                                    if num_guiding_survivors[L1_id] == 0 and to_closest_survivor_path[L1_id] == None and survivor_adjacent(L2_coords[L2_id][0], 2) not in assignments: #check if the current L1 isn't guiding any survivors, has an empty path, and that the survivor that has been found hasn't already been assigned
                                        print("L2 " + str(L2_id) + " assigns this survivor to L1", L1_id)
                                        searching[L2_id] = False #switches off L2 searching
                                        
                                        #Create the path for the current L1
                                        to_closest_survivor_path[L1_id] = dijkstra(L1_coords[L1_id][0], survivor_adjacent(L2_coords[L2_id][0], 2), grid, 1, None) #creating the path for this L1 to the survivor the current L1 found
                                        
                                        #Stores survivor location
                                        L2_survivor = survivor_adjacent(L2_coords[L2_id][0], 2)
                                        #The survivor location is then assigned to the current L1
                                        assignments[L1_id] = L2_survivor
                                        
                                        #Append the L2 that is attending the found survivor
                                        L2s_attending.append(L2_id)
                                        #This is appended every everytime a survivor is found
                                        survivors_found_locations.append(L2_survivor)
                                        
                                        break #don't need to look at any other L1s as the path has been assigned
                                
                                #Stat checks
                                '''
                                if current_num_survivors == num_survivors_input:
                                    cells_2_find_first_survivor = L2_cells_travelled
                                if current_num_survivors == 1:
                                    cells_2_find_last_survivor = L2_cells_travelled_for_last_survivor
                                    cells_2_find_all_survivors = L2_cells_travelled
                                
                                #For average calculations
                                current_survivor -= 1
                                cells_2_find_survivors.append(L2_cells_travelled_to_next_survivor)
                                print("L2 cells travelled: " + str(L2_cells_travelled_to_next_survivor))
                                L2_cells_travelled_to_next_survivor = 0
                                '''
                        
                        ##Random movement around the grid##
                        elif random_search and random_search_index[L2_id] < len(random_search[L2_id]):
                            #If moving, then the L2 must be searching!
                            searching[L2_id] = True
                            
                            print("Moving current L2 " + str(L2_id) + " to it's next cell:")
                            next_cell = random_search[L2_id][random_search_index[L2_id]]
                            #print("Random search path: " + str(random_search))
                            #Update the L2's position
                            #The last [] is for either the x coord (0) and y coord (1). The [5][2] is for the specific spot in the cell settings
                            print("L2 IDs in current cell before remove: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                            #if len(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]) != 0:
                            grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2].remove(L2_id) #clear the cell of the current L2 id
                            #else:
                                #print("ERROR: Removal of an L2 from a cell didn't work!")
                            #print("L2 IDs in current cell after remove: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                            #print("L2 coords: " + str(L2_coords))
                            #print("L2 coords selecting [L2_id][0]: " + str(L2_coords[L2_id][0]))
                            #print("L2 next cell: " + str(next_cell))
                            L2_coords[L2_id][0] = next_cell
                            #print("L2 IDs in new current cell before append: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                            grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2].append(L2_id) #add the current L2 id in the new cell
                            #print("L2 IDs in new current cell after append: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                            
                            #Increase the index
                            random_search_index[L2_id] += 1
                            print("Index: " + str(random_search_index))
                            
                            #Increase cells traveled
                            '''
                            L2_cells_travelled += 1
                            if current_num_survivors == 1:
                                L2_cells_travelled_for_last_survivor += 1
                            
                            #For average calculations
                            L2_cells_travelled_to_next_survivor += 1
                            '''
                            
                            #Need to make random location = the last location for the current path
                            random_location = random_search[L2_id][-1]
                            if random_location == L2_coords[L2_id][0]:
                                print("Getting number " + str(L2_id) + " L2 for its new path:")
                                random_location = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                                #Pop old path
                                random_search.pop(L2_id)
                                #Insert needed hear as the new path needs to be in the specific index as each one is for a specific L2 path
                                random_search.insert(L2_id, dijkstra(L2_coords[L2_id][0], random_location, grid, 4, None))
                                #print(random_search)
                                random_search_index[L2_id] = 0
                            #After reaching the random location goes to a new one
                            print("Does the end of the path: " + str(random_location) + " equal the current coords: " + str(L2_coords[L2_id][0]) + " of number " + str(L2_id) + " L2.")
                        print("Checking to see if the elif for moving the L2s is working: Is " + str(random_search) + " and " + str(random_search_index[L2_id]) + " < " + str(len(random_search[L2_id])) + " true?")
            
                else: #when there is only 1 L1
                    print("Start of multi L2 random search (with 1 L1):")
                    for L2_id in range(multiple_L2s_input):
                        print("Random search for loop:")
                        ##If the L2 is adjacent to a survivor##
                        #Checks to see if L2 is adjacent to a survivor and that survivor isn't being guided by an L1
                        print("survivor_adjacent(L2_coords[L2_id][0], 2):", survivor_adjacent(L2_coords[L2_id][0], 2))
                        print("L1_coords:", L1_coords)
                        if survivor_adjacent(L2_coords[L2_id][0], 1) and survivor_adjacent(L2_coords[L2_id][0], 2) != L1_coords: #first [] is for selecting the current specific L2 and then the next [] is for selecting the coords
                            #if L2_id in L2s_attending:
                            #    continue
                            if searching:
                                print("L2 " + str(L2_id) + " is adjacent to a Survivor:")
                                searching = False #switches off L2 searching
                                #Update dijkstra for L1 so it goes to this survivor
                                #print("L2 coords: " + str(L2_coords))
                                #The L2_coords[L2_id][0] is making sure that only the coordinates are selected for the survivor adjacent function.
                                to_closest_survivor_path = dijkstra(L1_coords, survivor_adjacent(L2_coords[L2_id][0], 2), grid, 1, None)
                                #Stores survivor location
                                L2_survivor = survivor_adjacent(L2_coords[L2_id][0], 2)
                                #Append the L2 that is attending the found survivor
                                L2s_attending.append(L2_id)
                                #This is appended every everytime a survivor is found
                                survivors_found_locations.append(L2_survivor)
                                
                                #Stat checks
                                '''
                                if current_num_survivors == num_survivors_input:
                                    cells_2_find_first_survivor = L2_cells_travelled
                                if current_num_survivors == 1:
                                    cells_2_find_last_survivor = L2_cells_travelled_for_last_survivor
                                    cells_2_find_all_survivors = L2_cells_travelled
                                
                                #For average calculations
                                current_survivor -= 1
                                cells_2_find_survivors.append(L2_cells_travelled_to_next_survivor)
                                print("L2 cells travelled: " + str(L2_cells_travelled_to_next_survivor))
                                L2_cells_travelled_to_next_survivor = 0
                                '''
                        
                        ##Random movement around the grid##
                        elif random_search and random_search_index[L2_id] < len(random_search[L2_id]):
                            print("Moving current L2 " + str(L2_id) + " to it's next cell:")
                            next_cell = random_search[L2_id][random_search_index[L2_id]]
                            #print("Random search path: " + str(random_search))
                            #Update the L2's position
                            #The last [] is for either the x coord (0) and y coord (1). The [5][2] is for the specific spot in the cell settings
                            #print("L2 IDs in current cell before remove: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                            grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2].remove(L2_id) #clear the cell of the current L2 id
                            #print("L2 IDs in current cell after remove: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                            #print("L2 coords: " + str(L2_coords))
                            #print("L2 coords selecting [L2_id][0]: " + str(L2_coords[L2_id][0]))
                            #print("L2 next cell: " + str(next_cell))
                            L2_coords[L2_id][0] = next_cell
                            #print("L2 IDs in new current cell before append: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                            grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2].append(L2_id) #add the current L2 id in the new cell
                            #print("L2 IDs in new current cell after append: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                            
                            #Increase the index
                            random_search_index[L2_id] += 1
                            print("Index: " + str(random_search_index))
                            
                            #Increase cells traveled
                            '''
                            L2_cells_travelled += 1
                            if current_num_survivors == 1:
                                L2_cells_travelled_for_last_survivor += 1
                            
                            #For average calculations
                            L2_cells_travelled_to_next_survivor += 1
                            '''
                            
                            #After reaching the random location goes to a new one
                            print("Does the end of the path: " + str(random_location) + " equal the current coords: " + str(L2_coords[L2_id][0]) + " of number " + str(L2_id) + " L2.")
                            #Need to make random location = the last location for the current path
                            random_location = random_search[L2_id][-1]
                            if random_location == L2_coords[L2_id][0]:
                                print("Getting number " + str(L2_id) + " L2 for its new path:")
                                random_location = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                                #Pop old path
                                random_search.pop(L2_id)
                                #Insert needed hear as the new path needs to be in the specific index as each one is for a specific L2 path
                                random_search.insert(L2_id, dijkstra(L2_coords[L2_id][0], random_location, grid, 4, None))
                                #print(random_search)
                                random_search_index[L2_id] = 0
                        print("Checking to see if the elif for moving the L2s is working: Is " + str(random_search) + " and " + str(random_search_index[L2_id]) + " < " + str(len(random_search[L2_id])) + " true?")
            
            else: #when there is only 1 L2
                ##If the L2 is adjacent to a survivor##
                #Checks to see if L2 is adjacent to a survivor and that survivor isn't being guided by an L1
                #print("Adjacent survivor coords: " + str(survivor_adjacent(L2_coords, 2)) + " and L1 coords: " + str(L1_coords))
                if survivor_adjacent(L2_coords, 1) and survivor_adjacent(L2_coords, 2) != L1_coords:
                    if searching:
                        searching = False #switches off L2 searching
                        #Update dijkstra for L1 so it goes to this survivor
                        to_closest_survivor_path = dijkstra(L1_coords, survivor_adjacent(L2_coords, 2), grid, 1, None)
                        #Stores survivor location
                        L2_survivor = survivor_adjacent(L2_coords, 2)
                        survivors_found_locations.append(L2_survivor) #This is appended every loop the L2 is adjacent. Not needed to do this
                        
                        #Stat checks
                        '''
                        if current_num_survivors == num_survivors_input:
                            cells_2_find_first_survivor = L2_cells_travelled
                        if current_num_survivors == 1:
                            cells_2_find_last_survivor = L2_cells_travelled_for_last_survivor
                            cells_2_find_all_survivors = L2_cells_travelled
                        
                        #For average calculations
                        current_survivor -= 1
                        cells_2_find_survivors.append(L2_cells_travelled_to_next_survivor)
                        print("L2 cells travelled: " + str(L2_cells_travelled_to_next_survivor))
                        L2_cells_travelled_to_next_survivor = 0
                        '''
                
                ##Random movement around the grid##
                elif random_search and random_search_index < len(random_search):
                    L2_next_cell = random_search[random_search_index]
                    #Update the L2's position
                    print("L2 current cell before = None: " + str(grid[L2_coords[0]][L2_coords[1]][5][2]))
                    grid[L2_coords[0]][L2_coords[1]][5][2] = None #clear the previous L2 position
                    print("L2 current cell after = None: " + str(grid[L2_coords[0]][L2_coords[1]][5][2]))
                    print("L2 coords: " + str(L2_coords))
                    print("L2 next: " + str(L2_next_cell))
                    L2_coords = L2_next_cell
                    print("L2 new current cell before = 2: " + str(grid[L2_coords[0]][L2_coords[1]][5][2]))
                    grid[L2_coords[0]][L2_coords[1]][5][2] = 2 #set the new L2 position
                    print("L2 new current cell after = 2: " + str(grid[L2_coords[0]][L2_coords[1]][5][2]))
                    
                    #Increase the index
                    random_search_index += 1
                    
                    #Increase cells traveled
                    '''
                    L2_cells_travelled += 1
                    if current_num_survivors == 1:
                        L2_cells_travelled_for_last_survivor += 1
                    
                    #For average calculations
                    L2_cells_travelled_to_next_survivor += 1
                    '''
                    
                    #After reaching the random location goes to a new one
                    if random_location == L2_coords:
                        random_location = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                        random_search = dijkstra(L2_coords, random_location, grid, 4, None)
                        #print(random_search)
                        random_search_index = 0
                print("Checking to see if the elif for moving the L2s is working: Is " + str(random_search) + " and " + str(random_search_index) + " < " + str(len(random_search)) + " true?")
        
        ###Lawnmower search###
        elif search_type == 3:
            if multiple_L2s_input > 1: #when there is more than 1 L2
                if multiple_L1s_input > 1:
                    print("---Start of multi L2 lawnmower search (with multiple L1s):")
                    for L2_id in range(multiple_L2s_input):
                        print("--Lawnmower search for loop:")
                        ##If the L2 is adjacent to a survivor##
                        #Checks to see if L2 is adjacent to a survivor and that survivor isn't being guided by an L1
                        print("survivor_adjacent(L2_coords[L2_id][0], 2):", survivor_adjacent(L2_coords[L2_id][0], 2))
                        print("L1_coords:", L1_coords)
                        if lawnmower_search[L2_id] != None: #this is to handle if any of the L2s are at the end of its path as the lawnmower_search[L2_id] becomes none
                            ##If for making sure that L2s don't get stuck in visited cells##
                            print("The lawnmower search for the current id is " + str(lawnmower_search[L2_id]))
                            if lawnmower_search_index[L2_id] == len(lawnmower_search[L2_id]):
                                #Removing the specific path of the L2 and then readding the new one
                                lawnmower_search.pop(L2_id)
                                lawnmower_search.insert(L2_id, dijkstra(L2_coords[L2_id][0], None, grid, 5, unvisited_cells[L2_id]))
                                print("Lawnmower search: " + str(lawnmower_search))
                                lawnmower_search_index[L2_id] = 0
                            
                            ##If the L2s are adjacent to a survivor##
                            if survivor_adjacent(L2_coords[L2_id][0], 1) and survivor_adjacent(L2_coords[L2_id][0], 2) not in (L1_id for L1_id, _ in L1_coords):
                                print("Is searching true for L2", L2_id, "true:", searching[L2_id])
                                if searching[L2_id]:
                                    for L1_id in range(multiple_L1s_input): #loop for how many L1s there are
                                        print("Does L1", L1_id, "at cell", L1_coords[L1_id][0], "==", Exit, "and the of survivors being guided is", num_guiding_survivors[L1_id], "== 0 and", to_closest_survivor_path[L1_id], "== None and", survivor_adjacent(L2_coords[L2_id][0], 2), "is not in", assignments)
                                        if num_guiding_survivors[L1_id] == 0 and to_closest_survivor_path[L1_id] == None and survivor_adjacent(L2_coords[L2_id][0], 2) not in assignments: #check if the current L1 isn't guiding any survivors, has an empty path, and that the survivor that has been found hasn't already been assigned
                                            print("L2 " + str(L2_id) + " assigns this survivor to L1", L1_id)
                                            searching[L2_id] = False #switches off L2 searching
                                            
                                            #Create the path for the current L1
                                            to_closest_survivor_path[L1_id] = dijkstra(L1_coords[L1_id][0], survivor_adjacent(L2_coords[L2_id][0], 2), grid, 1, None) #creating the path for this L1 to the survivor the current L1 found
                                        
                                            #Stores survivor location
                                            L2_survivor = survivor_adjacent(L2_coords[L2_id][0], 2)
                                            #The survivor location is then assigned to the current L1
                                            assignments[L1_id] = L2_survivor
                                            
                                            #Append the L2 that is attending the found survivor
                                            L2s_attending.append(L2_id)
                                            #This is appended every everytime a survivor is found
                                            survivors_found_locations.append(L2_survivor)
                                    
                                    #Stat checks
                                    '''
                                    if current_num_survivors == num_survivors_input:
                                        cells_2_find_first_survivor = L2_cells_travelled
                                    if current_num_survivors == 1:
                                        cells_2_find_last_survivor = L2_cells_travelled_for_last_survivor
                                        cells_2_find_all_survivors = L2_cells_travelled
                                    
                                    #For average calculations
                                    current_survivor -= 1
                                    cells_2_find_survivors.append(L2_cells_travelled_to_next_survivor)
                                    L2_cells_travelled_to_next_survivor = 0
                                    '''
                            
                            ##Lawnmower movement around the grid##
                            elif lawnmower_search and lawnmower_search_index[L2_id] < len(lawnmower_search[L2_id]):
                                #If moving, then the L2 must be searching!
                                searching[L2_id] = True

                                print("Moving current L2 '" + str(L2_id) + "' to it's next cell:")
                                next_cell = lawnmower_search[L2_id][lawnmower_search_index[L2_id]]
                                
                                #Checks if not at starting point and that L2 coords and next cell equal each other
                                if not len(lawnmower_search[L2_id]) == 1:
                                    if L2_coords[L2_id][0] == next_cell:
                                        #Increase index and move to next cell
                                        lawnmower_search_index[L2_id] += 1
                                        next_cell = lawnmower_search[L2_id][lawnmower_search_index[L2_id]]
                                
                                print("Lawnmower search path: " + str(lawnmower_search))
                                #Update the L2's position
                                print("L2 IDs in current cell before remove: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                                grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2].remove(L2_id) #clear the cell of the current L2 id
                                print("L2 IDs in current cell after remove: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                                print("L2 coords: " + str(L2_coords))
                                print("L2 coords selecting [L2_id][0]: " + str(L2_coords[L2_id][0]))
                                print("L2 next cell: " + str(next_cell))
                                L2_coords[L2_id][0] = next_cell
                                print("L2 IDs in new current cell before append: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                                grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2].append(L2_id) #add the current L2 id in the new cell
                                print("L2 IDs in new current cell after append: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                                
                                #Increase the index
                                lawnmower_search_index[L2_id] += 1
                                print("Index: " + str(lawnmower_search_index))
                                
                                #Increase cells traveled
                                '''
                                L2_cells_travelled += 1
                                if current_num_survivors == 1:
                                    L2_cells_travelled_for_last_survivor += 1
                                
                                #For average calculations
                                L2_cells_travelled_to_next_survivor += 1
                                print("L2 cells travelled: " + str(L2_cells_travelled_to_next_survivor))
                                '''
                                
                                #After reaching the unvisted cell go to the next one
                                print("Does the next cell: " + str(next_cell) + " exist in the unvisited cells: " + str(unvisited_cells[L2_id]) + ".")
                                if next_cell in unvisited_cells[L2_id]:
                                    print("Getting number " + str(L2_id) + " L2 for its new path:")
                                    unvisited_cells[L2_id].remove(next_cell)
                                    
                                    #Removing the specific path of the L2 and then readding the new one
                                    lawnmower_search.pop(L2_id)
                                    lawnmower_search.insert(L2_id, dijkstra(L2_coords[L2_id][0], None, grid, 5, unvisited_cells[L2_id]))
                                    print("Lawnmower search: " + str(lawnmower_search))
                                    lawnmower_search_index[L2_id] = 0
                            #For some reason the print below causes an error somethimes???
                            #print("Checking to see if the elif for moving the L2s is working: Is " + str(lawnmower_search) + " and " + str(lawnmower_search_index[L2_id]) + " < " + str(len(lawnmower_search[L2_id])) + " true?")
                            print("The current interation of the loop for L2 '" + str(L2_id) + "' has ended:")
                    print("The for loop has ended.")
                
                else: #when there is only 1 L1
                    for L2_id in range(multiple_L2s_input):
                        if lawnmower_search[L2_id] != None: #this is to handle if any of the L2s are at the end of its path as the lawnmower_search[L2_id] becomes none
                            ##If for making sure that L2s don't get stuck in visited cells##
                            print("The lawnmower search for the current id is " + str(lawnmower_search[L2_id]))
                            if lawnmower_search_index[L2_id] == len(lawnmower_search[L2_id]):
                                #Removing the specific path of the L2 and then readding the new one
                                lawnmower_search.pop(L2_id)
                                lawnmower_search.insert(L2_id, dijkstra(L2_coords[L2_id][0], None, grid, 5, unvisited_cells[L2_id]))
                                print("Lawnmower search: " + str(lawnmower_search))
                                lawnmower_search_index[L2_id] = 0
                            
                            ##If the L2s are adjacent to a survivor##
                            if survivor_adjacent(L2_coords[L2_id][0], 1) and survivor_adjacent(L2_coords[L2_id][0], 2) != L1_coords:
                                if searching:
                                    searching = False #switches off L2 searching
                                    #Update dijkstra for L1 so it goes to this survivor
                                    to_closest_survivor_path = dijkstra(L1_coords, survivor_adjacent(L2_coords[L2_id][0], 2), grid, 1, None)
                                    #Stores survivor location
                                    L2_survivor = survivor_adjacent(L2_coords[L2_id][0], 2)
                                    #Append the L2 that is attending the found survivor
                                    L2s_attending.append(L2_id)
                                    #This is appended every everytime a survivor is found
                                    survivors_found_locations.append(L2_survivor)
                                    
                                    #Stat checks
                                    '''
                                    if current_num_survivors == num_survivors_input:
                                        cells_2_find_first_survivor = L2_cells_travelled
                                    if current_num_survivors == 1:
                                        cells_2_find_last_survivor = L2_cells_travelled_for_last_survivor
                                        cells_2_find_all_survivors = L2_cells_travelled
                                    
                                    #For average calculations
                                    current_survivor -= 1
                                    cells_2_find_survivors.append(L2_cells_travelled_to_next_survivor)
                                    L2_cells_travelled_to_next_survivor = 0
                                    '''
                            
                            ##Lawnmower movement around the grid##
                            elif lawnmower_search and lawnmower_search_index[L2_id] < len(lawnmower_search[L2_id]):
                                print("Moving current L2 '" + str(L2_id) + "' to it's next cell:")
                                next_cell = lawnmower_search[L2_id][lawnmower_search_index[L2_id]]
                                
                                #Checks if not at starting point and that L2 coords and next cell equal each other
                                if not len(lawnmower_search[L2_id]) == 1:
                                    if L2_coords[L2_id][0] == next_cell:
                                        #Increase index and move to next cell
                                        lawnmower_search_index[L2_id] += 1
                                        next_cell = lawnmower_search[L2_id][lawnmower_search_index[L2_id]]
                                
                                print("Lawnmower search path: " + str(lawnmower_search))
                                #Update the L2's position
                                print("L2 IDs in current cell before remove: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                                grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2].remove(L2_id) #clear the cell of the current L2 id
                                print("L2 IDs in current cell after remove: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                                print("L2 coords: " + str(L2_coords))
                                print("L2 coords selecting [L2_id][0]: " + str(L2_coords[L2_id][0]))
                                print("L2 next cell: " + str(next_cell))
                                L2_coords[L2_id][0] = next_cell
                                print("L2 IDs in new current cell before append: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                                grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2].append(L2_id) #add the current L2 id in the new cell
                                print("L2 IDs in new current cell after append: " + str(grid[L2_coords[L2_id][0][0]][L2_coords[L2_id][0][1]][5][2]))
                                
                                #Increase the index
                                lawnmower_search_index[L2_id] += 1
                                print("Index: " + str(lawnmower_search_index))
                                
                                #Increase cells traveled
                                '''
                                L2_cells_travelled += 1
                                if current_num_survivors == 1:
                                    L2_cells_travelled_for_last_survivor += 1
                                
                                #For average calculations
                                L2_cells_travelled_to_next_survivor += 1
                                print("L2 cells travelled: " + str(L2_cells_travelled_to_next_survivor))
                                '''
                                
                                #After reaching the unvisted cell go to the next one
                                print("Does the next cell: " + str(next_cell) + " exist in the unvisited cells: " + str(unvisited_cells[L2_id]) + ".")
                                if next_cell in unvisited_cells[L2_id]:
                                    print("Getting number " + str(L2_id) + " L2 for its new path:")
                                    unvisited_cells[L2_id].remove(next_cell)
                                    
                                    #Removing the specific path of the L2 and then readding the new one
                                    lawnmower_search.pop(L2_id)
                                    lawnmower_search.insert(L2_id, dijkstra(L2_coords[L2_id][0], None, grid, 5, unvisited_cells[L2_id]))
                                    print("Lawnmower search: " + str(lawnmower_search))
                                    lawnmower_search_index[L2_id] = 0
                            #For some reason the print below causes an error somethimes???
                            #print("Checking to see if the elif for moving the L2s is working: Is " + str(lawnmower_search) + " and " + str(lawnmower_search_index[L2_id]) + " < " + str(len(lawnmower_search[L2_id])) + " true?")
                            print("The current interation of the loop for L2 '" + str(L2_id) + "' has ended:")
                    print("The for loop has ended.")
            
            else: #when there is only 1 L2
                    ##If the L2 is adjacent to a survivor##
                    if survivor_adjacent(L2_coords, 1) and survivor_adjacent(L2_coords, 2) != L1_coords:
                        if searching:
                            searching = False #switches off L2 searching
                            #Update dijkstra for L1 so it goes to this survivor
                            to_closest_survivor_path = dijkstra(L1_coords, survivor_adjacent(L2_coords, 2), grid, 1, None)
                            #Stores survivor location
                            L2_survivor = survivor_adjacent(L2_coords, 2)
                            survivors_found_locations.append(L2_survivor) #This is appended every loop the L2 is adjacent. Not needed to do this
                            
                            #Stat checks
                            '''
                            if current_num_survivors == num_survivors_input:
                                cells_2_find_first_survivor = L2_cells_travelled
                            if current_num_survivors == 1:
                                cells_2_find_last_survivor = L2_cells_travelled_for_last_survivor
                                cells_2_find_all_survivors = L2_cells_travelled
                            
                            #For average calculations
                            current_survivor -= 1
                            cells_2_find_survivors.append(L2_cells_travelled_to_next_survivor)
                            L2_cells_travelled_to_next_survivor = 0
                            '''
                    
                    ##Movement to unvisited cells##
                    elif lawnmower_search and lawnmower_search_index < len(lawnmower_search):
                        next_cell = lawnmower_search[lawnmower_search_index]
                        
                        #Checks if not at starting point and that L2 coords and next cell equal each other
                        if not len(lawnmower_search) == 1:
                            if L2_coords == next_cell:
                                #Increase index and move to next cell
                                lawnmower_search_index += 1
                                next_cell = lawnmower_search[lawnmower_search_index]
                        
                        #Update the L2's position
                        grid[L2_coords[0]][L2_coords[1]][5][2] = None #clear the previous L2 position
                        L2_coords = next_cell
                        grid[L2_coords[0]][L2_coords[1]][5][2] = 2 #set the new L2 position
                        
                        #Increase the index
                        lawnmower_search_index += 1
                        
                        #Increase cells traveled
                        '''
                        L2_cells_travelled += 1
                        if current_num_survivors == 1:
                            L2_cells_travelled_for_last_survivor += 1
                        
                        #For average calculations
                        L2_cells_travelled_to_next_survivor += 1
                        print("L2 cells travelled: " + str(L2_cells_travelled_to_next_survivor))
                        '''
                        
                        #After reaching the unvisted cell go to the next one
                        if next_cell in unvisited_cells:
                            unvisited_cells.remove(next_cell)
                            lawnmower_search = dijkstra(L2_coords, None, grid, 5, unvisited_cells)
                            lawnmower_search_index = 0
        
        ###Rescuing the survivor###
        #Checks to see if any survivors have been found by L1s or the current search type is omnicient
        if len(survivors_found_locations) != 0 or search_type == 1: #if was previously: elif not searching
            if multiple_L1s_input > 1: #code for when there are multiple L1s
                for L1_id in range(multiple_L1s_input):
                    print("It is L1 " + str(L1_id) + "'s turn:") #shows which L1 has its turn currently
                    
                    #Prints for basic trackers
                    print("Survivors: " + str(current_num_survivors))
                    print("Guiding: " + str(num_guiding_survivors))
                    print("L1 coords:", L1_coords[L1_id][0])
                    print("Exit:", Exit)
                    print("Next L1 Cell before update: " + str(next_cell))
                    print("Going to target survivor:", going_to_target[L1_id])
                    
                    #Prints to show what the variables are for each if and elif statements and if they are working
                    print("For the resetter if, does (" + str(L1_coords[L1_id][0]) + " == " + str(Exit) + " and " + str(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0]) + " == 'S') or (not " + str(going_to_target[L1_id]) + " and " + str(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0]) + " != 'S') or (", L1_movement_type[L1_id], "== 1 and", num_guiding_survivors[L1_id], "== 0)?")
                    #print("For the going to survivor whilst guiding elif, is " + str(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1]) + " True and " + str(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0]) + " == 'S' and ((" + str(L1_coords[L1_id][0]) + " != " + str(L2_survivor) + " and " + str(search_type) + " != 1) or (" + str(L1_coords[L1_id][0]) + " != " + str(assignments[L1_id]) + " and " + str(search_type) + " == 1)) and " + str(going_to_target[L1_id]) + "?")
                    #print("For the return to exit elif, is " + str(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1]) + " True and " + str(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0]) + " == 'S'")
                    if to_closest_survivor_path[L1_id] != None:
                        print("For the regular movement to the survivor elif, is " + str(to_closest_survivor_path[L1_id]) + " True and " + str(to_survivor_path_index[L1_id]) + " < " + str(len(to_closest_survivor_path[L1_id])))
                    else:
                        print("The to_closest_survivor_path[L1_id] variable equals None.")
                    
                    #print("L1 coords: " + str(L1_coords))
                    #print("L1 coords: " + str(L1_coords[L1_id]))
                    #print("L1 coords: " + str(L1_coords[L1_id][0]))
                    #print("L1 coords: " + str(L1_coords[L1_id][0][0]))
                    #print("L1 coords: " + str(L1_coords[L1_id][0][1]))
                    #print("Grid: " + str(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1]))
                    #print("Grid len: " + str(len(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1])))
                    #print("Grid: " + str(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0]))
                    #print("Exit: " + str(Exit))
                    #print("Exit[0]: " + str(Exit[0]))
                    #print("Exit[1]: " + str(Exit[1]))
                    #print("to_closest_survivor_path: " + str(to_closest_survivor_path))
                    #print("to_closest_survivor_path[L1_id]: " + str(to_closest_survivor_path[L1_id]))
                    #print("len(to_closest_survivor_path[L1_id]): " + str(len(to_closest_survivor_path[L1_id])))
                    #print("to_survivor_path_index: " + str(to_survivor_path_index))
                    print("assignments:", assignments)
                    #print("grid[assignments[L1_id][0]][assignments[L1_id][1]][5][0]:", grid[assignments[L1_id][0]][assignments[L1_id][1]][5][0])
                    
                    ###Resets the cycle of ifs###
                    #resetter if
                    #Sets it back to searching, reseting variables, and doing stuff for the end screen
                    #If the current L1 coords = the exit coords and the L1 also has a survivor then execute the resetter if and is not going to target survivor
                    #Resetter if also executes its code if the L1 isn't going to target and it doesn't have a survivor as this should not be happening
                    #Resetter if also executes when an L1 is attempting to go to the exit whilst guiding no survivors
                    #Resetter if also executes when an L1 is at the end of its path, isn't guiding any survivors, and isn't at the exit
                    if (L1_coords[L1_id][0] == Exit and grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0] == "S" and not going_to_target[L1_id]) or (not going_to_target[L1_id] and grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0] != "S") or (L1_movement_type[L1_id] == 1 and num_guiding_survivors[L1_id] == 0):# or (L1_coords[L1_id][0] != Exit and num_guiding_survivors[L1_id] == 0 and to_survivor_path_index[L1_id] == len(to_closest_survivor_path[L1_id])):# or (assignments[L1_id] != None and grid[assignments[L1_id][0]][assignments[L1_id][1]][5][0] != "S" and L1_coords[L1_id][0] == assignments[L1_id]):
                        print("L1", L1_id, "Reset occured")
                        
                        ''' To do with old stats so no longer needed
                        #If search type is 1 then put the finding stats as N/A
                        if search_type == 1:
                            cells_2_find_first_survivor = "N/A"
                            cells_2_find_last_survivor = "N/A"
                            cells_average_2_find_survivor = "N/A"
                            cells_2_find_all_survivors = "N/A"
                        
                        #L1 cells travelled assigning to cell 2 save
                        print("Cells travelled to save: " + str(L1_cells_travelled))
                        print("Cells travelled to save last: " + str(L1_cells_travelled_for_last_survivor))
                        if current_num_survivors == num_survivors_input:
                            cells_2_save_first_survivor = L1_cells_travelled
                        if current_num_survivors == 1:
                            cells_2_save_last_survivor = L1_cells_travelled_for_last_survivor
                            cells_2_save_all_survivors = L1_cells_travelled
                        #L1 time travelled assigning to time 2 save
                        if current_num_survivors == num_survivors_input:
                            time_2_save_first_survivor = L1_time_travelled
                        if current_num_survivors == 1:
                            time_2_save_last_survivor = L1_time_travelled_for_last_survivor
                            time_2_save_all_survivors = L1_time_travelled
                        
                        #For average calculations
                        L1_current_survivor -= 1
                        cells_2_save_survivors.append(L1_cells_travelled_to_next_survivor)
                        L1_cells_travelled_to_next_survivor = 0
                        time_2_save_survivors.append(L1_time_travelled_to_next_survivor)
                        L1_time_travelled_to_next_survivor = 0
                        '''
                        
                        #Back to searching
                        if search_type != 1:
                            print("L2_id:", L2_id)
                            searching[L2_id] = True
                        #Resets to going back to target survivor
                        going_to_target[L1_id] = True
                        
                        #Reset the current L1 back to regular movement
                        L1_movement_type[L1_id] = 2
                        
                        #Reset indexes
                        to_survivor_path_index[L1_id] = 0
                        to_exit_path_index[L1_id] = 0
                        to_survivor_with_a_survivor_path_index[L1_id] = 0
                        
                        #Remove the suvivor as they have been saved
                        if L1_coords[L1_id][0] == Exit and grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0] == "S":
                            grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0] = None
                            current_num_survivors -= num_guiding_survivors[L1_id]
                            print("Reset L1 " + str(L1_id) + " guiding amount to 0")
                            num_guiding_survivors[L1_id] = 0
                        
                        #Remove the first survivor in the found survivor locations list
                        if search_type != 1:
                            survivors_found_locations.pop(0)
                        
                        #Find the new closest survivor to L1
                        #A list of all the available survivors
                        #available_survivors = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE) if grid[x][y][5][0] == "S"]
                        #assignments = [] #an empty list for storing assigned survivor locations with the L1 asigned to it
                        #switch = None #to make sure that available survivors and assignments are only used when needed
                        if search_type == 1: #This should only happen when it is the first search type.
                            for x in range(GRID_SIZE):
                                for y in range(GRID_SIZE):
                                    #Check if there is a survivor and that it is an available one and makes sur the the current L1 isnt occupied else where
                                    if grid[x][y][5][0] == "S" and (x, y) in available_survivors:
                                        distance = math.sqrt((x - L1_coords[L1_id][0][0])**2 + (y - L1_coords[L1_id][0][1])**2)  #euclidean distance
                                        if distance < closest_distance:
                                            closest_survivor = (x, y)
                                            closest_distance = distance
                                            switch = True #enabling available_survivors and assignments to be used
                            if switch:
                                closest_distance = float('inf')
                                available_survivors.remove(closest_survivor)
                                assignments[L1_id] = closest_survivor #replace the previous value of the assignments for that particular L1 with the new survivor it is assigned to.
                                switch = False
                            #Dijkstra from L1 to new closest survivor replaces old path
                            to_closest_survivor_path[L1_id] = dijkstra(L1_coords[L1_id][0], assignments[L1_id], grid, 1, None)
                            #print(to_closest_survivor_path)
                        else: #this is to reset the L1's path when the reset occurs
                            print("Path for L1", L1_id, "is back to None")
                            to_closest_survivor_path[L1_id] = None #this makes sure that the L1 doesn't retake the path it just did
                        
                        #Go to end screen
                        if current_num_survivors == 0: #when there is no more survivors
                            simulation = False #end sim
                            end_screen = True #start end screen
                            
                            #Averages calculations
                            ''' old
                            if not search_type == 1:
                                print("L2 distances to make average: " + str(cells_2_find_survivors))
                                cells_average_2_find_survivor = sum(cells_2_find_survivors) / len(cells_2_find_survivors)
                            print("L1 distances to make average: " + str(cells_2_save_survivors))
                            cells_average_2_save_survivor = sum(cells_2_save_survivors) / len(cells_2_save_survivors)
                            print("L1 time to make average: " + str(time_2_save_survivors))
                            time_average_2_save_survivor = sum(time_2_save_survivors) / len(time_2_save_survivors)
                            '''
                            
                            #Stats
                            print("Time to find and save all survivors:", time_2_find_and_save_all_survivors)
                            all_times_2_find_and_save_all_survivors.append(time_2_find_and_save_all_survivors)
                            time_2_find_and_save_all_survivors_temp = time_2_find_and_save_all_survivors
                            print("Sum of all times:", sum(all_times_2_find_and_save_all_survivors))
                            print("Len of all times:", len(all_times_2_find_and_save_all_survivors))
                            time_2_find_and_save_all_survivors_average = sum(all_times_2_find_and_save_all_survivors) / len(all_times_2_find_and_save_all_survivors)
                            
                            #Grid size with same width and height (amount of cells)
                            GRID_SIZE = 15
                            
                            font = pygame.font.Font(None, 36) #setting up the font size
                            
                            screen.fill((WHITE))  #Filling the screen white
                    
                    ###Going to the survivor whilst guiding###
                    #!All the movement elifs need to change to compensate for multiple L1s!#
                    #If the L1 is at a survivor but not the one adjacent to the L2, find the shortest path to the survivor adjacent to the L2
                    #grid [L1_coords[L1_id][0][0]] [L1_coords[L1_id][0][1]][5][1] is the value of how many and which L1s are in those coordinates (spaces put in to distinguish the parts)
                    elif grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1] and (grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0] == "S" and num_guiding_survivors[L1_id] != 0) and (((L1_coords[L1_id][0] != assignments[L1_id]) and search_type != 1) or (L1_coords[L1_id][0] != assignments[L1_id] and search_type == 1)) and going_to_target[L1_id]:
                        print("L1", L1_id, "Moving to survivor with a survivor")
                        print("L1 coords: " + str(L1_coords[L1_id]))
                        print("L2 survivor coords: " + str(L2_survivor))
                        print("Assigned survivor coords: " + str(assignments[L1_id]))
                        
                        ##Set this L1's movement type##
                        L1_movement_type[L1_id] = 0
                        
                        ##New dijkstras depending on the search type##
                        #Checks to see if the search type is set for closest survivor search
                        if search_type == 1:
                            to_closest_survivor_path[L1_id] = dijkstra(L1_coords[L1_id][0], assignments[L1_id], grid, 2, None)
                        #Checks to see if the search type is set for random search
                        elif search_type == 2:
                            to_closest_survivor_path[L1_id] = dijkstra(L1_coords[L1_id][0], assignments[L1_id], grid, 2, None)
                        #Checks to see if the search type is set for dijkstra search
                        elif search_type == 3:
                            to_closest_survivor_path[L1_id] = dijkstra(L1_coords[L1_id][0], assignments[L1_id], grid, 2, None)
                        
                        print("The next cell value before its updated: " + str(next_cell))
                        #print("The current index: " + str(to_survivor_with_a_survivor_path_index))
                        to_survivor_with_a_survivor_path_index[L1_id] = 1
                        
                        ##Move the L1 to the survivor##
                        if to_closest_survivor_path[L1_id] and to_survivor_with_a_survivor_path_index[L1_id] < len(to_closest_survivor_path[L1_id]):
                            next_cell = to_closest_survivor_path[L1_id][to_survivor_with_a_survivor_path_index[L1_id]]
                            print("The next cell: " + str(next_cell))
                            
                            '''
                            #For average calculations
                            L1_time_travelled_to_next_survivor += 1
                            
                            #Time travelled increases
                            L1_time_travelled += 1
                            if current_num_survivors == 1:
                                L1_time_travelled_for_last_survivor += 1
                            '''
                            
                            if grid[next_cell[0]][next_cell[1]][2] and not grid[next_cell[0]][next_cell[1]][3]:  #check if navigable to the survivor
                                #For average calculations
                                #L1_cells_travelled_to_next_survivor += 1
                                
                                #Checks to see if the next cell has a survivor and doesn't have a survivor
                                if grid[next_cell[0]][next_cell[1]][5][0] == "S" and not grid[next_cell[0]][next_cell[1]][5][1]:
                                    print("Plus 1 survivor guiding by L1", L1_id, "when going to survivor whilst guiding")
                                    num_guiding_survivors[L1_id] += 1 #adds to the num of survivors being guided
                                
                                #Update the L1's and the survivor's position
                                grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1].remove(L1_id) #clear the previous positions
                                #if num_guiding_survivors[L1_id] != 0: #need so that there isn't phantom survivors
                                grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0] = None
                                L1_coords[L1_id][0] = next_cell
                                grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1].append(L1_id) #set the new positions
                                #if num_guiding_survivors[L1_id] != 0: #need so that there isn't phantom survivors
                                grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0] = "S"
                                
                                '''
                                #Cells travelled increases
                                L1_cells_travelled += 1
                                print("Cells travellled to survivor " + str(L1_cells_travelled))
                                if current_num_survivors == 1:
                                    L1_cells_travelled_for_last_survivor += 1
                                    print("Cells travellled to last survivor " + str(L1_cells_travelled_for_last_survivor))
                                '''
                    
                    ###Return to exit###
                    #If the L1 reaches the survivor, find the shortest path to the exit
                    elif grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1] and (grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0] == "S" and num_guiding_survivors[L1_id] != 0):
                        print("L1", L1_id, "Moving to exit")
                        
                        ##Set this L1's movement type##
                        L1_movement_type[L1_id] = 1
                        
                        ##Is now going to exit##
                        going_to_target[L1_id] = False
                        
                        ##New dijkstras depending on the search type##
                        #Checks to see if the search type is set for closest survivor search
                        if search_type == 1:
                            #print(shortest_path_to_exit)
                            #print(L1_id)
                            #print(assignments[L1_id])
                            #print(Exit)
                            shortest_path_to_exit[L1_id] = dijkstra(assignments[L1_id], Exit, grid, 2, None) #new dijkstra algorithm
                        #Checks to see if the search type is set for random search
                        elif search_type == 2:
                            shortest_path_to_exit[L1_id] = dijkstra(assignments[L1_id], Exit, grid, 2, None) #new dijkstra algorithm
                        #Checks to see if the search type is set for dijkstra search
                        elif search_type == 3:
                            shortest_path_to_exit[L1_id] = dijkstra(assignments[L1_id], Exit, grid, 2, None) #new dijkstra algorithm
                        
                        ##Move towards exit whilst guiding##
                        #Move the L1 to the exit from the survivor
                        if shortest_path_to_exit[L1_id] and to_exit_path_index[L1_id] < len(shortest_path_to_exit[L1_id]):
                            print("L1 cell: " + str(L1_coords[L1_id][0]))
                            next_cell = shortest_path_to_exit[L1_id][to_exit_path_index[L1_id]]
                            print("Next_cell: " + str(next_cell))
                            
                            '''
                            #For average calculations
                            L1_time_travelled_to_next_survivor += 1
                            
                            #Time travelled increases
                            L1_time_travelled += 1
                            if current_num_survivors == 1:
                                L1_time_travelled_for_last_survivor += 1
                            '''
                            
                            if grid[next_cell[0]][next_cell[1]][2] and not grid[next_cell[0]][next_cell[1]][3]:  #check if navigable to the survivor
                                #Checks to see if the next cell has a survivor
                                #print("Checking to see if the final bit is functioning: (not " + str(L1_coords[L1_id][0]) + " == " + str(assignments[L1_id]) + " and " + str(search_type) + " == 1)")
                                if grid[next_cell[0]][next_cell[1]][5][0] == "S" and ((L1_coords[L1_id][0] != assignments[L1_id] and search_type != 1) or (L1_coords[L1_id][0] != assignments[L1_id] and search_type == 1)):
                                    if grid[next_cell[0]][next_cell[1]][5][1]: #if there is L1(s) in the next cell
                                        print("grid[next_cell[0]][next_cell[1]][5][1]:", grid[next_cell[0]][next_cell[1]][5][1])
                                        print("len(grid[next_cell[0]][next_cell[1]][5][1]):)", len(grid[next_cell[0]][next_cell[1]][5][1]))
                                        if len(grid[next_cell[0]][next_cell[1]][5][1]) > 1: #when there are multiple L1s in the next cell
                                            for other_L1s in range(len(grid[next_cell[0]][next_cell[1]][5][1])):
                                                print("Added", num_guiding_survivors[grid[next_cell[0]][next_cell[1]][5][1][other_L1s]], "from L1", grid[next_cell[0]][next_cell[1]][5][1][other_L1s], "to the current L1", L1_id, "survivors guiding amount")
                                                num_guiding_survivors[L1_id] += num_guiding_survivors[grid[next_cell[0]][next_cell[1]][5][1][other_L1s]]
                                                print("L1", grid[next_cell[0]][next_cell[1]][5][1][other_L1s], "is no longer guiding anthing")
                                                num_guiding_survivors[grid[next_cell[0]][next_cell[1]][5][1][other_L1s]] = 0
                                                
                                        else: #when there is only one L1 in the next cell
                                            print("Added", num_guiding_survivors[grid[next_cell[0]][next_cell[1]][5][1][0]], "from L1", grid[next_cell[0]][next_cell[1]][5][1][0], "to the current L1", L1_id, "survivors guiding amount")
                                            num_guiding_survivors[L1_id] += num_guiding_survivors[grid[next_cell[0]][next_cell[1]][5][1][0]]
                                            print("L1", grid[next_cell[0]][next_cell[1]][5][1][0], "is no longer guiding anthing")
                                            num_guiding_survivors[grid[next_cell[0]][next_cell[1]][5][1][0]] = 0
                                            print("The guiding survivors amounts are now", num_guiding_survivors)
                                            
                                    else: #when there isn't a L1 in the next cell
                                        print("Plus 1 survivor guiding by L1", L1_id, "when returning to exit")
                                        num_guiding_survivors[L1_id] += 1 #adds to the num of survivors being guided
                                
                                #For average calculations
                                #L1_cells_travelled_to_next_survivor += 1
                                
                                #Update the L1's and the survivor's position
                                grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1].remove(L1_id) #clear the previous positions
                                grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0] = None
                                L1_coords[L1_id][0] = next_cell
                                grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1].append(L1_id) #set the new positions
                                grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][0] = "S"
                                
                                #Increase the index
                                to_exit_path_index[L1_id] += 1
                                
                                '''
                                #Cells travelled increases
                                L1_cells_travelled += 1
                                print("Cells travellled from survivor " + str(L1_cells_travelled))
                                if current_num_survivors == 1:
                                    L1_cells_travelled_for_last_survivor += 1
                                    print("Cells travellled from last survivor " + str(L1_cells_travelled_for_last_survivor))
                                '''
                    
                    ###Move the L1 to the survivor###
                    elif to_closest_survivor_path[L1_id] and to_survivor_path_index[L1_id] < len(to_closest_survivor_path[L1_id]):
                        print("L1", L1_id, "Moving to survivor")
                        print("The next cell will equal " + str(to_closest_survivor_path[L1_id][to_survivor_path_index[L1_id]]) + " which is the " + str(to_survivor_path_index) + " index in the path of " + str(to_closest_survivor_path))
                        next_cell = to_closest_survivor_path[L1_id][to_survivor_path_index[L1_id]]
                        
                        ##Set this L1's movement type##
                        L1_movement_type[L1_id] = 2
                        
                        #For average calculations
                        #L1_time_travelled_to_next_survivor += 1
                        
                        '''
                        #Time travelled increases
                        L1_time_travelled += 1
                        if current_num_survivors == 1:
                            L1_time_travelled_for_last_survivor += 1
                        '''
                        
                        if grid[next_cell[0]][next_cell[1]][4]: #checks if navigable to the L1
                            #For average calculations
                            #L1_cells_travelled_to_next_survivor += 1
                            
                            #Checks to see if the next cell has a survivor and doesn't have an L1
                            if grid[next_cell[0]][next_cell[1]][5][0] == "S" and not grid[next_cell[0]][next_cell[1]][5][1]:
                                print("Plus 1 survivor guiding by L1", L1_id, "when moving to a survivor with no L1")
                                num_guiding_survivors[L1_id] += 1 #adds to the num of survivors being guided
                            
                            #Update the L1's position
                            #print("L1 IDs in current cell before remove: " + str(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1]))
                            #if len(grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1]) != 0:
                            grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1].remove(L1_id) #clear the previous L1 position
                            #else:
                                #print("ERROR: Removal of an L1 from a cell didn't work!")
                            L1_coords[L1_id][0] = next_cell
                            grid[L1_coords[L1_id][0][0]][L1_coords[L1_id][0][1]][5][1].append(L1_id) #set the new L1 position
                            
                            #Increase the index
                            to_survivor_path_index[L1_id] += 1
                            
                            '''
                            #Cells travelled increases
                            L1_cells_travelled += 1
                            print("Cells travellled to survivor " + str(L1_cells_travelled))
                            if current_num_survivors == 1:
                                L1_cells_travelled_for_last_survivor += 1
                                print("Cells travellled to last survivor " + str(L1_cells_travelled_for_last_survivor))
                            '''
            
            else: #code for when ther is only 1 L1
                ###Resets the cycle of ifs###
                #resetter if
                #Sets it back to searching, reseting variables, and doing stuff for the end screen
                #if the L1 coords = the exit coords and the L1 also has a survivor then execute the resetter if
                if L1_coords == Exit and grid[L1_coords[0]][L1_coords[1]][5][0] == "S":
                    print("Reset occured")
                    
                    ''' old stats
                    #If search type is 1 then put the finding stats as N/A
                    if search_type == 1:
                        cells_2_find_first_survivor = "N/A"
                        cells_2_find_last_survivor = "N/A"
                        cells_average_2_find_survivor = "N/A"
                        cells_2_find_all_survivors = "N/A"
                    
                    #L1 cells travelled assigning to cell 2 save
                    print("Cells travelled to save: " + str(L1_cells_travelled))
                    print("Cells travelled to save last: " + str(L1_cells_travelled_for_last_survivor))
                    if current_num_survivors == num_survivors_input:
                        cells_2_save_first_survivor = L1_cells_travelled
                    if current_num_survivors == 1:
                        cells_2_save_last_survivor = L1_cells_travelled_for_last_survivor
                        cells_2_save_all_survivors = L1_cells_travelled
                    #L1 time travelled assigning to time 2 save
                    if current_num_survivors == num_survivors_input:
                        time_2_save_first_survivor = L1_time_travelled
                    if current_num_survivors == 1:
                        time_2_save_last_survivor = L1_time_travelled_for_last_survivor
                        time_2_save_all_survivors = L1_time_travelled
                    
                    #For average calculations
                    L1_current_survivor -= 1
                    cells_2_save_survivors.append(L1_cells_travelled_to_next_survivor)
                    L1_cells_travelled_to_next_survivor = 0
                    time_2_save_survivors.append(L1_time_travelled_to_next_survivor)
                    L1_time_travelled_to_next_survivor = 0
                    '''
                    
                    #Back to searching
                    if not search_type == 1:
                        searching = True
                    #Resets to going back to target survivor
                    going_to_target = True
                    
                    #Reset indexes
                    to_survivor_path_index = 0
                    to_exit_path_index = 0
                    to_survivor_with_a_survivor_path_index = 0
                    
                    #Remove the suvivor as they have been saved
                    grid[L1_coords[0]][L1_coords[1]][5][0] = None
                    current_num_survivors -= num_guiding_survivors
                    num_guiding_survivors = 0
                    
                    #Remove the first survivor in the found survivor locations list
                    if search_type != 1:
                        survivors_found_locations.pop(0)
                    
                    #Find the new closest survivor to L1
                    closest_survivor = None
                    closest_distance = float('inf')
                    for x in range(GRID_SIZE):
                        for y in range(GRID_SIZE):
                            if grid[x][y][5][0] == "S":  #check if there is a survivor
                                distance = math.sqrt((x - L1_coords[0])**2 + (y - L1_coords[1])**2)  #euclidean distance
                                if distance < closest_distance:
                                    closest_survivor = (x, y)
                                    closest_distance = distance
                    #New dijkstra algorithm needed for new closest survivor
                    to_closest_survivor_path = dijkstra(L1_coords, closest_survivor, grid, 1, None)
                    
                    #Go to end screen
                    if current_num_survivors == 0: #when there is no more survivors
                        simulation = False #end sim
                        end_screen = True #start end screen
                        
                        ''' old stats
                        #Averages calculations
                        if not search_type == 1:
                            print("L2 distances to make average: " + str(cells_2_find_survivors))
                            cells_average_2_find_survivor = sum(cells_2_find_survivors) / len(cells_2_find_survivors)
                        print("L1 distances to make average: " + str(cells_2_save_survivors))
                        cells_average_2_save_survivor = sum(cells_2_save_survivors) / len(cells_2_save_survivors)
                        print("L1 time to make average: " + str(time_2_save_survivors))
                        time_average_2_save_survivor = sum(time_2_save_survivors) / len(time_2_save_survivors)
                        '''
                        
                        #Stats
                        print("Time to find and save all survivors:", time_2_find_and_save_all_survivors)
                        all_times_2_find_and_save_all_survivors.append(time_2_find_and_save_all_survivors)
                        time_2_find_and_save_all_survivors_temp = time_2_find_and_save_all_survivors
                        print("Sum of all times:", sum(all_times_2_find_and_save_all_survivors))
                        print("Len of all times:", len(all_times_2_find_and_save_all_survivors))
                        time_2_find_and_save_all_survivors_average = sum(all_times_2_find_and_save_all_survivors) / len(all_times_2_find_and_save_all_survivors)
                        
                        #Grid size with same width and height (amount of cells)
                        GRID_SIZE = 15
                        
                        font = pygame.font.Font(None, 36) #setting up the font size
                        
                        screen.fill((WHITE))  #Filling the screen white
                
                ###Going to the survivor whilst guiding###
                #If the L1 is at a survivor but not the one adjacent to the L2, find the shortest path to the survivor adjacent to the L2
                elif grid[L1_coords[0]][L1_coords[1]][5][1] == 1 and grid[L1_coords[0]][L1_coords[1]][5][0] == "S" and ((not L1_coords == L2_survivor and not search_type == 1) or (not L1_coords == closest_survivor and search_type == 1)) and going_to_target:
                    print("Moving to survivor with a survivor")
                    print("L1 coords: " + str(L1_coords))
                    print("L2 survivor coords: " + str(L2_survivor))
                    print("Closest survivor coords: " + str(closest_survivor))
                    
                    ##New dijkstras depending on the search type##
                    #Checks to see if the search type is set for closest survivor search
                    if search_type == 1:
                        to_closest_survivor_path = dijkstra(L1_coords, closest_survivor, grid, 2, None)
                    #Checks to see if the search type is set for random search
                    elif search_type == 2:
                        to_closest_survivor_path = dijkstra(L1_coords, L2_survivor, grid, 2, None)
                    #Checks to see if the search type is set for dijkstra search
                    elif search_type == 3:
                        to_closest_survivor_path = dijkstra(L1_coords, L2_survivor, grid, 2, None)
                    
                    print("The next cell value before its updated: " + str(next_cell))
                    print("The current index: " + str(to_survivor_with_a_survivor_path_index))
                    to_survivor_with_a_survivor_path_index = 1
                    
                    ##Move the L1 to the survivor##
                    if to_closest_survivor_path and to_survivor_with_a_survivor_path_index < len(to_closest_survivor_path):
                        next_cell = to_closest_survivor_path[to_survivor_with_a_survivor_path_index]
                        print("The next cell: " + str(next_cell))
                        
                        '''
                        #For average calculations
                        L1_time_travelled_to_next_survivor += 1
                        
                        #Time travelled increases
                        L1_time_travelled += 1
                        if current_num_survivors == 1:
                            L1_time_travelled_for_last_survivor += 1
                        '''
                        
                        if grid[next_cell[0]][next_cell[1]][2] and not grid[next_cell[0]][next_cell[1]][3]:  #check if navigable to the survivor
                            #For average calculations
                            #L1_cells_travelled_to_next_survivor += 1
                            
                            #Checks to see if the next cell has a survivor
                            if grid[next_cell[0]][next_cell[1]][5][0] == "S":
                                print("Guiding increase at M2SWS")
                                num_guiding_survivors += 1 #adds to the num of survivors being guided
                            
                            #Update the L1's and the survivor's position
                            grid[L1_coords[0]][L1_coords[1]][5][1] = None #clear the previous positions
                            grid[L1_coords[0]][L1_coords[1]][5][0] = None
                            L1_coords = next_cell
                            grid[L1_coords[0]][L1_coords[1]][5][1] = 1 #set the new positions
                            grid[L1_coords[0]][L1_coords[1]][5][0] = "S"
                            
                            '''
                            #Cells travelled increases
                            L1_cells_travelled += 1
                            print("Cells travellled to survivor " + str(L1_cells_travelled))
                            if current_num_survivors == 1:
                                L1_cells_travelled_for_last_survivor += 1
                                print("Cells travellled to last survivor " + str(L1_cells_travelled_for_last_survivor))
                            '''
                
                ###Return to exit###
                #If the L1 reaches the survivor, find the shortest path to the exit
                elif grid[L1_coords[0]][L1_coords[1]][5][1] == 1 and grid[L1_coords[0]][L1_coords[1]][5][0] == "S":
                    print("Moving to exit")
                    #Is now going to exit
                    going_to_target = False
                    
                    ##New dijkstras depending on the search type##
                    #Checks to see if the search type is set for closest survivor search
                    if search_type == 1:
                        shortest_path_to_exit = dijkstra(closest_survivor, Exit, grid, 2, None) #new dijkstra algorithm
                    #Checks to see if the search type is set for random search
                    elif search_type == 2:
                        shortest_path_to_exit = dijkstra(L2_survivor, Exit, grid, 2, None) #new dijkstra algorithm
                    #Checks to see if the search type is set for dijkstra search
                    elif search_type == 3:
                        shortest_path_to_exit = dijkstra(L2_survivor, Exit, grid, 2, None) #new dijkstra algorithm
                    
                    ##Move towards exit whilst guiding##
                    #Move the L1 to the exit from the survivor
                    if shortest_path_to_exit and to_exit_path_index < len(shortest_path_to_exit):
                        next_cell = shortest_path_to_exit[to_exit_path_index]
                        
                        '''
                        #For average calculations
                        L1_time_travelled_to_next_survivor += 1
                        
                        #Time travelled increases
                        L1_time_travelled += 1
                        if current_num_survivors == 1:
                            L1_time_travelled_for_last_survivor += 1
                        '''
                        
                        if grid[next_cell[0]][next_cell[1]][2] and not grid[next_cell[0]][next_cell[1]][3]:  #check if navigable to the survivor
                            #Checks to see if the next cell has a survivor
                            if grid[next_cell[0]][next_cell[1]][5][0] == "S" and ((not L1_coords == L2_survivor and not search_type == 1) or (not L1_coords == closest_survivor and search_type == 1)):
                                print("Guiding increase at M2E")
                                num_guiding_survivors += 1 #adds to the num of survivors being guided
                            
                            #For average calculations
                            #L1_cells_travelled_to_next_survivor += 1
                            
                            #Update the L1's and the survivor's position
                            grid[L1_coords[0]][L1_coords[1]][5][1] = None #clear the previous positions
                            grid[L1_coords[0]][L1_coords[1]][5][0] = None
                            L1_coords = next_cell
                            grid[L1_coords[0]][L1_coords[1]][5][1] = 1 #set the new positions
                            grid[L1_coords[0]][L1_coords[1]][5][0] = "S"
                            
                            #Increase the index
                            to_exit_path_index += 1
                            
                            '''
                            #Cells travelled increases
                            L1_cells_travelled += 1
                            print("Cells travellled from survivor " + str(L1_cells_travelled))
                            if current_num_survivors == 1:
                                L1_cells_travelled_for_last_survivor += 1
                                print("Cells travellled from last survivor " + str(L1_cells_travelled_for_last_survivor))
                            '''
                
                ###Move the L1 to the survivor###
                elif to_closest_survivor_path and to_survivor_path_index < len(to_closest_survivor_path):
                    print("Moving to survivor")
                    print("The next cell will equal " + str(to_closest_survivor_path[to_survivor_path_index]) + " which is the " + str(to_survivor_path_index) + " index in the path of " + str(to_closest_survivor_path))
                    next_cell = to_closest_survivor_path[to_survivor_path_index]

                    '''
                    #For average calculations
                    L1_time_travelled_to_next_survivor += 1
                    
                    #Time travelled increases
                    L1_time_travelled += 1
                    if current_num_survivors == 1:
                        L1_time_travelled_for_last_survivor += 1
                    '''
                    
                    if grid[next_cell[0]][next_cell[1]][4]: #checks if navigable to the L1
                        #For average calculations
                        #L1_cells_travelled_to_next_survivor += 1
                        
                        #Checks to see if the next cell has a survivor
                        if grid[next_cell[0]][next_cell[1]][5][0] == "S":
                            print("Guiding increase at M2S")
                            num_guiding_survivors += 1 #adds to the num of survivors being guided
                        
                        #Update the L1's position
                        grid[L1_coords[0]][L1_coords[1]][5][1] = None #clear the previous L1 position
                        L1_coords = next_cell
                        grid[L1_coords[0]][L1_coords[1]][5][1] = 1 #set the new L1 position
                        
                        #Increase the index
                        to_survivor_path_index += 1
                        
                        '''
                        #Cells travelled increases
                        L1_cells_travelled += 1
                        print("Cells travellled to survivor " + str(L1_cells_travelled))
                        if current_num_survivors == 1:
                            L1_cells_travelled_for_last_survivor += 1
                            print("Cells travellled to last survivor " + str(L1_cells_travelled_for_last_survivor))
                        '''

        ###Stats###
        time_2_find_and_save_all_survivors += 1
        
        #!Cycle of the sim finishes!#
        
    #Flip is what actually displays everything
    pygame.display.flip()
    #Delay is here to make sure that everything doesn't happen instantly
    pygame.time.delay(10) #Should be at 500 normally
    clock.tick(60) #limited to running at 60 fps

pygame.quit()