import random
import matplotlib.pyplot as plt 
import matplotlib.colors as colors

plt.style.use("seaborn-paper")

# Value mapping
terrain_sand = 0
terrain_hole_core = 0.1
terrain_hole_side = 0.15
terrain_swamp = 0.2
terrain_nest_bc = 0.3
terrain_nest_sc = 0.4
terrain_nest_swamp_sc = 0.5
terrain_nest_starved_bc = 0.6

# Welcome-to-tweak variables
sinkhole_density = 400  # increases sinkhole spawn chance. choose from 0 - 1000
sinkhole_min_dist = 14  # minimum distance between sinkholes
swamp_density = 650  # increases swamp spawn chance. choose from 0 - 1000
swamp_avg_size = 5  # average buildsize for swampspawns
sc_nest_density = 8  # increases scnest spawn chance. choose from 0 - 10
sc_nest_max_hole_dist = 14  # max sc tile distance to sinkhole tiles
sc_nest_max_swamp_dist = 3  # max sc tile distance to swamp tiles

# Tweak-with-caution variables
sinkhole_avg_size = 7  # average sinkhole size
sinkhole_size_deviation = 2  # max deviation from average sinkhole size. Best set lower than sinkhole_avg_size
bc_nest_density = 8  # increases bcnest spawn chance. choose from 0 - 10
bc_nest_max_dist = 4  # max distance to a sinkhole tile
bc_check_radius = 16  # radius in which to check for sinkhole tiles
bc_load = 800  # weight of othe bc nest tiles
bc_max_nest_size = 2  # max branching of bc nests
sc_check_radius = 30  # radius in which to check for sinkhole tiles
bc_starve_range = 30  # radius in which to check for sc feeding support
sc_feed_multiplier = 4  # food capacity of sc nests


def generate_world(width=100, height=100):
    """Generates a 2d array of values that represent terrain types"""
    terrain_map = []
    # Fill the terrain array with 0's for sand to start
    for y in range(height):
        new_row = []
        for x in range(width):
            new_row.append(0.0)
        terrain_map.append(new_row)

    terrain_map = create_sinkholes(terrain_map)
    terrain_map = create_swamps(terrain_map)
    terrain_map = create_nests(terrain_map)
    terrain_map = starve_nests(terrain_map)

    return terrain_map


def generate_image(noise_map):
    cmap = colors.ListedColormap(
        [
            "lavender",
            "slateblue",
            "slateblue",
            "olivedrab",
            "red",
            "darkturquoise",
            "orange",
            "maroon",
        ]
    )

    bounds = [
        0,
        terrain_hole_core,
        terrain_hole_side,
        terrain_swamp,
        terrain_nest_bc,
        terrain_nest_sc,
        terrain_nest_swamp_sc,
        terrain_nest_starved_bc,
        0.7,
    ]
    norm = colors.BoundaryNorm(bounds, cmap.N)
    plt.rcParams["figure.figsize"] = (20, 10)
    img = plt.imshow(noise_map, cmap=cmap, norm=norm)
    # img = plt.imshow(noise_map)

    plt.axis("off")
    plt.savefig("world.png", bbox_inches="tight")


