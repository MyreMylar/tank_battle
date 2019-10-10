import random
import pygame


class Explosion(pygame.sprite.Sprite):
    def __init__(self, start_pos, size, explosion_sheet, all_explosion_sprites, *groups):

        super().__init__(*groups)
        self.all_explosion_sprites = all_explosion_sprites
        self.radius = size
        self.collide_radius = self.radius
        self.explosion_sheet = explosion_sheet
        self.explosion_frames = 16
        self.explosion_images = []
        random_explosion_int = random.randrange(0, 512, 64)
        for i in range(0, self.explosion_frames):
            x_start_index = (i * 64)
            explosion_frame = self.explosion_sheet.subsurface(pygame.Rect(x_start_index + 1,
                                                                          random_explosion_int + 1, 62, 62))
            explosion_frame = pygame.transform.scale(explosion_frame,
                                                     (self.radius*2, self.radius*2))
            self.explosion_images.append(explosion_frame)

        self.image = self.explosion_images[0]
        self.rect = self.explosion_images[0].get_rect()
        self.rect.center = start_pos

        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]
                
        self.should_die = False
        self.life_time = 0.45
        self.time = self.life_time
        self.frame_time = self.life_time / self.explosion_frames
        self.frame = 1

        self.all_explosion_sprites.add(self)
        
    def update_sprite(self, time_delta):
               
        self.time -= time_delta
        if self.time < 0.0:
            self.should_die = True
            self.all_explosion_sprites.remove(self)

        if self.frame < self.explosion_frames and (self.life_time - self.time) > (self.frame_time * self.frame):
            self.image = self.explosion_images[self.frame]
            self.frame += 1

    def update_movement_and_collision(self):
        pass
