import math
import pygame

from game.base_projectile import BaseProjectile


class Laser(BaseProjectile):
    def __init__(self, initial_heading_vector, start_position, owner_id, *groups):

        # we want to start projectiles a little in front of the tank so they don't
        # immediately overlap with the tank that fires them and blow it up
        super().__init__(*groups)
        safe_start_position = [start_position[0], start_position[1]]
        safe_start_position[0] += initial_heading_vector[0] * 5.0
        safe_start_position[1] += initial_heading_vector[1] * 5.0

        # normalise heading vector
        self.heading_vector = [initial_heading_vector[0], initial_heading_vector[1]]
        heading_vector_len = math.sqrt((self.heading_vector[0] ** 2) + (self.heading_vector[1] ** 2))
        self.heading_vector = [self.heading_vector[0] / heading_vector_len, self.heading_vector[1] / heading_vector_len]

        self.current_angle = math.atan2(self.heading_vector[0], self.heading_vector[1]) * 180 / math.pi
        self.position = safe_start_position
        self.owner_id = owner_id

        self.total_life_time = 1.0
        self.life_time_acc = self.total_life_time
        self.should_die = False

        self.laser_length = 500.0
        self.deadly_laser_length = 0.0

        self.image = pygame.Surface([2, int(self.laser_length)])
        self.image.fill(pygame.Color(150, 50, 50, 150), None, pygame.BLEND_RGBA_ADD)
        self.image.set_colorkey(pygame.Color("#000000"))
        self.image = pygame.transform.rotate(self.image, self.current_angle)
        self.image.set_alpha(150)
        self.rect = self.image.get_rect()

        self.rect.center = [int(self.position[0] + (self.heading_vector[0] * self.laser_length / 2)),
                            int(self.position[1] + (self.heading_vector[1] * self.laser_length / 2))]

        self.deadly_sprite = pygame.sprite.Sprite()

    def is_controlled(self):
        return True
                             
    def fire_pressed(self, projectiles):
        return self

    def should_lock_tank_controls(self):
        return True
    
    def update(self, time_delta, all_sprites, maze_walls, players):
        all_sprites.add(self)
        
        laser_lerp = (self.total_life_time - self.life_time_acc) / self.total_life_time
        self.deadly_laser_length = self.lerp(0.0, self.laser_length, laser_lerp)

        self.deadly_sprite.image = pygame.Surface([4, int(self.deadly_laser_length)])
        self.deadly_sprite.image.fill(pygame.Color(255, 50, 50, 150), None, pygame.BLEND_RGBA_ADD)
        self.deadly_sprite.image.set_colorkey(pygame.Color("#000000"))
        self.deadly_sprite.image = pygame.transform.rotate(self.deadly_sprite.image, self.current_angle)
        self.deadly_sprite.image.set_alpha(150)
        self.deadly_sprite.rect = self.deadly_sprite.image.get_rect()

        self.deadly_sprite.rect.center = [int(self.position[0] + (self.heading_vector[0] * self.deadly_laser_length/2)),
                                          int(self.position[1] + (self.heading_vector[1] * self.deadly_laser_length/2))]

        all_sprites.add(self.deadly_sprite)
        
        self.life_time_acc -= time_delta
        if self.life_time_acc < 0.0:
            self.should_die = True
        return all_sprites

    def test_tank_collision(self, projectile, tank):
        if tank.playerID == projectile.ownerID:
            return False
        else:
            laser_x_length = (self.heading_vector[0] * self.deadly_laser_length)
            laser_y_length = (self.heading_vector[1] * self.deadly_laser_length)
            return tank.test_rect_edge_against_real_bounds(self.position,
                                                           [int(self.position[0] + laser_x_length),
                                                            int(self.position[1] + laser_y_length)])

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)