def create_sinkholes(terrain_map):
    """Sinkholes are defined by a core tile, all of which are first placed, and then 'periphery' or 'side' tiles are constructed each"""
    height = len(terrain_map)
    width = len(terrain_map[0])

    # place the first core in a random position
    random_spot_x = random.randint(0, width - 1)
    random_spot_y = random.randint(0, height - 1)
    terrain_map[random_spot_y][random_spot_x] = terrain_hole_core

    # check each tile for potential placement of more cores
    for y in range(height):
        for x in range(width):
            if (
                sinkhole_adjacent(terrain_map, x, y) == False
            ):  # no sinkholes directly adjacent to this spot. This might just be obsolete due to distance check 3 lines below
                z = random.randint(
                    0, (1000 - sinkhole_density)
                )  # random chacnce at spawning core tiles
                if z == 0:
                    if (
                        distance_to_closest_sinkhole(terrain_map, x, y)
                        > sinkhole_min_dist + sinkhole_avg_size
                    ):  # it's far away enough from other sinkholes
                        terrain_map[y][x] = terrain_hole_core  # place core

    # build peripheries
    pointy_offset = 0
    for y in range(height):
        for x in range(width):
            if terrain_map[y][x] == terrain_hole_core:  # A core tile is found.
                # Set some sizes
                sinkhole_size = random.randint(0, sinkhole_avg_size)
                sinkhole_min_arm_size = sinkhole_avg_size - 3
                deviation_amount_north = sinkhole_size - random.randint(
                    0, sinkhole_size_deviation
                )
                pointy_offset = random.randint(0, 1)
                if deviation_amount_north <= sinkhole_min_arm_size:
                    deviation_amount_north = sinkhole_min_arm_size
                # Draw a line of tiles outward, then draw towards it in steps to create a circle-like structure
                # Do this upwards
                for b in range(deviation_amount_north):
                    if (y - b >= 0) & (y + b <= height - 1) & (b != 0):
                        terrain_map[y - b][x] = terrain_hole_side
                        for c in range(deviation_amount_north - b + pointy_offset):
                            if x + c <= width - 1:
                                terrain_map[y - b][x + c] = terrain_hole_side
                        for c in range(deviation_amount_north - b + pointy_offset):
                            if x - c >= 0:
                                terrain_map[y - b][x - c] = terrain_hole_side
                deviation_amount_south = sinkhole_size - random.randint(
                    0, (sinkhole_size_deviation)
                )
                if deviation_amount_south <= sinkhole_min_arm_size:
                    deviation_amount_south = sinkhole_min_arm_size
                # Downwards
                for b in range(deviation_amount_south):
                    if (y - b >= 0) & (y + b <= height - 1) & (b != 0):
                        terrain_map[y + b][x] = terrain_hole_side
                        for c in range(deviation_amount_south - b + pointy_offset):
                            if x + c <= width - 1:
                                terrain_map[y + b][x + c] = terrain_hole_side
                        for c in range(deviation_amount_south - b + pointy_offset):
                            if x - c >= 0:
                                terrain_map[y + b][x - c] = terrain_hole_side
                deviation_amount_east = sinkhole_size - random.randint(
                    0, (sinkhole_size_deviation)
                )
                if deviation_amount_east <= sinkhole_min_arm_size:
                    deviation_amount_east = sinkhole_min_arm_size
                # Rightwards
                for a in range(deviation_amount_east):
                    if (x - a >= 0) & (x + a <= width - 1) & (a != 0):
                        terrain_map[y][x - a] = terrain_hole_side
                        for c in range(deviation_amount_east - a + pointy_offset):
                            if y + c <= height - 1:
                                terrain_map[y + c][x - a] = terrain_hole_side
                        for c in range(deviation_amount_east - a + pointy_offset):
                            if y - c >= 0:
                                terrain_map[y - c][x - a] = terrain_hole_side
                deviation_amount_west = sinkhole_size - random.randint(
                    0, (sinkhole_size_deviation)
                )
                if deviation_amount_west <= sinkhole_min_arm_size:
                    deviation_amount_west = sinkhole_min_arm_size
                # Leftwards
                for a in range(deviation_amount_west):
                    if (x - a >= 0) & (x + a <= width - 1) & (a != 0):
                        terrain_map[y][x + a] = terrain_hole_side
                        for c in range(deviation_amount_west - a + pointy_offset):
                            if (y + c <= height - 1) & (x + a <= width - 1):
                                terrain_map[y + c][x + a] = terrain_hole_side
                        for c in range(deviation_amount_west - a + pointy_offset):
                            if (y - c >= 0) & (x + a <= width - 1):
                                terrain_map[y - c][x + a] = terrain_hole_side

    return terrain_map


