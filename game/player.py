import math
import pygame
from pygame.locals import *
from game.normal_bullet import Bullet
from game.cluster_bomb import ClusterBomb
from game.remote_missile import RemoteMissile
from game.laser import Laser


class Scheme:
    def __init__(self):
        self.forward = K_UP
        self.backward = K_DOWN
        self.left = K_LEFT
        self.right = K_RIGHT
        self.fire = K_RSHIFT


class Player(pygame.sprite.Sprite):
    def __init__(self, explosion_data, start_pos, control_scheme, tank_image_name, player_id, player_score, *groups):

        super().__init__(*groups)
        self.explosion_data = explosion_data
        self.player_id = player_id
        self.player_score = player_score
        self.scheme = control_scheme
        self.image_name = tank_image_name
        self.original_tank_image = pygame.image.load(tank_image_name).convert_alpha()
        self.tank_image = self.original_tank_image.copy()

        self.image = self.tank_image
        self.rect = self.tank_image.get_rect()
        self.rect.topleft = start_pos

        self.current_tank_angle = 0

        self.real_bounds_tl = [self.rect.topleft[0], self.rect.topleft[1] + 6]
        self.real_bounds_tr = [self.rect.topright[0] - 3, self.rect.topright[1] + 6]
        self.real_bounds_bl = [self.rect.bottomleft[0], self.rect.bottomleft[1]]
        self.real_bounds_br = [self.rect.bottomright[0] - 3, self.rect.bottomright[1]]

        self.real_bounds_width = self.real_bounds_tr[0] - self.real_bounds_tl[0]
        self.real_bounds_height = self.real_bounds_bl[1] - self.real_bounds_tl[1]
        self.half_longest_diagonal = math.sqrt(self.real_bounds_width ** 2 + self.real_bounds_height ** 2) / 2

        self.should_left_rotate = False
        self.should_right_rotate = False
        self.should_move_forward = False
        self.should_move_backward = False

        self.tank_speed = 0.0
        self.tank_acceleration = 100.0
        self.tank_top_speed = 100.0
        self.friction = 300.0

        self.tank_rotate_speed = 0.0
        self.tank_rotate_top_speed = 150.0
        self.tank_rotate_acceleration = 400.0
        self.rotate_friction = 1600.0

        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]

        self.tank_front = [0.0, 0.0]

        self.should_fire = False

        self.should_die = False
        self.collision_delta = 0.1

        self.active_weapon = "bullets"
        self.have_active_power_up = False
        self.controlled_projectile = None

    def on_death(self):
        self.explosion_data.create_explosion(self.position)

    def activate_power_up(self, type_name, display_name):
        self.have_active_power_up = True
        self.active_weapon = type_name
        self.player_score.activePowerUp = display_name

    def deactivate_power_up(self):
        self.have_active_power_up = False
        self.active_weapon = "bullets"
        self.player_score.activePowerUp = "None"

    def setup_projectile(self, projectile, projectiles):
        if projectile.is_controlled():
            self.controlled_projectile = projectile
        projectiles.append(projectile)
        self.deactivate_power_up()
                    
    def deactivate_controlled_projectile(self):
        self.controlled_projectile = None

    def update_weapon(self, projectiles, time_delta):
        self.tank_front = [self.real_bounds_tl[0] + (self.real_bounds_tr[0] - self.real_bounds_tl[0]) / 2.0,
                           self.real_bounds_tl[1] + (self.real_bounds_tr[1] - self.real_bounds_tl[1]) / 2.0]

        if self.controlled_projectile is not None:
            if self.controlled_projectile.should_die:
                self.deactivate_controlled_projectile()
            else:  
                if self.should_fire:
                    self.should_fire = False
                    self.controlled_projectile = self.controlled_projectile.fire_pressed(projectiles)
                    if self.controlled_projectile is None:
                        self.deactivate_controlled_projectile()
                if self.controlled_projectile is not None:
                    if self.should_left_rotate and self.controlled_projectile.should_lock_tank_controls():
                        self.controlled_projectile.rotate_left(time_delta)

                    if self.should_right_rotate and self.controlled_projectile.should_lock_tank_controls():
                        self.controlled_projectile.rotate_right(time_delta)
                        
        else:
            if self.should_fire:
                self.should_fire = False
                heading = math.radians(90.0 - float(self.current_tank_angle))
                heading_vector = (-math.cos(heading), -math.sin(heading))

                if self.active_weapon == "bullets":
                    bullet = Bullet(heading_vector, self.tank_front, self.player_id)
                    self.setup_projectile(bullet, projectiles)
                elif self.active_weapon == "remote_missile":
                    remote_missile = RemoteMissile(heading_vector, self.tank_front, self.player_id, self.explosion_data)
                    self.setup_projectile(remote_missile, projectiles)
                elif self.active_weapon == "cluster_bomb":
                    cluster_bomb = ClusterBomb(heading_vector, self.tank_front, self.player_id)
                    self.setup_projectile(cluster_bomb, projectiles)
                elif self.active_weapon == "laser":
                    laser_beam = Laser(heading_vector, self.tank_front, self.player_id)
                    self.setup_projectile(laser_beam, projectiles)

    def update_real_bounds(self, position):
        heading = math.radians(-float(self.current_tank_angle))
        self.real_bounds_tl[0] = position[0] + (((-self.real_bounds_width / 2) * math.cos(heading))
                                                - ((-self.real_bounds_height / 2) * math.sin(heading)))
        self.real_bounds_tl[1] = position[1] + (((-self.real_bounds_width / 2) * math.sin(heading))
                                                + ((-self.real_bounds_height / 2) * math.cos(heading)))
        self.real_bounds_tr[0] = position[0] + (((self.real_bounds_width / 2) * math.cos(heading))
                                                - ((-self.real_bounds_height / 2) * math.sin(heading)))
        self.real_bounds_tr[1] = position[1] + (((self.real_bounds_width / 2) * math.sin(heading))
                                                + ((-self.real_bounds_height / 2) * math.cos(heading)))
        self.real_bounds_bl[0] = position[0] + (((-self.real_bounds_width / 2) * math.cos(heading))
                                                - ((self.real_bounds_height / 2) * math.sin(heading)))
        self.real_bounds_bl[1] = position[1] + (((-self.real_bounds_width / 2) * math.sin(heading))
                                                + ((self.real_bounds_height / 2) * math.cos(heading)))
        self.real_bounds_br[0] = position[0] + (((self.real_bounds_width / 2) * math.cos(heading))
                                                - ((self.real_bounds_height / 2) * math.sin(heading)))
        self.real_bounds_br[1] = position[1] + (((self.real_bounds_width / 2) * math.sin(heading))
                                                + ((self.real_bounds_height / 2) * math.cos(heading)))

    def draw_rotated_real_bounds(self, screen):
        point_list = [self.real_bounds_tl, self.real_bounds_tr, self.real_bounds_br, self.real_bounds_bl]
        # noinspection PyArgumentList
        pygame.draw.lines(screen, (255, 0, 0), True, point_list, 1)
    
    def update_sprite(self, all_sprites):
        self.image = self.tank_image
        all_sprites.add(self)
        return all_sprites

    def process_event(self, event):

        if event.type == KEYDOWN:     
            if event.key == self.scheme.left:
                self.should_left_rotate = True
            if event.key == self.scheme.right:
                self.should_right_rotate = True
            if event.key == self.scheme.forward:
                self.should_move_forward = True
            if event.key == self.scheme.backward:
                self.should_move_backward = True
            if event.key == self.scheme.fire:
                self.should_fire = True
                # print("fire!")
        elif event.type == KEYUP:
            if event.key == self.scheme.left:
                self.should_left_rotate = False
            if event.key == self.scheme.right:
                self.should_right_rotate = False
            if event.key == self.scheme.forward:
                self.should_move_forward = False
            if event.key == self.scheme.backward:
                self.should_move_backward = False

    def update_movement_and_collision(self, time_delta, maze_walls, projectiles, score_board):
        for projectile in projectiles:
            if projectile.test_tank_collision(projectile, self):
                self.should_die = True
                self.on_death()
                projectile.shouldDie = True
                for player_score in score_board:
                    if projectile.owner_id == player_score.player_id:
                        if projectile.owner_id == self.player_id:
                            player_score.score -= 1
                        else:
                            player_score.score += 1

        self.update_weapon(projectiles, time_delta)

        temp_rect = self.rect.copy()
        temp_tank_pos = [0.0, 0.0]
        temp_tank_pos[0] = self.position[0]
        temp_tank_pos[1] = self.position[1]
        
        if self.controlled_projectile is None or not self.controlled_projectile.should_lock_tank_controls():
            rotate_dir = 1
            if self.should_move_backward:
                rotate_dir = -1
            if self.should_left_rotate:
                if abs(self.tank_rotate_speed) < self.tank_rotate_top_speed:
                    if self.tank_rotate_speed < 0.0:
                        self.tank_rotate_speed += (self.tank_rotate_acceleration + self.rotate_friction) \
                                                  * time_delta * rotate_dir
                    else:
                        self.tank_rotate_speed += self.tank_rotate_acceleration * time_delta * rotate_dir

            elif self.should_right_rotate:
                if abs(self.tank_rotate_speed) < self.tank_rotate_top_speed:
                    if self.tank_rotate_speed > 0.0:
                        self.tank_rotate_speed -= (self.tank_rotate_acceleration + self.rotate_friction) \
                                                  * time_delta * rotate_dir
                    else:
                        self.tank_rotate_speed -= self.tank_rotate_acceleration * time_delta * rotate_dir

            else:
                if 5.0 > self.tank_rotate_speed > -5.0:  # make sure we don't wobble around 0.0
                    self.tank_rotate_speed = 0.0
                elif self.tank_rotate_speed > 0.0:
                    self.tank_rotate_speed -= self.rotate_friction * time_delta
                elif self.tank_rotate_speed < 0.0:
                    self.tank_rotate_speed += self.rotate_friction * time_delta

            if abs(self.tank_rotate_speed) > 0.0:
                self.current_tank_angle += self.tank_rotate_speed * time_delta
                loc = self.rect.center
                self.tank_image = pygame.transform.rotate(self.original_tank_image, self.current_tank_angle)
                self.rect = self.tank_image.get_rect()
                self.rect.center = loc

            heading = math.radians(90.0 - float(self.current_tank_angle))
            heading_vector = (math.cos(heading), math.sin(heading))
            
            if self.should_move_forward:
                if abs(self.tank_speed) < self.tank_top_speed:
                    self.tank_speed += self.tank_acceleration * time_delta
                
            elif self.should_move_backward:
                if abs(self.tank_speed) < self.tank_top_speed:
                    self.tank_speed -= self.tank_acceleration * time_delta
            else:
                if 5.0 > self.tank_speed > -5.0:  # make sure we don't wobble around 0.0
                    self.tank_speed = 0.0
                elif self.tank_speed > 0.0:
                    self.tank_speed -= self.friction * time_delta
                elif self.tank_speed < 0.0:
                    self.tank_speed += self.friction * time_delta

            temp_tank_pos[0] -= (heading_vector[0] * self.tank_speed * time_delta)
            temp_tank_pos[1] -= (heading_vector[1] * self.tank_speed * time_delta)
            temp_rect.center = (int(temp_tank_pos[0]), int(temp_tank_pos[1]))

        self.update_real_bounds(temp_tank_pos)
            
        collided = False
        collision_points = []
        for wall in maze_walls:
            result = self.test_wall_collision(temp_rect, wall)
            if result[0]:
                for collisionPoint in result[1]:
                    collision_points.append(collisionPoint)
                collided = True

        if collided:
            loops = 0
            temp_tank_pos = self.handle_collision(collision_points, temp_tank_pos, temp_rect, maze_walls, loops)
                
            self.position[0] = temp_tank_pos[0]
            self.position[1] = temp_tank_pos[1]

        else:
            self.position[0] = temp_tank_pos[0]
            self.position[1] = temp_tank_pos[1]

        self.update_real_bounds(self.position)

        self.rect.center = (int(self.position[0]), int(self.position[1]))

    def handle_collision(self, collision_points, temp_tank_pos, temp_rect, maze_walls, loops):
        temp_tank_pos = temp_tank_pos
        
        if len(collision_points) > 0 and loops < 10:
            loops += 1
            all_collision_vecs = [0.0, 0.0]
            for point in collision_points:
                all_collision_vecs[0] += temp_tank_pos[0] - point[0]
                all_collision_vecs[1] += temp_tank_pos[1] - point[1]
            average_collision_vec = [0.0, 0.0]
            average_collision_vec[0] = all_collision_vecs[0]/len(collision_points)
            average_collision_vec[1] = all_collision_vecs[1]/len(collision_points)
            collision_vec_len = math.sqrt((average_collision_vec[0] ** 2) + (average_collision_vec[1] ** 2))
            normal_collision_vec = [average_collision_vec[0]/collision_vec_len,
                                    average_collision_vec[1]/collision_vec_len]

            collision_overlap = min(1.0, max(0.3, (self.half_longest_diagonal - collision_vec_len)))
            
            normal_collision_vec[0] *= collision_overlap
            normal_collision_vec[1] *= collision_overlap

            temp_tank_pos[0] += normal_collision_vec[0]
            temp_tank_pos[1] += normal_collision_vec[1]

            temp_rect.center = (int(temp_tank_pos[0]), int(temp_tank_pos[1]))

            self.update_real_bounds(temp_tank_pos)
            
            # collided = False
            collision_points = []
            for wall in maze_walls:
                result = self.test_wall_collision(temp_rect, wall)
                if result[0]:
                    for collisionPoint in result[1]:
                        collision_points.append(collisionPoint)
                    # collided = True

            temp_tank_pos = self.handle_collision(collision_points, temp_tank_pos, temp_rect, maze_walls, loops)

        return temp_tank_pos

    def test_pick_up_collision(self, pickup_rect):

        collided = False
        if pickup_rect.colliderect(self.rect):
            result1 = self.test_rect_edge_against_real_bounds(pickup_rect.topleft, pickup_rect.topright)
            result2 = self.test_rect_edge_against_real_bounds(pickup_rect.topleft, pickup_rect.bottomleft)
            result3 = self.test_rect_edge_against_real_bounds(pickup_rect.topright, pickup_rect.bottomright)
            result4 = self.test_rect_edge_against_real_bounds(pickup_rect.bottomleft, pickup_rect.bottomright)
            if result1:
                collided = True
            if result2: 
                collided = True
            if result3:
                collided = True
            if result4: 
                collided = True

        return collided

    def test_rect_edge_against_real_bounds(self, start_edge, end_edge):
        collided = False
        result1 = self.line_intersect_test((start_edge, end_edge), (self.real_bounds_tl, self.real_bounds_tr))
        result2 = self.line_intersect_test((start_edge, end_edge), (self.real_bounds_tl, self.real_bounds_bl))
        result3 = self.line_intersect_test((start_edge, end_edge), (self.real_bounds_tr, self.real_bounds_br))
        result4 = self.line_intersect_test((start_edge, end_edge), (self.real_bounds_bl, self.real_bounds_br))

        if result1[0]:
            collided = True
        if result2[0]: 
            collided = True
        if result3[0]:
            collided = True
        if result4[0]: 
            collided = True

        return collided

    def test_wall_collision(self, temp_rect, wall):
        collided = False
        collision_points = []
        if temp_rect.colliderect(wall.rect):
            # do top collision
            for edge in wall.edges:
                result1 = self.line_intersect_test((edge[0], edge[1]), (self.real_bounds_tl, self.real_bounds_tr))
                result2 = self.line_intersect_test((edge[0], edge[1]), (self.real_bounds_tl, self.real_bounds_bl))
                result3 = self.line_intersect_test((edge[0], edge[1]), (self.real_bounds_tr, self.real_bounds_br))
                result4 = self.line_intersect_test((edge[0], edge[1]), (self.real_bounds_bl, self.real_bounds_br))
                if result1[0]:
                    collided = True
                    collision_points.append(result1[1])
                if result2[0]: 
                    collided = True
                    collision_points.append(result2[1])
                if result3[0]:
                    collided = True
                    collision_points.append(result3[1])
                if result4[0]: 
                    collided = True
                    collision_points.append(result4[1])

        return [collided, collision_points]

    @staticmethod
    def line_intersect_test(line_ab, line_cd):

        a = line_ab[0]
        b = line_ab[1]
        c = line_cd[0]
        d = line_cd[1]

        cm_p = (c[0] - a[0], c[1] - a[1])
        r = (b[0] - a[0], b[1] - a[1])
        s = (d[0] - c[0], d[1] - c[1])

        cm_pxr = cm_p[0] * r[1] - cm_p[1] * r[0]
        cm_pxs = cm_p[0] * s[1] - cm_p[1] * s[0]
        rxs = r[0] * s[1] - r[1] * s[0]

        intersection_point = [0.0, 0.0]
        intersection_truth = False
        if cm_pxr == 0.0:
            # Lines are collinear, and so intersect if they have any overlap
            intersection_truth1 = ((c[0] - a[0] < 0.0) != (c[0] - b[0] < 0.0))
            intersection_truth2 = ((c[1] - a[1] < 0.0) != (c[1] - b[1] < 0.0))
            intersection_point[0] = c[0] + (d[0]-c[0])/2  # set collision point to middle of line
            intersection_point[1] = c[1] + (d[1]-c[1])/2
                
            return [intersection_truth1 or intersection_truth2, intersection_point]

        if rxs == 0.0:
            return [intersection_truth, intersection_point]  # Lines are parallel.

        rxsr = 1.0 / rxs
        t = cm_pxs * rxsr
        u = cm_pxr * rxsr

        if (t >= 0.0) and (t <= 1.0) and (u >= 0.0) and (u <= 1.0):  # lines intersect
            intersection_truth = True
            intersection_point = [a[0] + t*r[0], a[1] + t*r[1]]

        return [intersection_truth, intersection_point]

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
        # returns to other results of this function, you
        # can just return the squared distance instead
        # (i.e. remove the sqrt) to gain a little performance

        dist = math.sqrt(dx*dx + dy*dy)

        return dist


class RespawnPlayer:
    def __init__(self, player):
        self.control_scheme = player.scheme
        self.image = player.image_name
        self.player_id = player.player_id
        self.score = player.player_score
        self.score.active_power_up = "None"
        
        self.respawn_timer = 2.0
        self.time_to_spawn = False
        self.has_respawned = False

    def update(self, frame_time_ms):
        self.respawn_timer -= (frame_time_ms / 1000.0)
        if self.respawn_timer < 0.0:
            self.time_to_spawn = True


class PlayerScore:
    def __init__(self, player_id, screen_position):
        self.player_id = player_id
        self.screen_position = screen_position
        self.score = 0
        self.active_power_up = "None"

    def reset_score(self):
        self.score = 0
        self.active_power_up = "None"
