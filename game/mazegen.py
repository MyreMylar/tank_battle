import random
import pygame


colours = []
for i in range(0, 500):
    result = i % 6
    if result == 1:
        colours.append(pygame.Color("#FF0000"))
    elif result == 2:
        colours.append(pygame.Color("#00FF00"))
    elif result == 3:
        colours.append(pygame.Color("#0000FF"))
    elif result == 4:
        colours.append(pygame.Color("#FFFF00"))
    elif result == 5:
        colours.append(pygame.Color("#00FFFF"))


class WalkableZone:
    def __init__(self, x_pos, y_pos):
        self.grid_x_pos = x_pos
        self.grid_y_pos = y_pos

        self.screen_x_pos = 125 + (self.grid_x_pos * 25)
        self.screen_y_pos = 50 + (self.grid_y_pos * 25)


class JunctionPoint:
    def __init__(self, x_pos, y_pos):
        self.grid_x_pos = x_pos
        self.grid_y_pos = y_pos

        self.screen_x_pos = 125 + (self.grid_x_pos * 25)
        self.screen_y_pos = 50 + (self.grid_y_pos * 25)
        self.neighbours = []


class MazeWall:
    def __init__(self, start_index, end_index):
        self.is_vertical_wall = False
        self.is_horizontal_wall = False

        if start_index[0] < end_index[0]:
            first_id = start_index[0]
            second_id = end_index[0]
            self.is_vertical_wall = True
        else:
            first_id = end_index[0]
            second_id = start_index[0]

        if start_index[1] < end_index[1]:
            third_id = start_index[1]
            fourth_id = end_index[1]
            self.is_horizontal_wall = True
        else:
            third_id = end_index[1]
            fourth_id = start_index[1]
        
        self.id = str(first_id) + str(second_id) + str(third_id) + str(fourth_id)
        self.start_index = start_index
        self.end_index = end_index

        self.start_pos = [125 + (start_index[1] * 25), 50 + (start_index[0] * 25)]
        self.end_pos = [125 + (end_index[1] * 25), 50 + (end_index[0] * 25)]
            
        self.right_neighbour = False
        self.left_neighbour = False
        self.top_neighbour = False
        self.bottom_neighbour = False
        
        self.is_top_corner = False
        self.is_bottom_corner = False
        self.is_left_corner = False
        self.is_right_corner = False
        self.collided = False

        self.edges = []
        self.colour = pygame.Color("#000000")

        self.rect = None
        self.surface = None

    def generate_edges(self):

        if self.start_pos[0] < self.end_pos[0]:
            left = self.start_pos[0]
            width = self.end_pos[0] - self.start_pos[0]
        else:
            left = self.end_pos[0]
            width = self.start_pos[0] - self.end_pos[0]
            if width == 0:
                width = 4

        if self.start_pos[1] < self.end_pos[1]:
            top = self.start_pos[1]
            height = self.end_pos[1] - self.start_pos[1]
        else:
            top = self.start_pos[1]
            height = self.start_pos[1] - self.end_pos[1]
            if height == 0:
                height = 4

        if self.is_vertical_wall:
            top += 4

        if self.is_vertical_wall and self.is_bottom_corner:
            height -= 4

        if self.is_horizontal_wall and self.is_right_corner:
            width += 4

        self.rect = pygame.Rect((left, top), (width, height))
        self.surface = pygame.Surface((width, height))
        self.surface.fill(self.colour)
        
        if not self.top_neighbour:
            self.edges.append([[self.rect.left, self.rect.top], [self.rect.right, self.rect.top], [0.0, -1.0]])
        if not self.left_neighbour:
            self.edges.append([[self.rect.left, self.rect.top], [self.rect.left, self.rect.bottom], [-1.0, 0.0]])
        if not self.right_neighbour:
            self.edges.append([[self.rect.right, self.rect.top], [self.rect.right, self.rect.bottom], [1.0, 0.0]])
        if not self.bottom_neighbour:
            self.edges.append([[self.rect.left, self.rect.bottom], [self.rect.right, self.rect.bottom], [0.0, 1.0]])

    def draw(self, screen):
        screen.blit(self.surface, self.rect)

# Draw collision edges
#        if self.is_vertical_wall:
#            for edge in self.edges:
#                pygame.draw.line(screen, pygame.Color(255,50,50),edge[0],edge[1])
#        else:
#            for edge in self.edges:
#                pygame.draw.line(screen, pygame.Color(50,50,50),edge[0],edge[1])

    def is_point_inside(self, point):
        if self.rect.left < point[0] < self.rect.right:
            if self.rect.top < point[1] < self.rect.bottom:
                return True
        return False


def add_new_wall_if_unique(possible_new_wall, maze_walls):
    wall_already_exists = False
    for wall in maze_walls:
        if wall.id == possible_new_wall.id:
            wall_already_exists = True
    if not wall_already_exists:
        maze_walls.append(possible_new_wall)

    return maze_walls