def create_swamps(terrain_map):
    """Choose random locations at random, then create a spiraling noisy shape"""
    height = len(terrain_map)
    width = len(terrain_map[0])

    for y in range(height):
        for x in range(width):
            if terrain_map[y][x] == 0:
                z = random.randint(0, (1000 - swamp_density))
                if z == 2:
                    if sinkhole_adjacent(terrain_map, x, y) == False:
                        create_swamp(terrain_map, x, y)

    return terrain_map


def create_swamp(terrain_map, x, y):
    """Create a random shape through a spiraling for-loop, with a bonus for distance from sinkholes"""
    height = len(terrain_map)
    width = len(terrain_map[0])
    min_size = 1
    max_size = 2
    min_arm = 1
    max_arm = 3
    dist_bonus = 1
    total_size = height + width
    # The growth of swamps is inhibited by the spillover of sinkhole vapor, so they get an avg size bonus based on distance to closest sinkhole
    min_dist = distance_to_closest_sinkhole(terrain_map, x, y)
    if (total_size / min_dist) < 5:
        dist_bonus = 12
    elif (total_size / min_dist) < 8:
        dist_bonus = 8
    elif (total_size / min_dist) < 12:
        dist_bonus = 5
    elif (total_size / min_dist) < 16:
        dist_bonus = 3
    if sinkhole_adjacent(terrain_map, x, y) == False:
        terrain_map[y][x] = terrain_swamp
    xNew = x
    yNew = y
    # In each of four directions, create lines of swamptiles of varying lengths
    for a in range(random.randint(min_size, (max_size * dist_bonus))):
        arm_length = random.randint(min_arm, max_arm)
        for b in range(arm_length):
            xNew += 1
            if (xNew >= 0) & (xNew <= width - 1) & (yNew > 0) & (yNew <= height - 1):
                if (terrain_map[yNew][xNew] == 0) & (
                    sinkhole_adjacent(terrain_map, xNew, yNew) == False
                ):
                    terrain_map[yNew][xNew] = terrain_swamp
        arm_length = random.randint(min_arm, max_arm)
        for b in range(arm_length):
            yNew -= 1
            if (xNew >= 0) & (xNew <= width - 1) & (yNew > 0) & (yNew <= height - 1):
                if (terrain_map[yNew][xNew] == 0) & (
                    sinkhole_adjacent(terrain_map, xNew, yNew) == False
                ):
                    terrain_map[yNew][xNew] = terrain_swamp
        arm_length = random.randint(min_arm, max_arm)
        for b in range(arm_length):
            xNew -= 1
            if (xNew >= 0) & (xNew <= width - 1) & (yNew > 0) & (yNew <= height - 1):
                if (terrain_map[yNew][xNew] == 0) & (
                    sinkhole_adjacent(terrain_map, xNew, yNew) == False
                ):
                    terrain_map[yNew][xNew] = terrain_swamp
            if random.randint(0, 1) == 1:
                xNew -= 1
        arm_length = random.randint(min_arm, max_arm)
        for b in range(arm_length):
            yNew += 1
            if (xNew >= 0) & (xNew <= width - 1) & (yNew > 0) & (yNew <= height - 1):
                if (terrain_map[yNew][xNew] == 0) & (
                    sinkhole_adjacent(terrain_map, xNew, yNew) == False
                ):
                    terrain_map[yNew][xNew] = terrain_swamp


def create_nests(terrain_map):
    """Create BC nests, then SC nests"""
    height = len(terrain_map)
    width = len(terrain_map[0])

    sc_nest_count = 0
    # BCnests spawn randomly, but at a max dist from sinkholes
    for y in range(height):
        for x in range(width):
            z = random.randint(0, (10 - bc_nest_density))
            if z == 1:
                if distance_to_closest_sinkhole(terrain_map, x, y) <= bc_nest_max_dist:
                    spawn_bc_nest(terrain_map, x, y)

    # SCnests spawn in or near swamps, need sinkholes within range for sustenance
    for y in range(height):
        for x in range(width):
            z = random.randint(0, (10 - sc_nest_density))
            if z == 1:
                if (
                    distance_to_closest_sinkhole(terrain_map, x, y)
                    <= sc_nest_max_hole_dist
                ):
                    if (
                        distance_to_closest_terrain_type(
                            terrain_map, x, y, terrain_swamp
                        )
                        <= sc_nest_max_swamp_dist
                    ):
                        sc_nest_count += 1
                        spawn_sc_nest(terrain_map, x, y)

    return terrain_map


