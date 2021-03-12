# Corrinthea

This application procedurally generates a 2d image of a world best left undiscovered: Corrinthea
Inspired by this procedural noise generation article, it populates a 2d array with float values that represent specific terrain types.

Run the following code in jupyter lab or from console: 

from map_generator import generate_world, generate_image
generate_image(generate_world())


## Description
This is a world I would not like to visit, something of an imaginary personal nightmare.

Big Creepy crawlers (BCs) come out to hunt Small Creepy fliers (SCs) - and who knows what else they might like to snack on!

The SCs feed on vapor that collects in sinkholes which are scattered around the sandy plains.

SCs are the primary food source for BCs, who like to nest nearby these sinkholes for this reason.

SCs would build their nest similarly close, except they'd just get eaten up. So they will make sure to nest nearby mossy, slimy, nasty Swamps, where they can find refuge from any prying BCs. 


* **Environment**: Sandy Plains
* **Resource**: Sinkholes
* **Prey**(nest): Small Creepies
* **Predator**(nest): Big Creepies
* **Prey Habitat**: Swamps


## Legend & Generation Conditions

All generative descriptions **bolded** in descriptions below.

### Sand (Lavender)
Default terrain type. It's extra coarse.

### Sinkholes (Purple)
Scattered across the landscape, these slightly vary in size and shape, and are placed **at a minimum of sinkhole_min_dist from other sinkholes**.

### Swamps (Green)
You think mosquitos are bad? These mossy humid forests are filled with nasty stingy plants & insects. They do not thrive near sinkhole vapors, so **will not spawn directly next to them**, and will get a **size bonus for distance to sinkholes**. Multiple swamps can spawn in or near each other.

### Big Creepycrawler Nests (Red)
Imagine giant millipedes, but much worse. They are lazy, though, so will only nest within a **bc_nest_max_dist** from sinkholes.
They don't care much for competition, either, so BC nests near a sinkhole will **affect the frequency and size of other BC nests** as they are placed.

### Big Creepycrawler Nests (Starved) (Dark Red)
Sometimes a sinkhole just doesn't provide. When there are **too many BC nests compared to SC nests** in a given radius, they can starve out due to a lack of food, turning a darker red. 

### Small Creepyflier Nests (Teal)
They're about as stingy as flying pests get, probably with a nasty venomous sting. But that won't help them defend against BCs, so they make sure to always nest **closer to Swamps than to any BC nests**. 
With a limited flight range, these nests **need to be closer than sc_nest_max_hole_dist to sinkholes** too.  

### Small Creepyflier Nests (Swamp) (Orange)
Might as well nestle in right there in the filth! These tiles have a special value for when a SC nest **spawns on top** of a pre-existing swamp tile.   
