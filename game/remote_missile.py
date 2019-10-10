import math
import pygame

from game.base_projectile import BaseProjectile


class RemoteMissile(BaseProjectile):
    def __init__(self, initial_heading_vector, start_position, owner_id, explosion_data, *groups):

        # we want to start projectiles a little in front of the tank so they don't
        # immediately overlap with the tank that fires them and blow it up
        super().__init__(*groups)
        safe_start_position = [start_position[0], start_position[1]]
        safe_start_position[0] += initial_heading_vector[0] * 16.0
        safe_start_position[1] += initial_heading_vector[1] * 16.0
        
        self.explosion_data = explosion_data
        self.heading_vector = [initial_heading_vector[0], initial_heading_vector[1]]
        heading_vector_len = math.sqrt((self.heading_vector[0] ** 2) + (self.heading_vector[1] ** 2))
        self.heading_vector = [self.heading_vector[0] / heading_vector_len,
                               self.heading_vector[1] / heading_vector_len]

        self.current_angle = math.atan2(self.heading_vector[0], self.heading_vector[1]) * 180 / math.pi
        self.bullet_position = safe_start_position
        self.owner_id = owner_id

        self.original_image = pygame.image.load('images/missile.png').convert_alpha()
        self.image = pygame.transform.rotate(self.original_image, self.current_angle)
        self.rect = self.image.get_rect()

        self.bullet_speed = 150.0
        self.rotate_speed = 150.0

        self.bullet_life_time = 7.0
        self.should_die = False
        self.bounces = 0

        self.collision_delta = 1.0

        self.test_rotate_angle = self.current_angle

        self.invalid_normals_printed = False

    def is_controlled(self):
        return True
                             
    def should_lock_tank_controls(self):
        return True

    def fire_pressed(self, projectiles):
        self.should_die = True

    def rotate_left(self, time_delta):
        self.test_rotate_angle = self.current_angle
        self.test_rotate_angle += self.rotate_speed * time_delta

    def rotate_right(self, time_delta):
        self.test_rotate_angle = self.current_angle
        self.test_rotate_angle -= self.rotate_speed * time_delta

    def draw_last_collision(self, screen):
        pass

    def update(self, time_delta, all_sprites, maze_walls, players):
        collided = False
        all_unique_collision_points = []
        collision_points = []
        normals = []

        for wall in maze_walls:
            result = self.test_wall_collision(self.rect, wall)
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

        if collided:     
            self.bounces += 1
            loops = 0
            bullet_position_and_normal = self.handle_collision(all_unique_collision_points, collision_points,
                                                               self.rect, self.bullet_position, normals,
                                                               maze_walls, time_delta, loops)
            # bullet_position = bullet_position_and_normal[0]
            normals = bullet_position_and_normal[1]

            heading_vector_len = math.sqrt((self.heading_vector[0] ** 2) + (self.heading_vector[1] ** 2))
            self.heading_vector = [self.heading_vector[0] / heading_vector_len,
                                   self.heading_vector[1] / heading_vector_len]

            # to calculate our collision surface normal we look at all the points of collision, imagine they are
            # smoothed out into a flat surface and then grab the tangent angle of that surface. We then pick our
            # final normal out of all our collided surfaces by comparing the dot product  of our 'tangent' vector
            # and each of the surfaces' vectors. Not sure if this is a good approach or a terrible one, but it's
            # what I'm using.
            final_normal = [0.0, 0.0]
            if len(all_unique_collision_points) > 0:
                
                collision_point_plane = [0.0, 0.0]

                sub_vectors = []
                for point in all_unique_collision_points:
                    sub_vectors.append([all_unique_collision_points[0][0] - point[0],
                                        all_unique_collision_points[0][1] - point[1]])
                
                for vector in sub_vectors:
                    collision_point_plane[0] += abs(vector[0])
                    collision_point_plane[1] += abs(vector[1])

                collision_point_plane_len = math.sqrt((collision_point_plane[0] ** 2) + (collision_point_plane[1] ** 2))
                if collision_point_plane_len > 0.0:
                    collision_point_plane = [collision_point_plane[0]/collision_point_plane_len,
                                             collision_point_plane[1]/collision_point_plane_len]

                tangent_or_normal_of_plane = [-collision_point_plane[1], -collision_point_plane[0]]

                greatest_abs_dot = 0.0
                for normal in normals:
                    collision_heading_dot = normal[0] * self.heading_vector[0] + normal[1] * self.heading_vector[1]
                    if collision_heading_dot < 0.0:  # remove back faces from consideration

                        dot = normal[0] * tangent_or_normal_of_plane[0] + normal[1] * tangent_or_normal_of_plane[1]

                        if abs(dot) > greatest_abs_dot:
                            greatest_abs_dot = abs(dot)
                            final_normal = normal

            collision_heading_dot = final_normal[0] * self.heading_vector[0] + final_normal[1] * self.heading_vector[1]

            self.heading_vector[0] = self.heading_vector[0] - (2 * collision_heading_dot * final_normal[0])
            self.heading_vector[1] = self.heading_vector[1] - (2 * collision_heading_dot * final_normal[1])

            heading_vector_len = math.sqrt((self.heading_vector[0] ** 2) + (self.heading_vector[1] ** 2))
            self.heading_vector = [self.heading_vector[0] / heading_vector_len,
                                   self.heading_vector[1] / heading_vector_len]
            self.current_angle = math.atan2(self.heading_vector[0], self.heading_vector[1]) * 180 / math.pi
            self.test_rotate_angle = self.current_angle
            self.image = pygame.transform.rotate(self.original_image, self.current_angle)
            self.rect = self.image.get_rect()
            self.rect.center = [int(self.bullet_position[0]), int(self.bullet_position[1])]
        else:
            self.current_angle = self.test_rotate_angle

            self.image = pygame.transform.rotate(self.original_image, self.current_angle)
            self.rect = self.image.get_rect()
            heading = math.radians(90.0 - float(self.current_angle))
            self.heading_vector = [math.cos(heading), math.sin(heading)]
        
        self.bullet_position[0] += (self.heading_vector[0] * self.bullet_speed * time_delta)
        self.bullet_position[1] += (self.heading_vector[1] * self.bullet_speed * time_delta)
        self.rect.center = (int(self.bullet_position[0]), int(self.bullet_position[1]))
        all_sprites.add(self)

        self.bullet_life_time -= time_delta
        if self.bullet_life_time < 0.0:
            self.should_die = True
            self.explosion_data.create_explosion(self.bullet_position, 16)
        return all_sprites