def spawn_bc_nest(terrain_map, x, y):
    """Check how many sinkhole tiles and other BC nests are nearby for potential extra tiles, then spawn a nest"""
    height = len(terrain_map)
    width = len(terrain_map[0])
    # check in a XbyX radius for how many sinkhole tiles there are, and how many other BC tiles. Each BC nest takes bc_load sinkhole tiles.
    hole_tile_total = 0
    bc_tile_total = 0

    for a in range(bc_check_radius):
        # check upwards
        if y - a >= 0:
            if (terrain_map[y - a][x] == terrain_hole_core) | (
                terrain_map[y - a][x] == terrain_hole_side
            ):
                hole_tile_total += 1
            if terrain_map[y - a][x] == terrain_nest_bc:
                bc_tile_total += 1
        # check downwards
        if y + a <= height - 1:
            if (terrain_map[y + a][x] == terrain_hole_core) | (
                terrain_map[y + a][x] == terrain_hole_side
            ):
                hole_tile_total += 1
            if terrain_map[y + a][x] == terrain_nest_bc:
                bc_tile_total += 1
        # check rightward
        if x + a <= width - 1:
            if (terrain_map[y][x + a] == terrain_hole_core) | (
                terrain_map[y][x + a] == terrain_hole_side
            ):
                hole_tile_total += 1
            if terrain_map[y][x + a] == terrain_nest_bc:
                bc_tile_total += 1
        # check leftward
        if x - a >= 0:
            if (terrain_map[y][x - a] == terrain_hole_core) | (
                terrain_map[y][x - a] == terrain_hole_side
            ):
                hole_tile_total += 1
            if terrain_map[y][x - a] == terrain_nest_bc:
                bc_tile_total += 1
    surplus = hole_tile_total - (bc_tile_total * bc_load)

    # surplus gives a chance at extra nest tiles for each nest spawn, in a random direction
    if surplus > 0:
        if surplus > bc_max_nest_size:
            surplus = bc_max_nest_size
        for b in range(surplus):
            if random.randint(0, 10 - bc_nest_density) == 0:
                # create a tile. Arbitrarily check right, then down, then left, then up
                random_dir = random.randint(0, 3)
                if random_dir == 0:
                    if x + b <= width - 1:
                        if (terrain_map[y][x + b] == 0) & (
                            distance_to_closest_sinkhole(terrain_map, x + b, y)
                            < bc_nest_max_dist
                        ):
                            terrain_map[y][x + b] = terrain_nest_bc
                elif random_dir == 1:
                    if y + b <= height - 1:
                        if (terrain_map[y + b][x] == 0) & (
                            distance_to_closest_sinkhole(terrain_map, x, y + b)
                            < bc_nest_max_dist
                        ):
                            terrain_map[y + b][x] = terrain_nest_bc
                elif random_dir == 2:
                    if x - b >= 0:
                        if (terrain_map[y][x - b] == 0) & (
                            distance_to_closest_sinkhole(terrain_map, x - b, y)
                            < bc_nest_max_dist
                        ):
                            terrain_map[y][x - b] = terrain_nest_bc
                elif random_dir == 3:
                    if y - b >= 0:
                        if (terrain_map[y - b][x] == 0) & (
                            distance_to_closest_sinkhole(terrain_map, x, y - b)
                            < bc_nest_max_dist
                        ):
                            terrain_map[y - b][x] = terrain_nest_bc

    return terrain_map


