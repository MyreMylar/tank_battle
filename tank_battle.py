import math
import pygame
from pygame.locals import *
from game.explosion import Explosion
from game.mazegen import create_maze
from player import Player, PlayerScore, Scheme, RespawnPlayer
from pick_up import PickUpSpawner


class ScreenData:
    def __init__(self, screen_size):
        self.screenSize = screen_size


# -----------------------------------------------------------
# This is a simple 'class' that holds all our explosion data
# and has some helpful functions to use on it.
#
# We use this class in Challenge 2.
#
# SCROLL DOWN FURTHER FOR CHALLENGE 1
# -----------------------------------------------------------
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

    # ------------------------------------------------------------------------------
    # Here is where we create the explosion_data object variable used in Challenge 2
    # ------------------------------------------------------------------------------
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

    # player_2_id = "Player 2"
    # player_2_score = PlayerScore(player_2_id, (645, 300))
    # score_board.append(player_2_score)

    # --------------------------------------------------------------------------------------------
    # CHALLENGE 1
    # -------------
    # Create and add a second player to the game. (GUIDELINE IS 8 LINES OF CODE)
    #
    # Hints:
    # - Use 'start_location_2' and uncomment the ID and score variables defined above for player 2.
    #
    # - Create a new 'player_2_control_scheme' based on the player 1 version below.
    #   The list of all pygame control key codes is at the bottom of this file.
    #
    # - Pick a tank sprite image (there are two other colours of tank included in the game folder)
    #
    # - Remember to append the new player to the players list.
    #
    # - To make the new player spawn when you restart the game after a player wins, copy and paste
    #   the two lines of code that create and add the player to the list and paste them at
    #   around line 221 when we reset the game.
    # ---------------------------------------------
    # CHALLENGE 2 - PART 1 IS JUST BELOW THIS ONE
    # ---------------------------------------------------------------------------------------------
    player_1_control_scheme = Scheme()
    player_1_control_scheme.forward = K_w
    player_1_control_scheme.backward = K_s
    player_1_control_scheme.left = K_a
    player_1_control_scheme.right = K_d
    player_1_control_scheme.fire = K_LSHIFT

    player_1 = Player(explosion_data, start_location_1, player_1_control_scheme,
                      'green_tank.png', player_1_id, player_1_score)
    players.append(player_1)

    # Add second player here, see also line 219
    # ------------------------

    # bullets
    projectiles = []
    players_to_respawn = []

    clock = pygame.time.Clock()
    running = True
    restart_game = False
    end_game = False
    end_game_string = ""

    # ----------------------------------------------------------------------------------
    # CHALLENGE 2 - PART 1
    # ---------------------
    #
    # Add a couple of class function calls to update and draw explosion graphics. (GUIDELINE IS 2 LINES OF CODE)
    #
    # Tips:
    #
    # - We will need to use the 'explosion_data' object variable already created from the
    #   ExplosionData class visible at the top of this file. Remember you can call a class function
    #   by using a . after the objects variable name. In this case: explosion_data.
    #
    # - We must update() the explosion_data every frame, or main loop, of the game.
    #   This is so that explosions can animate over time. Find a place in the code below to do this.
    #   HINT: there will be a few other things updating at this point as well.
    #
    # - We must also draw() the explosions every frame, at the right time.
    #   Graphics are drawn, like plates in a stack, in the order in which we call their draw() functions.
    #   For our explosions we want to draw them *after* all the other game graphics (e.g. tanks, bullets, maze walls),
    #   but before the game text, which should be drawn last.
    #
    # - The ExplosionData class has simple functions you can use to update and draw the explosions.
    #   Make sure to check which variables you need to pass in to the functions.
    #
    # -------------------------------------------------------
    # CHALLENGE 2 - PART 2 IS IN THE 'player' PYTHON FILE.
    # ---------------------------------------------------------------------------------------------

    # -------------------------------
    # The main game loop starts here
    # -------------------------------
    while running:
        frame_time = clock.tick()
        time_delta = frame_time / 1000.0
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
                              'green_tank.png', player_1_id, player_1_score)
            players.append(player_1)

            # Add second player again here
            # ------------------------

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

            # all_sprites.update()

        # -----------------------------------------
        # Start drawing the graphics to the screen
        # ------------------------------------------

        screen.blit(background, (0, 0))  # draw the background

        for wall in maze_walls:  # draw the maze
            wall.draw(screen)

        all_pick_up_sprites.draw(screen)  # draw the pickups
        all_sprites.draw(screen)  # draw the players and projectiles

        # ---------------------------
        # Text drawing starts here
        # ---------------------------

        if end_game:
            end_game_text_render = large_font.render(end_game_string + " wins!", True, pygame.Color("#000000"))
            end_game_text_render_rect = end_game_text_render.get_rect(centerx=screen_data.screenSize[0] / 2,
                                                                      centery=screen_data.screenSize[1] / 2)
            text_background = pygame.Surface((end_game_text_render_rect.width, end_game_text_render_rect.height))
            text_background.fill(pygame.Color("#FFFFFF"))
            screen.blit(text_background, end_game_text_render_rect)
            screen.blit(end_game_text_render, end_game_text_render_rect)

            restart_game_text_render = font.render("Press Y to restart", True, pygame.Color("#000000"))
            restart_game_text_render_rect = restart_game_text_render.get_rect(centerx=(screen_data.screenSize[0] / 2),
                                                                              centery=(screen_data.screenSize[
                                                                                           1] / 2) + 40)
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

        #        if time_delta > 0.0:
        #            FPSString = "FPS: " + "{:.2f}".format(1.0/time_delta)
        #            FPSTextRender = font.render(FPSString, True, pygame.Color(0, 0, 0))
        #            screen.blit(FPSTextRender, FPSTextRender.get_rect(centerx=screen_data.screenSize[0]*0.9,
        #  centery=screen_data.screenSize[1]-(screen_data.screenSize[1]*0.95)))

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

