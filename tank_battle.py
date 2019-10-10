import math
import pygame
from pygame.locals import *
from game.explosion import Explosion
from game.mazegen import create_maze
from game.player import Player, PlayerScore, Scheme, RespawnPlayer
from game.pick_up import PickUpSpawner


class ScreenData:
    def __init__(self, screen_size):
        self.screenSize = screen_size


class ExplosionData:
    def __init__(self):
        self.explosions_sprite_sheet = pygame.image.load("images/explosions.png").convert_alpha()
        self.explosions = []
        self.all_explosion_sprites = pygame.sprite.Group()

    def update(self, time_delta):
        for explosion in self.explosions:
            explosion.update_sprite(time_delta)
        self.explosions[:] = [explosion for explosion in self.explosions if not explosion.should_die]

    def draw(self, screen):
        self.all_explosion_sprites.draw(screen)

    def create_explosion(self, position, size=32):
        self.explosions.append(Explosion(position, size, self.explosions_sprite_sheet, self.all_explosion_sprites))
                
        
def main():

    # create empty pygame window with white background
    pygame.init()
    screen_data = ScreenData([800, 600])
    pygame.display.set_caption('Tank Battle')
    screen = pygame.display.set_mode((800, 600))
    background = pygame.Surface(screen.get_size())
    background = background.convert(screen)
    background.fill((255, 255, 255))
    all_sprites = pygame.sprite.OrderedUpdates()
    all_pick_up_sprites = pygame.sprite.Group()
    font = pygame.font.Font(None, 20)
    large_font = pygame.font.Font(None, 64)
    bold_font = pygame.font.Font(None, 24)
    bold_font.set_underline(True)
    bold_font.set_bold(True)

    explosion_data = ExplosionData()

    # generate a maze
    maze_data = create_maze(20, 20)
    maze_walls = maze_data[0]
    walkable_zones = maze_data[2]

    pick_ups = []

    pick_up_spawner = PickUpSpawner(pick_ups, all_pick_up_sprites, walkable_zones)
    
    # players
    players = []
    start_locations = []
    start_location_1 = (137, 62)
    start_location_2 = (587, 512)
    start_location_3 = (137, 512)
    start_location_4 = (587, 62)

    start_locations.append(start_location_1)
    start_locations.append(start_location_2)
    start_locations.append(start_location_3)
    start_locations.append(start_location_4)

    score_board = []
    
    player_1_id = "Player 1"
    player_1_score = PlayerScore(player_1_id, (645, 100))
    score_board.append(player_1_score)
    
    player_2_id = "Player 2"
    player_2_score = PlayerScore(player_2_id, (645, 300))
    score_board.append(player_2_score)

    player_1_control_scheme = Scheme()
    player_1_control_scheme.forward = K_w
    player_1_control_scheme.backward = K_s
    player_1_control_scheme.left = K_a
    player_1_control_scheme.right = K_d
    player_1_control_scheme.fire = K_LCTRL

    player_2_control_scheme = Scheme()
    player_2_control_scheme.forward = K_UP
    player_2_control_scheme.backward = K_DOWN
    player_2_control_scheme.left = K_LEFT
    player_2_control_scheme.right = K_RIGHT
    player_2_control_scheme.fire = K_RCTRL

    player_1 = Player(explosion_data, start_location_1, player_1_control_scheme,
                      'green_tank.png', player_1_id, player_1_score)
    players.append(player_1)

    player_2 = Player(explosion_data, start_location_2, player_2_control_scheme,
                      'red_tank.png', player_2_id, player_2_score)
    players.append(player_2)

    # bullets
    projectiles = []
    players_to_respawn = []
    
    clock = pygame.time.Clock()
    running = True
    restart_game = False
    end_game = False
    end_game_string = ""

    # -------------------------------
    # The main game loop starts here
    # -------------------------------
    while running:
        frame_time = clock.tick()
        time_delta = frame_time/1000.0
        # handle UI and inout events
        for event in pygame.event.get():

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for wall in maze_walls:
                        if wall.is_point_inside(pygame.mouse.get_pos()):
                            print("Start Index: " + str(wall.startIndex) + ", " + "End Index: " + str(wall.endIndex))
            if event.type == QUIT:
                running = False

            if end_game:
                if event.type == KEYDOWN:
                    if event.key == K_y:
                        restart_game = True
                    if event.key == K_ESCAPE:
                        running = False                 
                        
            else:
                for player in players:
                    player.process_event(event)

        if restart_game:
            restart_game = False
            end_game = False
            end_game_string = ""

            players[:] = []
            pick_ups[:] = []
            projectiles[:] = []
            players_to_respawn[:] = []
            all_pick_up_sprites.empty()

            maze_data = create_maze(20, 20)
            maze_walls = maze_data[0]
            walkable_zones = maze_data[2]

            pick_up_spawner = PickUpSpawner(pick_ups, all_pick_up_sprites, walkable_zones)

            for score in score_board:
                score.reset_score()

            player_1 = Player(explosion_data, start_location_1, player_1_control_scheme,
                              'images/green_tank.png', player_1_id, player_1_score)
            players.append(player_1)

            player_2 = Player(explosion_data, start_location_2, player_2_control_scheme,
                              'images/red_tank.png', player_2_id, player_2_score)
            players.append(player_2)

        # ---------------------------------------------------------------------
        # Start updating the game objects (for movement and collision largely)
        # ---------------------------------------------------------------------
        if end_game:
            pass
        else:
            for score in score_board:
                if score == 5:
                    end_game = True
                    end_game_string = score.player_id

            pick_up_spawner.update(time_delta)

            # handle respawning players after dying
            for respawning_player in players_to_respawn:
                if respawning_player.time_to_spawn:
                    furthest_spawn = find_furthest_start_location_from_other_players(players, start_locations)
                    player = Player(explosion_data, furthest_spawn, respawning_player.control_scheme,
                                    respawning_player.image, respawning_player.player_id, respawning_player.score)
                    players.append(player)
                    respawning_player.has_respawned = True
                else:
                    respawning_player.update(frame_time)
            players_to_respawn[:] = [r for r in players_to_respawn if not r.has_respawned]
            
            all_sprites.empty()

            for pick_up in pick_ups:
                pick_up.update_movement_and_collision(players)
            pick_ups[:] = [pick_up for pick_up in pick_ups if not pick_up.should_die]
            
            # update players and bullets
            for player in players:
                player.update_movement_and_collision(time_delta, maze_walls, projectiles, score_board)
                all_sprites = player.update_sprite(all_sprites)
                if player.should_die:
                    players_to_respawn.append(RespawnPlayer(player))
            players[:] = [player for player in players if not player.should_die]

            for projectile in projectiles:
                all_sprites = projectile.update(time_delta, all_sprites, maze_walls, players)
            projectiles[:] = [projectile for projectile in projectiles if not projectile.should_die]

            explosion_data.update(time_delta)

        # -----------------------------------------
        # Start drawing the graphics to the screen
        # ------------------------------------------
        
        screen.blit(background, (0, 0))  # draw the background
        
        for wall in maze_walls:  # draw the maze
            wall.draw(screen)
      
        all_pick_up_sprites.draw(screen)  # draw the pickups
        all_sprites.draw(screen)  # draw the players and projectiles

        explosion_data.draw(screen)

        # ---------------------------
        # Text drawing starts here
        # ---------------------------

        if end_game:
            end_game_text_render = large_font.render(end_game_string + " wins!", True, pygame.Color("#000000"))
            end_game_text_render_rect = end_game_text_render.get_rect(centerx=screen_data.screenSize[0]/2,
                                                                      centery=screen_data.screenSize[1]/2)
            text_background = pygame.Surface((end_game_text_render_rect.width, end_game_text_render_rect.height))
            text_background.fill(pygame.Color("#FFFFFF"))
            screen.blit(text_background, end_game_text_render_rect)
            screen.blit(end_game_text_render, end_game_text_render_rect)
            
            restart_game_text_render = font.render("Press Y to restart", True, pygame.Color("#000000"))
            restart_game_text_render_rect = restart_game_text_render.get_rect(centerx=(screen_data.screenSize[0]/2),
                                                                              centery=(screen_data.screenSize[1]/2)+40)
            text_background2 = pygame.Surface((restart_game_text_render_rect.width,
                                               restart_game_text_render_rect.height))
            text_background2.fill(pygame.Color("#FFFFFF"))
            screen.blit(text_background2, restart_game_text_render_rect)
            screen.blit(restart_game_text_render, restart_game_text_render_rect)

        for score in score_board:
            player_id_text_render = bold_font.render(score.player_id, True, pygame.Color("#000000"))
            player_id_text_render_rect = player_id_text_render.get_rect(x=score.screen_position[0],
                                                                        centery=score.screen_position[1])
            screen.blit(player_id_text_render, player_id_text_render_rect)

            power_up_text_render = font.render("Special: " + score.active_power_up, True, pygame.Color("#000000"))
            power_up_text_render_rect = power_up_text_render.get_rect(x=score.screen_position[0],
                                                                      centery=score.screen_position[1] + 26)
            screen.blit(power_up_text_render, power_up_text_render_rect)
            
            score_text_render = font.render("Score: " + str(score.score), True, pygame.Color("#000000"))
            score_text_render_rect = score_text_render.get_rect(x=score.screen_position[0],
                                                                centery=score.screen_position[1] + 48)
            screen.blit(score_text_render, score_text_render_rect)

        pygame.display.flip()  # flip all our drawn stuff onto the screen

    pygame.quit()  # exited game loop so quit pygame


def find_furthest_start_location_from_other_players(players, start_locations):
    furthest_location = start_locations[0]
    longest_distance = 0
    for loc in start_locations:
        shortest_distance = 100000
        for player in players:
            distance_squared = ((player.position[0] - loc[0]) ** 2) + ((player.position[1] - loc[1]) ** 2)
            distance = math.sqrt(distance_squared)
            if distance < shortest_distance:
                shortest_distance = distance
        if shortest_distance > longest_distance:
            longest_distance = shortest_distance
            furthest_location = loc

    return furthest_location


if __name__ == '__main__':
    main()
