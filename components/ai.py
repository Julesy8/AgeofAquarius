import tcod as libtcod


class Melee:
    def take_turn(self, target, fov_map, game_map, entities):
        monster = self.owner
        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(target) >= 2:
                monster.move_astar(target, entities, game_map)

            elif target.fighter.alive:
                print('Melee attack by {0}!'.format(monster.name))
