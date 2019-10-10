import math
import pygame

from game.base_projectile import BaseProjectile
from game.cluster_shard import ClusterShard


class ClusterBomb(BaseProjectile):
    def __init__(self, initial_heading_vector, start_position, owner_id, *groups):

        # we want to start projectiles a little in front of the tank so they don't
        # immediately overlap with the tank that fires them and blow it up
        super().__init__(*groups)
        safe_start_position = [start_position[0], start_position[1]]
        safe_start_position[0] += initial_heading_vector[0] * 10.0
        safe_start_position[1] += initial_heading_vector[1] * 10.0
        
        self.heading_vector = [initial_heading_vector[0], initial_heading_vector[1]]
        heading_vector_len = math.sqrt((self.heading_vector[0] ** 2) + (self.heading_vector[1] ** 2))
        self.heading_vector = [self.heading_vector[0] / heading_vector_len, self.heading_vector[1] / heading_vector_len]
         
        self.bullet_position = safe_start_position
        self.owner_id = owner_id

        self.image = pygame.image.load('images/cluster_bomb.png').convert()
        self.rect = self.image.get_rect()

        self.bullet_speed = 200.0

        self.bullet_life_time = 4.0
        self.should_die = False
        self.bounces = 0

        self.collision_delta = 1.0

    def is_controlled(self):
        return True

    def fire_pressed(self, projectiles):
        self.should_die = True

        heading_angle = math.atan2(self.heading_vector[0], self.heading_vector[1]) * 180 / math.pi

        angle1 = heading_angle + 40.0
        angle2 = heading_angle + 80.0
        angle3 = heading_angle + 120.0
        angle4 = heading_angle + 160.0
        angle5 = heading_angle + 200.0
        angle6 = heading_angle + 240.0
        angle7 = heading_angle + 280.0
        angle8 = heading_angle + 320.0
        angle9 = heading_angle + 360.0

        shard1 = ClusterShard(self.normalise_2d_vec([math.cos(math.radians(angle1)), math.sin(math.radians(angle1))]),
                              self.bullet_position, self.owner_id)
        projectiles.append(shard1)
        shard2 = ClusterShard(self.normalise_2d_vec([math.cos(math.radians(angle2)), math.sin(math.radians(angle2))]),
                              self.bullet_position, self.owner_id)
        projectiles.append(shard2)
        shard3 = ClusterShard(self.normalise_2d_vec([math.cos(math.radians(angle3)), math.sin(math.radians(angle3))]),
                              self.bullet_position, self.owner_id)
        projectiles.append(shard3)
        shard4 = ClusterShard(self.normalise_2d_vec([math.cos(math.radians(angle4)), math.sin(math.radians(angle4))]),
                              self.bullet_position, self.owner_id)
        projectiles.append(shard4)
        shard5 = ClusterShard(self.normalise_2d_vec([math.cos(math.radians(angle5)), math.sin(math.radians(angle5))]),
                              self.bullet_position, self.owner_id)
        projectiles.append(shard5)
        shard6 = ClusterShard(self.normalise_2d_vec([math.cos(math.radians(angle6)), math.sin(math.radians(angle6))]),
                              self.bullet_position, self.owner_id)
        projectiles.append(shard6)
        shard7 = ClusterShard(self.normalise_2d_vec([math.cos(math.radians(angle7)), math.sin(math.radians(angle7))]),
                              self.bullet_position, self.owner_id)
        projectiles.append(shard7)
        shard8 = ClusterShard(self.normalise_2d_vec([math.cos(math.radians(angle8)), math.sin(math.radians(angle8))]),
                              self.bullet_position, self.owner_id)
        projectiles.append(shard8)
        shard9 = ClusterShard(self.normalise_2d_vec([math.cos(math.radians(angle9)), math.sin(math.radians(angle9))]),
                              self.bullet_position, self.owner_id)
        projectiles.append(shard9)
        
        return None

    @staticmethod
    def normalise_2d_vec(vec):
        vec_len = math.sqrt(vec[0] * vec[0] + vec[1] * vec[1])
        if vec_len == 0.0:
            vec_len = 1.0
        return [vec[0]/vec_len, vec[1]/vec_len]

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

            # to calculate our collision surface normal we look at all the points of collision,
            # imagine they are smoothed out into a flat surface
            # and then grab the tangent angle of that surface. We then pick our final normal out
            #  of all our collided surfaces by comparing the dot product
            # of our 'tangent' vector and each of the surfaces' vectors. Not sure if this is a good
            #  approach or a terrible one, but it's what I'm using.
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

        self.bullet_position[0] += (self.heading_vector[0] * self.bullet_speed * time_delta)
        self.bullet_position[1] += (self.heading_vector[1] * self.bullet_speed * time_delta)
        self.rect.center = (int(self.bullet_position[0]), int(self.bullet_position[1]))
        all_sprites.add(self)

        self.bullet_life_time -= time_delta
        if self.bullet_life_time < 0.0:
            self.should_die = True

            for player in players:
                if player.controlled_projectile == self:
                    player.deactivate_controlled_projectile()
        return all_sprites
