import math
import pygame


class BaseProjectile(pygame.sprite.Sprite):

    def __init__(self, *groups):
        super().__init__(*groups)

        self.image = None
        self.rect = None

        self.heading_vector = None
        self.bullet_speed = None

    def is_controlled(self):
        return False
    
    def fire_pressed(self, projectiles):
        return None

    def should_lock_tank_controls(self):
        return False

    def update(self, time_delta, all_sprites, maze_walls, players):
        pass

    def rotate_left(self, time_delta):
        pass
 
    def rotate_right(self, time_delta):
        pass

    def handle_collision(self, all_unique_collision_points, collision_points, temp_rect, bullet_position,
                         normals, maze_walls, time_delta, loops):
        bullet_position = bullet_position
        if len(collision_points) > 0 and loops < 10:
            loops += 1
            # collision_vec = [bullet_position[0] - collision_points[0][0], bullet_position[1] - collision_points[0][1]]
            # collision_vec_len = math.sqrt((collision_vec[0] ** 2) + (collision_vec[1] ** 2))
            # normal_collision_vec = [collision_vec[0]/collision_vec_len, collision_vec[1]/collision_vec_len]

            # collision_overlap = self.collision_delta

            bullet_position[0] -= (self.heading_vector[0] * self.bullet_speed * time_delta)
            bullet_position[1] -= (self.heading_vector[1] * self.bullet_speed * time_delta)

            temp_rect.center = (int(bullet_position[0]), int(bullet_position[1]))
      
            self.collision_loop(temp_rect, maze_walls, all_unique_collision_points,
                                collision_points, normals)

            bullet_position_and_normal = self.handle_collision(all_unique_collision_points, collision_points,
                                                               temp_rect, bullet_position, normals, maze_walls,
                                                               time_delta, loops)
            bullet_position = bullet_position_and_normal[0]
            normals = bullet_position_and_normal[1]

        return [bullet_position, normals]

    def test_tank_collision(self, projectile, tank):
        collided = False
        if projectile.rect.colliderect(tank.rect):
            rect = projectile.rect
            result1 = tank.test_rect_edge_against_real_bounds(rect.topleft, rect.topright)
            result2 = tank.test_rect_edge_against_real_bounds(rect.topleft, rect.bottomleft)
            result3 = tank.test_rect_edge_against_real_bounds(rect.topright, rect.bottomright)
            result4 = tank.test_rect_edge_against_real_bounds(rect.bottomleft, rect.bottomright)

            if result1:
                collided = True
            if result2: 
                collided = True
            if result3:
                collided = True
            if result4: 
                collided = True

        return collided

    def collision_loop(self, rect, maze_walls, all_unique_collision_points, collision_points, normals):
        collided = False
        for wall in maze_walls:
            result = self.test_wall_collision(rect, wall)
            if result[0]:
                for collisionPoint in result[1]:
                    collision_points.append(collisionPoint)
                    is_unique = True
                    for uniquePoint in all_unique_collision_points:
                        if uniquePoint[0] == collisionPoint[0] and uniquePoint[1] == collisionPoint[1]:
                            is_unique = False
                    if is_unique:
                        all_unique_collision_points.append(collisionPoint)
                collided = True
                for normal in result[2]:
                    normals.append(normal)

        return collided

    def test_wall_collision(self, temp_rect, wall):
        collided = False
        collision_points = []
        normals = []

        if temp_rect.colliderect(wall.rect):
            for edge in wall.edges:
                collided_this_edge = False

                result1 = self.line_intersect_test((edge[0], edge[1]), (temp_rect.topright, temp_rect.topleft))
                result2 = self.line_intersect_test((edge[0], edge[1]), (temp_rect.topleft, temp_rect.bottomleft))
                result3 = self.line_intersect_test((edge[0], edge[1]), (temp_rect.topright, temp_rect.bottomright))
                result4 = self.line_intersect_test((edge[0], edge[1]), (temp_rect.bottomleft, temp_rect.bottomright))

                result5 = self.line_inside_rect(temp_rect, edge)

                if result1[0]:
                    collided_this_edge = True
                    collided = True
                    collision_points.append(result1[1])
                if result2[0]:
                    collided_this_edge = True
                    collided = True
                    collision_points.append(result2[1])
                if result3[0]:
                    collided_this_edge = True
                    collided = True
                    collision_points.append(result3[1])
                if result4[0]:
                    collided_this_edge = True
                    collided = True
                    collision_points.append(result4[1])
                if result5:  # just add the normal of lines inside, makes for better collision planes
                    collided_this_edge = True
                    collided = True

                if collided_this_edge:
                    normals.append(edge[2])
            
        return [collided, collision_points, normals]

    @staticmethod
    def line_inside_rect(rect, line):
        is_a_inside = False
        is_b_inside = False
        if (rect.left <= line[0][0] <= rect.right) and (rect.top <= line[0][1] <= rect.bottom):
            is_a_inside = True

        if (rect.left <= line[1][0] <= rect.right) and (rect.top <= line[1][1] <= rect.bottom):
            is_b_inside = True

        return is_a_inside and is_b_inside

    @staticmethod
    def line_intersect_test(line_a_b, line_c_d):
        intersection_truth = False
        a = line_a_b[0]
        b = line_a_b[1]
        c = line_c_d[0]
        d = line_c_d[1]

        cm_p = (c[0] - a[0], c[1] - a[1])
        r = (b[0] - a[0], b[1] - a[1])
        s = (d[0] - c[0], d[1] - c[1])

        cm_pxr = cm_p[0] * r[1] - cm_p[1] * r[0]
        cm_pxs = cm_p[0] * s[1] - cm_p[1] * s[0]
        rxs = r[0] * s[1] - r[1] * s[0]

        intersection_point = [0.0, 0.0]
        if cm_pxr == 0.0:
            # Lines are collinear, and so intersect if they have any overlap
            intersection_truth1 = ((c[0] - a[0] < 0.0) != (c[0] - b[0] < 0.0))
            intersection_truth2 = ((c[1] - a[1] < 0.0) != (c[1] - b[1] < 0.0))

            if intersection_truth1:  # horiz overlap ?
                if a[0] < b[0]:  # A higher than B
                    if c[0] < d[0]:  # C higher than D
                        intersect_point_x = b[0] - (b[0] - c[0])
                    else:
                        intersect_point_x = b[0] - (b[0] - d[0])
                else:
                    if c[0] < d[0]:  # C higher than D
                        intersect_point_x = a[0] - (a[0] - c[0])
                    else:
                        intersect_point_x = a[0] - (a[0] - d[0])

                line_slope = 0.0
                if b[0]-a[0] != 0.0:
                    line_slope = (b[1] - a[1])/(b[0]-a[0])

                intersect_point_y = line_slope * (intersect_point_x - a[0]) + a[1]

                intersection_point = [intersect_point_x, intersect_point_y]
                # print("Weird horiz: " + str(intersect_point_x) + ", " + str(intersect_point_y))

            if intersection_truth2:  # vert overlap?

                if a[1] < b[1]:  # A higher than B
                    if c[1] < d[1]:  # C higher than D
                        intersect_point_y = b[1] - (b[1] - c[1])
                    else:
                        intersect_point_y = b[1] - (b[1] - d[1])
                else:
                    if c[1] < d[1]:  # C higher than D
                        intersect_point_y = a[1] - (a[1] - c[1])
                    else:
                        intersect_point_y = a[1] - (a[1] - d[1])

                line_slope = 0.0
                if b[0]-a[0] != 0.0:
                    line_slope = (b[1] - a[1])/(b[0]-a[0])

                if line_slope != 0.0:
                    intersect_point_x = (intersect_point_y - a[1])/line_slope + a[0]
                else:
                    intersect_point_x = a[0]

                intersection_point = [intersect_point_x, intersect_point_y]

            return [intersection_truth1 or intersection_truth2, intersection_point, 1]

        if rxs == 0.0:
            return [intersection_truth, intersection_point, 2]  # Lines are parallel.

        rxsr = 1.0 / rxs
        t = cm_pxs * rxsr
        u = cm_pxr * rxsr

        if (t >= 0.0) and (t <= 1.0) and (u >= 0.0) and (u <= 1.0):  # lines intersect
            intersection_truth = True
            intersection_point = [a[0] + t*r[0], a[1] + t*r[1]]

        return [intersection_truth, intersection_point, 3]

    @staticmethod
    def distance_from_line(point, line):

        x1 = line[0][0]
        y1 = line[0][1]
        x2 = line[1][0]
        y2 = line[1][1]
        x3 = point[0]
        y3 = point[1]

        px = x2-x1
        py = y2-y1

        something = px*px + py*py

        u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        # Note: If the actual distance does not matter,
        # if you only want to compare what this function
        distance = math.sqrt(dx ** 2 + dy ** 2)
        return distance