def spawn_sc_nest(terrain_map, x, y):
    """Create SC nests where allowed"""
    height = len(terrain_map)
    width = len(terrain_map[0])
    count_exclude = 0
    hole_tile_total = 0
    bc_tile_total = 0

    # Only spawn on tiles that are closer to swamps than to BC nests
    if distance_to_closest_terrain_type(
        terrain_map, x, y, terrain_swamp
    ) < distance_to_closest_terrain_type(terrain_map, x, y, terrain_nest_bc):
        # Count the number of sinkhole tiles and BC tiles, and spawn only if there are more sinkhole tiles in the radius
        for a in range(sc_check_radius):
            # check upwards
            if y - a >= 0:
                if (terrain_map[y - a][x] == terrain_hole_core) | (
                    terrain_map[y - a][x] == terrain_hole_side
                ):
                    hole_tile_total += 1
                if terrain_map[y - a][x] == terrain_nest_bc:
                    bc_tile_total += 1
            # check downwards
            if y + a <= height - 1:
                if (terrain_map[y + a][x] == terrain_hole_core) | (
                    terrain_map[y + a][x] == terrain_hole_side
                ):
                    hole_tile_total += 1
                if terrain_map[y + a][x] == terrain_nest_bc:
                    bc_tile_total += 1
            # check rightward
            if x + a <= width - 1:
                if (terrain_map[y][x + a] == terrain_hole_core) | (
                    terrain_map[y][x + a] == terrain_hole_side
                ):
                    hole_tile_total += 1
                if terrain_map[y][x + a] == terrain_nest_bc:
                    bc_tile_total += 1
            # check leftward
            if x - a >= 0:
                if (terrain_map[y][x - a] == terrain_hole_core) | (
                    terrain_map[y][x - a] == terrain_hole_side
                ):
                    hole_tile_total += 1
                if terrain_map[y][x - a] == terrain_nest_bc:
                    bc_tile_total += 1
        if hole_tile_total > bc_tile_total:
            # Spawn as special tile if it happens to be on top of a swamp
            if terrain_map[y][x] == terrain_swamp:
                terrain_map[y][x] = terrain_nest_swamp_sc
            else:
                terrain_map[y][x] = terrain_nest_sc

    return terrain_map


def starve_nests(terrain_map):
    """For each BC, check other SC and BC tiles in a given range, and starve the nest if it then exceeds a limit set by sc_feed_multiplier"""
    height = len(terrain_map)
    width = len(terrain_map[0])

    for y in range(height):
        for x in range(width):
            if terrain_map[y][x] == terrain_nest_bc:
                sc_tile_total = 0
                bc_tile_total = 0
                for a in range(bc_starve_range):
                    # check upwards
                    if y - a >= 0:
                        if terrain_map[y - a][x] == terrain_nest_sc:
                            sc_tile_total += 1
                        if terrain_map[y - a][x] == terrain_nest_bc:
                            bc_tile_total += 1
                    # check downwards
                    if y + a <= height - 1:
                        if terrain_map[y + a][x] == terrain_nest_sc:
                            sc_tile_total += 1
                        if terrain_map[y + a][x] == terrain_nest_bc:
                            bc_tile_total += 1
                    # check rightward
                    if x + a <= width - 1:
                        if terrain_map[y][x + a] == terrain_nest_sc:
                            sc_tile_total += 1
                        if terrain_map[y][x + a] == terrain_nest_bc:
                            bc_tile_total += 1
                    # check leftward
                    if x - a >= 0:
                        if terrain_map[y][x - a] == terrain_nest_sc:
                            sc_tile_total += 1
                        if terrain_map[y][x - a] == terrain_nest_bc:
                            bc_tile_total += 1
                if bc_tile_total > sc_tile_total * sc_feed_multiplier:
                    # starve the bc nest
                    terrain_map[y][x] = terrain_nest_starved_bc
    return terrain_map