# -----------------------------------------------
# Pygame key codes
# ---------------------
#
# KeyASCII      ASCII   Common Name
# K_BACKSPACE   \b      backspace
# K_TAB         \t      tab
# K_CLEAR               clear
# K_RETURN      \r      return
# K_PAUSE               pause
# K_ESCAPE      ^[      escape
# K_SPACE               space
# K_EXCLAIM     !       exclaim
# K_QUOTEDBL    "       quotedbl
# K_HASH        #       hash
# K_DOLLAR      $       dollar
# K_AMPERSAND   &       ampersand
# K_QUOTE               quote
# K_LEFTPAREN   (       left parenthesis
# K_RIGHTPAREN  )       right parenthesis
# K_ASTERISK    *       asterisk
# K_PLUS        +       plus sign
# K_COMMA       ,       comma
# K_MINUS       -       minus sign
# K_PERIOD      .       period
# K_SLASH       /       forward slash
# K_0           0       0
# K_1           1       1
# K_2           2       2
# K_3           3       3
# K_4           4       4
# K_5           5       5
# K_6           6       6
# K_7           7       7
# K_8           8       8
# K_9           9       9
# K_COLON       :       colon
# K_SEMICOLON   ;       semicolon
# K_LESS        <       less-than sign
# K_EQUALS      =       equals sign
# K_GREATER     >       greater-than sign
# K_QUESTION    ?       question mark
# K_AT          @       at
# K_LEFTBRACKET [       left bracket
# K_BACKSLASH   \       backslash
# K_RIGHTBRACKET ]      right bracket
# K_CARET       ^       caret
# K_UNDERSCORE  _       underscore
# K_BACKQUOTE   `       grave
# K_a           a       a
# K_b           b       b
# K_c           c       c
# K_d           d       d
# K_e           e       e
# K_f           f       f
# K_g           g       g
# K_h           h       h
# K_i           i       i
# K_j           j       j
# K_k           k       k
# K_l           l       l
# K_m           m       m
# K_n           n       n
# K_o           o       o
# K_p           p       p
# K_q           q       q
# K_r           r       r
# K_s           s       s
# K_t           t       t
# K_u           u       u
# K_v           v       v
# K_w           w       w
# K_x           x       x
# K_y           y       y
# K_z           z       z
# K_DELETE              delete
# K_KP0                 keypad 0
# K_KP1                 keypad 1
# K_KP2                 keypad 2
# K_KP3                 keypad 3
# K_KP4                 keypad 4
# K_KP5                 keypad 5
# K_KP6                 keypad 6
# K_KP7                 keypad 7
# K_KP8                 keypad 8
# K_KP9                 keypad 9
# K_KP_PERIOD   .       keypad period
# K_KP_DIVIDE   /       keypad divide
# K_KP_MULTIPLY *       keypad multiply
# K_KP_MINUS    -       keypad minus
# K_KP_PLUS     +       keypad plus
# K_KP_ENTER    \r      keypad enter
# K_KP_EQUALS   =       keypad equals
# K_UP                  up arrow
# K_DOWN                down arrow
# K_RIGHT               right arrow
# K_LEFT                left arrow
# K_INSERT              insert
# K_HOME                home
# K_END                 end
# K_PAGEUP              page up
# K_PAGEDOWN            page down
# K_F1                  F1
# K_F2                  F2
# K_F3                  F3
# K_F4                  F4
# K_F5                  F5
# K_F6                  F6
# K_F7                  F7
# K_F8                  F8
# K_F9                  F9
# K_F10                 F10
# K_F11                 F11
# K_F12                 F12
# K_F13                 F13
# K_F14                 F14
# K_F15                 F15
# K_NUMLOCK             numlock
# K_CAPSLOCK            capslock
# K_SCROLLOCK           scrollock
# K_RSHIFT              right shift
# K_LSHIFT              left shift
# K_RCTRL               right ctrl
# K_LCTRL               left ctrl
# K_RALT                right alt
# K_LALT                left alt
# K_RMETA               right meta
# K_LMETA               left meta
# K_LSUPER              left windows key
# K_RSUPER              right windows key
# K_MODE                mode shift
# K_HELP                help
# K_PRINT               print screen
# K_SYSREQ              sysrq
# K_BREAK               break
# K_MENU                menu
# K_POWER               power
# K_EURO                euro
#
# ----------------------------------------------------