def create_maze(width=11, height=16, complexity=.75, density=.75):
    # Only odd shapes
    shape = ((height // 2) * 2 + 1, (width // 2) * 2 + 1)
    # Adjust complexity and density relative to maze size
    complexity = int(complexity * (5 * (shape[0] + shape[1])))
    density = int(density * ((shape[0] // 2) * (shape[1] // 2)))
    # Build actual maze
    z = []
    for y in range(0, shape[0]):
        zero_list = []
        for x in range(0, shape[1]):
            zero_list.append(0)
        z.append(zero_list)
    # Fill borders
    for y in range(0, shape[0]):
        z[y][0] = 1
        z[y][-1] = 1

    z[0][:] = [1] * shape[1]
    z[-1][:] = [1] * shape[1]

    # Make aisles
    for m in range(density):
        x, y = random.randint(0, shape[1] // 2) * 2, random.randint(0, shape[0] // 2) * 2
        z[y][x] = 1
        for n in range(complexity):
            neighbours = []
            if x > 1:
                neighbours.append((y, x - 2))
            if x < shape[1] - 2:
                neighbours.append((y, x + 2))
            if y > 1:
                neighbours.append((y - 2, x))
            if y < shape[0] - 2:
                neighbours.append((y + 2, x))
            if len(neighbours):
                y_, x_ = neighbours[random.randint(0, len(neighbours) - 1)]
                if z[y_][x_] == 0:
                    z[y_][x_] = 1
                    z[y_ + (y - y_) // 2][x_ + (x - x_) // 2] = 1
                    x, y = x_, y_

    for y in range(1, shape[0]-1):
        for x in range(1, shape[1]-1):
            if z[y][x] == 0:
                wall_neighbours = []
                exits = 0
                if z[y+1][x] == 0:
                    exits += 1
                elif (y+1) != shape[0]-1:
                    wall_neighbours.append((y+1, x))
                if z[y][x+1] == 0:
                    exits += 1
                elif (x+1) != shape[1]-1:
                    wall_neighbours.append((y, x+1))
                if z[y][x-1] == 0:
                    exits += 1
                elif (x-1) != 0:
                    wall_neighbours.append((y, x-1))
                if z[y-1][x] == 0:
                    exits += 1
                elif (y-1) != 0:
                    wall_neighbours.append((y-1, x))

                if exits <= 1:
                    y_, x_ = wall_neighbours[random.randint(0, len(wall_neighbours) - 1)]
                    z[y_][x_] = 0

    maze_walls = []
    junction_points = []
    walkable_zones = []
    for y in range(0, shape[0]):
        for x in range(0, shape[1]):
            if z[y][x] == 1:
                # check for neighbours with a wall, if a wall is on it's own we just won't draw it
                if y + 1 < shape[0]:
                    if z[y+1][x] == 1:
                        maze_walls = add_new_wall_if_unique(MazeWall((y, x), (y + 1, x)), maze_walls)
                if y - 1 > 0:
                    if z[y-1][x] == 1:
                        maze_walls = add_new_wall_if_unique(MazeWall((y, x), (y - 1, x)), maze_walls)
                if x + 1 < shape[1]:
                    if z[y][x+1] == 1:
                        maze_walls = add_new_wall_if_unique(MazeWall((y, x), (y, x + 1)), maze_walls)
                if x - 1 > 0:
                    if z[y][x-1] == 1:
                        maze_walls = add_new_wall_if_unique(MazeWall((y, x), (y, x - 1)), maze_walls)
            elif z[y][x] == 0:
                if (z[y+1][x] == 1) and (z[y-1][x] == 1) and (z[y][x-1] == 0) and (z[y][x+1] == 0):
                    pass  # in horizontal corridor
                elif(z[y+1][x] == 0) and (z[y-1][x] == 0) and (z[y][x-1] == 1) and (z[y][x+1] == 1):
                    pass  # vertical corridor
                else:  # must be a point at which we can or need to change direction
                    junction_points.append(JunctionPoint(x, y))

                walkable_zones.append(WalkableZone(x, y))

    for wall in maze_walls:
        for other_wall in maze_walls:
            if wall.id != other_wall.id:
                thing1 = (wall.start_index[0] == other_wall.start_index[0] and
                          wall.start_index[1] == other_wall.start_index[1])
                thing2 = (wall.start_index[0] == other_wall.end_index[0] and
                          wall.start_index[1] == other_wall.end_index[1])
                thing3 = (wall.end_index[0] == other_wall.end_index[0] and
                          wall.end_index[1] == other_wall.end_index[1])
                thing4 = (wall.end_index[0] == other_wall.start_index[0] and
                          wall.end_index[1] == other_wall.start_index[1])
                if thing1 or thing2 or thing3 or thing4:
                    if wall.is_vertical_wall and other_wall.is_vertical_wall:
                        if thing2:
                            wall.top_neighbour = True
                        if thing4:
                            wall.bottom_neighbour = True
                    if wall.is_horizontal_wall and other_wall.is_horizontal_wall:
                        if thing4:
                            wall.right_neighbour = True
                        if thing2:
                            wall.left_neighbour = True

                    if wall.is_horizontal_wall and other_wall.is_vertical_wall:
                        if thing1:
                            wall.is_top_corner = True
                            wall.is_left_corner = True
                        if thing2:
                            wall.is_bottom_corner = True
                            wall.is_left_corner = True
                        if thing3:
                            wall.is_bottom_corner = True
                            wall.is_right_corner = True
                        if thing4:
                            wall.is_top_corner = True
                            wall.is_right_corner = True
                            
                    if wall.is_vertical_wall and other_wall.is_horizontal_wall:
                        if thing1:
                            wall.is_top_corner = True
                            wall.is_left_corner = True
                            wall.top_neighbour = True
                        if thing2:
                            wall.is_top_corner = True
                            wall.is_right_corner = True
                            wall.top_neighbour = True
                        if thing3:
                            wall.is_bottom_corner = True
                            wall.is_right_corner = True
                            wall.bottom_neighbour = True
                        if thing4:
                            wall.is_bottom_corner = True
                            wall.is_left_corner = True
                            wall.bottom_neighbour = True

    for wall in maze_walls:
        wall.generate_edges()

    return [maze_walls, junction_points, walkable_zones]
