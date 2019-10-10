import pygame
import random


# --------------------------------------
# SCROLL DOWN FOR CHALLENGE 3 - PART 1
# --------------------------------------
class PickUpSpawner:
    def __init__(self, pick_ups, all_pick_up_sprites, walkable_zones):
        self.pick_ups = pick_ups
        self.all_pick_up_sprites = all_pick_up_sprites

        self.pickup_image_sheet = self.load_tile_table("images/power_ups.png", 16, 16, True)

        self.pickup_images = {'cluster_bomb': self.pickup_image_sheet[0][0],
                              'remote_missile': self.pickup_image_sheet[5][0],
                              'laser': self.pickup_image_sheet[6][0]}

        self.walkable_zones = walkable_zones

        self.pickup_spawn_time = random.uniform(5.0, 25.0)
        self.pickup_acc = 0.0

    def update(self, time_delta):

        self.pickup_acc += time_delta

        if self.pickup_acc >= self.pickup_spawn_time:
            self.pickup_spawn_time = random.uniform(5.0, 25.0)
            self.pickup_acc = 0.0

            if len(self.pick_ups) < 4:
                found_good_spot = False
                random_pick_up_spot = random.choice(self.walkable_zones)
                while not found_good_spot:
                    random_pick_up_spot = random.choice(self.walkable_zones)
                    found_bad_spot = False
                    for pick_up in self.pick_ups:
                        if (random_pick_up_spot.screen_x_pos == pick_up.position[0]) and\
                                (random_pick_up_spot.screen_y_pos == pick_up.position[1]):
                            found_bad_spot = True
                    if not found_bad_spot:
                        found_good_spot = True

                self.try_spawn([random_pick_up_spot.screen_x_pos, random_pick_up_spot.screen_y_pos])

    # -----------------------------------------------------------------------
    # CHALLENGE 3 - PART 1
    # ----------------------
    #
    # Add a 'laser' pickup to the try_spawn function below. (GUIDELINE IS 2 LINES OF CODE)
    #
    # Hints:
    #
    # - This function creates a randomly selected type of pick up at a given location in the maze.
    #
    # - Don't forget to adjust the randomRoll range so that your new laser pick up has
    #   a chance of appearing.
    #
    # ------------------------------------------------------------
    # CHALLENGE 3 - PART 2 IS FOUND IN THE 'player' PYTHON FILE.
    # -----------------------------------------------------------------------
    def try_spawn(self, spawn_position):
        random_roll = random.randint(0, 1)
        if random_roll == 0:
            self.pick_ups.append(PickUp(spawn_position, self.pickup_images["cluster_bomb"],
                                        "cluster_bomb", self.all_pick_up_sprites))
        elif random_roll == 1:
            self.pick_ups.append(PickUp(spawn_position, self.pickup_images["remote_missile"],
                                        "remote_missile", self.all_pick_up_sprites))

    @staticmethod
    def load_tile_table(filename, width, height, use_transparency):
        if use_transparency:
            image = pygame.image.load(filename).convert_alpha()
        else:
            image = pygame.image.load(filename).convert()
        image_width, image_height = image.get_size()
        tile_table = []
        for tile_x in range(0, int(image_width/width)):
            line = []
            tile_table.append(line)
            for tile_y in range(0, int(image_height/height)):
                rect = (tile_x*width, tile_y*height, width, height)
                line.append(image.subsurface(rect))
        return tile_table


class PickUp(pygame.sprite.Sprite):
    def __init__(self, start_pos, image, type_name, all_pick_up_sprites, *groups):
        super().__init__(*groups)
        self.world_position = [start_pos[0], start_pos[1]]
        self.type_name = type_name
        self.screen_name = "None"
        if type_name.find('_') != -1:
            self.screen_name = type_name.split('_')[0].title() + " " + type_name.split('_')[1].title()
        else:
            self.screen_name = type_name.title()
        self.image = image
        self.image = self.image
        self.rect = self.image.get_rect()
        self.rect.center = start_pos

        self.position = [float(self.rect.center[0]), float(self.rect.center[1])]

        self.all_pick_up_sprites = all_pick_up_sprites
        self.all_pick_up_sprites.add(self)
        self.should_die = False

    def update_movement_and_collision(self, players):
        for player in players:
            if not player.have_active_power_up:
                if player.test_pick_up_collision(self.rect):
                    self.should_die = True
                    player.activate_power_up(self.type_name, self.screen_name)
                    self.all_pick_up_sprites.remove(self)