def distance_to_closest_sinkhole(terrain_map, tileX, tileY):
    """"Calculate and return distance to closest sinkhole."""
    min_dist = 99999
    current_dist = 0
    width = len(terrain_map[0]) - 1
    height = len(terrain_map) - 1
    for y in range(height):
        for x in range(width):
            if (terrain_map[y][x] == terrain_hole_core) | (
                terrain_map[y][x] == terrain_hole_side
            ):  # it's a sinkhole tile
                current_dist = abs(tileY - y) + abs(tileX - x)
                if current_dist < min_dist:
                    min_dist = current_dist

    return min_dist


def distance_to_closest_terrain_type(terrain_map, tileX, tileY, terrain_type):
    """"Calculate and return distance to closest specific terrain type."""
    min_dist = 99999
    current_dist = 0
    width = len(terrain_map[0]) - 1
    height = len(terrain_map) - 1
    for y in range(height):
        for x in range(width):
            if terrain_map[y][x] == terrain_type:  # it's a sinkhole tile
                current_dist = abs(tileY - y) + abs(tileX - x)
                if current_dist < min_dist:
                    min_dist = current_dist

    return min_dist


def sinkhole_adjacent(terrain_map, x, y):
    """"Returns true if any sinkhole tiles are directly adjacent, includes diagonal"""
    sinkhole_nearby = False
    bound_lo = terrain_hole_core
    bound_hi = terrain_hole_side
    width = len(terrain_map[0]) - 1
    height = len(terrain_map) - 1

    if y != 0:  # check row above
        if x != 0:
            if (terrain_map[y - 1][x - 1] >= bound_lo) & (
                terrain_map[y - 1][x - 1] <= bound_hi
            ):
                sinkhole_nearby = True
        if (terrain_map[y - 1][x] >= bound_lo) & (terrain_map[y - 1][x] <= bound_hi):
            sinkhole_nearby = True
        if x <= width - 1:
            if (terrain_map[y - 1][x + 1] >= bound_lo) & (
                terrain_map[y - 1][x + 1] <= bound_hi
            ):
                sinkhole_nearby = True

    if x <= width - 1:  # check column at right side
        if y != 0:
            if (terrain_map[y - 1][x + 1] >= bound_lo) & (
                terrain_map[y - 1][x + 1] <= bound_hi
            ):
                sinkhole_nearby = True
        if (terrain_map[y][x + 1] >= bound_lo) & (terrain_map[y][x + 1] <= bound_hi):
            sinkhole_nearby = True
        if y <= height - 1:
            if (terrain_map[y + 1][x + 1] >= bound_lo) & (
                terrain_map[y + 1][x + 1] <= bound_hi
            ):
                sinkhole_nearby = True

    if y <= height - 1:  # check row below
        if x <= 0:
            if (terrain_map[y + 1][x - 1] >= bound_lo) & (
                terrain_map[y + 1][x - 1] <= bound_hi
            ):
                sinkhole_nearby = True
        if (terrain_map[y + 1][x] >= bound_lo) & (terrain_map[y + 1][x] <= bound_hi):
            sinkhole_nearby = True
        if x <= width - 1:
            if (terrain_map[y + 1][x + 1] >= bound_lo) & (
                terrain_map[y + 1][x + 1] <= bound_hi
            ):
                sinkhole_nearby = True

    if x != 0:  # check column at left side
        if y != 0:
            if (terrain_map[y - 1][x - 1] >= bound_lo) & (
                terrain_map[y - 1][x - 1] <= bound_hi
            ):
                sinkhole_nearby = True
        if (terrain_map[y][x - 1] >= bound_lo) & (terrain_map[y - 1][x] <= bound_hi):
            sinkhole_nearby = True
        if y <= height - 1:
            if (terrain_map[y + 1][x - 1] >= bound_lo) & (
                terrain_map[y + 1][x - 1] <= bound_hi
            ):
                sinkhole_nearby = True

    return sinkhole_nearby
