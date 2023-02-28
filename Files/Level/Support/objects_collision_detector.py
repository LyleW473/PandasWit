from Level.Objects.world_objects import BambooPile

from random import randrange as random_randrange
from math import sin, cos

from pygame.sprite import spritecollide as pygame_sprite_spritecollide
from pygame.sprite import collide_rect as pygame_sprite_collide_rect
from pygame.sprite import collide_mask as pygame_sprite_collide_mask

class ObjectCollisionDetector:

    def __init__(self, game, game_ui):
        
        # Attribute that references the Game object
        self.game = game

        # Attribute that references the GameUI object
        self.game_ui = game_ui

    def handle_bamboo_projectiles_collisions(self):

        # If there are any bamboo projectiles
        if len(self.game.bamboo_projectiles_group) > 0:

            # For each bamboo projectile 
            for bamboo_projectile in self.game.bamboo_projectiles_group:

                # --------------------------------
                # World / building tiles

                # Check for a rect collision between the bamboo projectile and world / building tiles inside the world tiles dictionary
                tile_collision_result = bamboo_projectile.rect.collidedict(self.game.world_tiles_dict)

                # If the bamboo_projectile collided with a tile
                if tile_collision_result != None:

                    # Check for a pixel-perfect collision between the bamboo projectile and the world tile that the bamboo_projectile's rect collided with
                    if pygame_sprite_collide_mask(bamboo_projectile, tile_collision_result[0]) != None:

                        # If this bamboo projectile was shot from the bamboo launcher
                        if bamboo_projectile.is_bamboo_launcher_projectile == True:
                            
                            # Create a bamboo projectiles explosion (shoots projectiles in a circle)
                            self.game.player.create_bamboo_projectiles_explosion(projectile = bamboo_projectile)

                            # Create many shattered bamboo pieces
                            self.game_ui.create_angled_polygons_effects(
                                                                        purpose = "ShatteredBambooPieces",
                                                                        position = (bamboo_projectile.rect.centerx, bamboo_projectile.rect.centery),
                                                                        specified_number_of_pieces = random_randrange(15, 25)
                                                                        )
                        # If this bamboo projectile was not shot from the bamboo launcher
                        elif bamboo_projectile.is_bamboo_launcher_projectile == False:
                            # Create a few shattered bamboo pieces
                            self.game_ui.create_angled_polygons_effects(
                                                                        purpose = "ShatteredBambooPieces",
                                                                        position = (bamboo_projectile.rect.centerx, bamboo_projectile.rect.centery),
                                                                        angle = bamboo_projectile.angle,
                                                                        specified_number_of_pieces = random_randrange(2, 6)
                                                                        )

                        # If there is a pixel-perfect collision, remove the bamboo_projectile from the specified group
                        self.game.bamboo_projectiles_group.remove(bamboo_projectile)

                # --------------------------------
                # Bosses

                # If a boss has been spawned
                if self.game.boss_group.sprite != None:

                    # If the bamboo projectile's rect has collided with the current boss' rect
                    if bamboo_projectile.rect.colliderect(self.game.boss_group.sprite.rect) == True:
                        
                        # Check for a pixel-perfect collision between the bamboo projectile and the current boss
                        if pygame_sprite_collide_mask(bamboo_projectile, self.game.boss_group.sprite) != None:

                            # ------------------------------------------------------------------------------------------------------------------------------------------------
                            # Damage

                            # Damage the current boss by the amount of damage that was passed into the bamboo projectile and a random additive damage amount (e.g. 25 - 3)
                            # Note: This allows for different damage values for e.g. different weapons
                            randomised_damage_amount =  random_randrange(-3, 3)

                            # If the current boss is the "SikaDeer"
                            if self.game.bosses_dict["CurrentBoss"] == "SikaDeer":
                                # If the deer boss is stunned
                                if self.game.boss_group.sprite.current_action == "Stunned":
                                    # Increase the base damage of the bamboo projectile by the damage multiplier dealt to the deer boss when stunned, plus a random damage amount
                                    total_damage_dealt = (bamboo_projectile.damage_amount * self.game.boss_group.sprite.behaviour_patterns_dict["Stunned"]["PlayerDamageMultiplierWhenStunned"]) + randomised_damage_amount

                                # If the deer boss is not stunned
                                elif self.game.boss_group.sprite.current_action != "Stunned":
                                    # Set the total damage to be the base damage amount plus a random damage amount
                                    total_damage_dealt = bamboo_projectile.damage_amount + randomised_damage_amount

                            # If the current boss is the "GoldenMonkey"
                            elif self.game.bosses_dict["CurrentBoss"] == "GoldenMonkey":
                                # If the golden monkey boss is currently sleeping
                                if self.game.boss_group.sprite.current_action == "Sleep":
                                    # Increase the base damage of the bamboo projectile by the damage multiplier dealt to the deer boss when stunned, plus a random damage amount
                                    total_damage_dealt = (bamboo_projectile.damage_amount * self.game.boss_group.sprite.behaviour_patterns_dict["Sleep"]["PlayerDamageMultiplierWhenBossIsSleeping"]) + randomised_damage_amount
                                
                                # If the golden monkey boss is not sleeping
                                elif self.game.boss_group.sprite.current_action != "Sleep":
                                    # Set the total damage to be the base damage amount plus a random damage amount
                                    total_damage_dealt = bamboo_projectile.damage_amount + randomised_damage_amount

                            # Deal damage to the boss
                            self.game.boss_group.sprite.extra_information_dict["CurrentHealth"] -= total_damage_dealt

                            # ------------------------------------------------------------------------------------------------------------------------------------------------
                            # Additional

                            # Play the boss' damaged flash effect
                            self.game.boss_group.sprite.extra_information_dict["DamagedFlashEffectTimer"] = self.game.boss_group.sprite.extra_information_dict["DamagedFlashEffectTime"]

                            # If the player's frenzy mode is not activated and the current boss is alive
                            if self.game.player.player_gameplay_info_dict["FrenzyModeTimer"] == None and self.game.boss_group.sprite.extra_information_dict["CurrentHealth"] > 0:
                                # Increase the player's frenzy mode meter by the deal damage increment amount, limiting it to the maximum frenzy mode value
                                self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                    self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.game.player.player_gameplay_info_dict["DealDamageFrenzyModeIncrement"],
                                                                                                    self.game.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                    )
                                # Create frenzy mode value increment effect text
                                self.game_ui.create_effect_text(
                                                                type_of_effect_text = "FrenzyModeValueIncrement",
                                                                target = "Player",
                                                                text = "+" + str(self.game.player.player_gameplay_info_dict["DealDamageFrenzyModeIncrement"]),
                                                                larger_font = False
                                                                )             
                                
                            # If the current boss is alive
                            if self.game.boss_group.sprite.extra_information_dict["CurrentHealth"] > 0:

                                # Create damage effect text
                                self.game_ui.create_effect_text(
                                                                type_of_effect_text = "Damage",
                                                                target = "Boss",
                                                                text = "-" + str(total_damage_dealt),
                                                                larger_font = False
                                                                )

                            # If this bamboo projectile was shot from the bamboo launcher
                            if bamboo_projectile.is_bamboo_launcher_projectile == True:
                                # Always (even when the boss is dead) create a bamboo projectiles explosion (shoots projectiles in a circle)
                                self.game.player.create_bamboo_projectiles_explosion(projectile = bamboo_projectile)

                                # Create many shattered bamboo pieces
                                self.game_ui.create_angled_polygons_effects(
                                                                            purpose = "ShatteredBambooPieces",
                                                                            position = (bamboo_projectile.rect.centerx, bamboo_projectile.rect.centery),
                                                                            specified_number_of_pieces = random_randrange(15, 25)
                                                                            )
                                # Play the bamboo launcher explosion sound effect
                                self.game.play_manual_sound(sound_effect = "BambooLauncherProjectileExplosion")

                            # If this bamboo projectile was not shot from the bamboo launcher
                            elif bamboo_projectile.is_bamboo_launcher_projectile == False:
                                # Create a few shattered bamboo pieces
                                self.game_ui.create_angled_polygons_effects(
                                                                            purpose = "ShatteredBambooPieces",
                                                                            position = (self.game.boss_group.sprite.rect.centerx, self.game.boss_group.sprite.rect.centery),
                                                                            angle = bamboo_projectile.angle,
                                                                            specified_number_of_pieces = random_randrange(2, 6)
                                                                            )
                                # Play the bamboo launcher explosion sound effect
                                self.game.play_manual_sound(sound_effect = "BambooProjectileHit")
                            # Remove the bamboo projectile
                            self.game.bamboo_projectiles_group.remove(bamboo_projectile)
           
                # --------------------------------
                # Chilli projectiles and bamboo projectiles

                # If there is a chilli projectiles dict
                if hasattr(self.game, "chilli_projectiles_dict"):

                    # Check for a rect collision between the bamboo projectile and world / chilli projectiles inside the chilli projectiles dictionary
                    chilli_bamboo_collision_result = bamboo_projectile.rect.collidedict(self.game.chilli_projectiles_dict)
                
                    # If the bamboo_projectile collided with a chilli projectile
                    if chilli_bamboo_collision_result != None:

                        # Check for a pixel-perfect collision between the bamboo projectile and the chilli projectile that the bamboo_projectile's rect collided with
                        if pygame_sprite_collide_mask(bamboo_projectile, chilli_bamboo_collision_result[0]) != None:
                            
                            # Take away a life from the bamboo projectile
                            bamboo_projectile.lives -= 1

                            # If the bamboo projectile has no lives
                            if bamboo_projectile.lives <= 0:

                                # If this bamboo projectile was shot from the bamboo launcher
                                if bamboo_projectile.is_bamboo_launcher_projectile == True:
                                    #  Create a bamboo projectiles explosion (shoots projectiles in a circle)
                                    self.game.player.create_bamboo_projectiles_explosion(projectile = bamboo_projectile)

                                    # Create many shattered bamboo pieces
                                    self.game_ui.create_angled_polygons_effects(
                                                                                purpose = "ShatteredBambooPieces",
                                                                                position = (bamboo_projectile.rect.centerx, bamboo_projectile.rect.centery),
                                                                                specified_number_of_pieces = random_randrange(15, 25)
                                                                                )
                                # If this bamboo projectile was not shot from the bamboo launcher
                                elif bamboo_projectile.is_bamboo_launcher_projectile == False:
                                    # Create a few shattered bamboo pieces
                                    self.game_ui.create_angled_polygons_effects(
                                                                                purpose = "ShatteredBambooPieces",
                                                                                position = (bamboo_projectile.rect.centerx, bamboo_projectile.rect.centery),
                                                                                angle = bamboo_projectile.angle,
                                                                                specified_number_of_pieces = random_randrange(2, 4)
                                                                                )         
                                # Remove it from the group
                                self.game.bamboo_projectiles_group.remove(bamboo_projectile)

                            # Create chilli pieces
                            self.game_ui.create_angled_polygons_effects(
                                                                        purpose = "ChilliPieces",
                                                                        position = (chilli_bamboo_collision_result[0].rect.centerx, chilli_bamboo_collision_result[0].rect.centery),
                                                                        angle = chilli_bamboo_collision_result[0].angle,
                                                                        specified_number_of_pieces = 5
                                                                        )                 

                            # Remove the chilli projecitle from the chilli projectiles dict
                            self.game.chilli_projectiles_dict.pop(chilli_bamboo_collision_result[0])

    def handle_bamboo_piles_collisions(self):

        # Look for collisions between the player and bamboo piles, and only delete the bamboo pile if there is a collision and the player does not currently have the maximum amount of bamboo resource
        player_and_bamboo_piles_collision_list = pygame_sprite_spritecollide(self.game.player, self.game.bamboo_piles_group, dokill = False, collided = pygame_sprite_collide_rect)
        if len(player_and_bamboo_piles_collision_list) > 0 and \
            ((self.game.player.player_gameplay_info_dict["AmountOfBambooResource"] != self.game.player.player_gameplay_info_dict["MaximumAmountOfBambooResource"]) or (self.game.player.player_gameplay_info_dict["CurrentHealth"] != self.game.player.player_gameplay_info_dict["MaximumHealth"])):

            # -------------------------------------------------------------------------------------
            # Bamboo piles and segments
            
            # Find the bamboo pile to remove
            bamboo_pile_to_remove = player_and_bamboo_piles_collision_list[0]

            # Find the segment that the bamboo pile was taking up
            segment_key = tuple(segment_number for segment_number, bamboo_pile in self.game.bamboo_piles_segments_taken_dict.items() if bamboo_pile == bamboo_pile_to_remove)

            # Set this segment to be untaken
            self.game.bamboo_piles_segments_taken_dict[segment_key[0]] = segment_key[0]

            # -------------------------------------------------------------------------------------

            # Remove the bamboo pile from the bamboo piles group
            self.game.bamboo_piles_group.remove(player_and_bamboo_piles_collision_list)

            # Add the empty tile back to the empty tiles dictionary so other items can spawn in the tile
            empty_tile = self.game.replaced_empty_tiles_dict[player_and_bamboo_piles_collision_list[0]]
            self.game.empty_tiles_dict[empty_tile] = 0

            # Remove the bamboo pile from the replaced empty tiles dict
            self.game.replaced_empty_tiles_dict.pop(player_and_bamboo_piles_collision_list[0])

            # Play the bamboo pile pick up sound effect
            self.game.play_manual_sound(sound_effect = "BambooPilePickUp")

            # If adding the bamboo pile's replenishment amount exceeds the player's maximum amount of bamboo resource
            if self.game.player.player_gameplay_info_dict["AmountOfBambooResource"] + BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"] > self.game.player.player_gameplay_info_dict["MaximumAmountOfBambooResource"]:
                # Find the amount that we can replenish the player's amount of bamboo resource to the maximum amount
                bamboo_resource_replenishment_amount = BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"] - (
                    (self.game.player.player_gameplay_info_dict["AmountOfBambooResource"] + BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"]) % self.game.player.player_gameplay_info_dict["MaximumAmountOfBambooResource"])
            
            # If adding the bamboo pile's replenishment amount is less than or equal to the player's maximum amount of bamboo resource
            elif self.game.player.player_gameplay_info_dict["AmountOfBambooResource"] + BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"] <= self.game.player.player_gameplay_info_dict["MaximumAmountOfBambooResource"]:
                # Set the health replenishment amount as the bamboo pile's full resource replenishment amount
                bamboo_resource_replenishment_amount = BambooPile.bamboo_pile_info_dict["BambooResourceReplenishAmount"]
            
            # Create bamboo resource replenishment effect text
            self.game_ui.create_effect_text(
                                            type_of_effect_text = "BambooResourceReplenishment",
                                            target = "Player",
                                            text = "+" + str(bamboo_resource_replenishment_amount),
                                            larger_font = False
                                        )

            # Increase the amount of bamboo resource that the player has, limiting it to the maximum amount the player can hold at one time
            self.game.player.player_gameplay_info_dict["AmountOfBambooResource"] += bamboo_resource_replenishment_amount

            # 75% chance of increasing the player's current health
            if random_randrange(0, 100) <= 75:

                # If adding the bamboo pile's health replenishment amount exceeds the player's health
                if self.game.player.player_gameplay_info_dict["CurrentHealth"] + BambooPile.bamboo_pile_info_dict["HealthReplenishmentAmount"] > self.game.player.player_gameplay_info_dict["MaximumHealth"]:
                    # Find the amount that we can heal the player up to their maximum health
                    health_replenishment_amount = BambooPile.bamboo_pile_info_dict["HealthReplenishmentAmount"] - (
                        (self.game.player.player_gameplay_info_dict["CurrentHealth"] + BambooPile.bamboo_pile_info_dict["HealthReplenishmentAmount"]) % self.game.player.player_gameplay_info_dict["MaximumHealth"])
                
                # If adding the bamboo pile's health replenishment amount is less than or equal to the player's health 
                elif self.game.player.player_gameplay_info_dict["CurrentHealth"] + BambooPile.bamboo_pile_info_dict["HealthReplenishmentAmount"] <= self.game.player.player_gameplay_info_dict["MaximumHealth"]:
                    # Set the health replenishment amount as the bamboo pile's full health replenishment amount
                    health_replenishment_amount = BambooPile.bamboo_pile_info_dict["HealthReplenishmentAmount"]

                # If the player is alive / has more than 0 health
                if self.game.player.player_gameplay_info_dict["CurrentHealth"] > 0:
                    # Create heal effect text
                    self.game_ui.create_effect_text(
                                                    type_of_effect_text = "Heal",
                                                    target = "Player",
                                                    text = "+" + str(health_replenishment_amount),
                                                    larger_font = False
                                                )


                # Increase the player's current health, limiting it to the maximum health the player can have
                self.game.player.player_gameplay_info_dict["CurrentHealth"] += health_replenishment_amount

    def handle_stomp_attack_nodes_collisions(self):

        # Additional check because this group does not exist until the Sika Deer boss has spawned and started stomping
        if hasattr(self.game, "stomp_attack_nodes_group") and len(self.game.stomp_attack_nodes_group) > 0:

            # For each stomp attack node
            for stomp_attack_node in self.game.stomp_attack_nodes_group:

                # --------------------------------
                # World / building tiles

                # Look for tile rect collisions between the stomp attack nodes and world / building tiles
                collision_result = stomp_attack_node.rect.collidedict(self.game.world_tiles_dict)

                # Look for tile rect collisions between the stomp attack nodes and world / building tiles
                if collision_result != None:
                    
                    # --------------------------------
                    # Building tiles

                    # If the stomp attack node image is not the same as the diameter of the attack node 
                    """ Note: This is here instead of inside the stomp attack node's increase_size method to avoid resizing the image everytime the attack node's size is changed
                    - The rect has already been adjusted according to the changed radius
                    """
                    if stomp_attack_node.image.get_width() != (stomp_attack_node.radius * 2):
                        # Rescale the image for pixel-perfect collision
                        stomp_attack_node.rescale_image()
                    
                    # Check for a pixel-perfect collision between the stomp attack node and the building tile
                    if pygame_sprite_collide_mask(stomp_attack_node, collision_result[0]) != None:

                        # If the stomp attack node was blocked by a building tile
                        if collision_result[1] == "BuildingTile":
                            
                            # If the stomp attack node has not been reflected already
                            # Note: This is so that it does not bounce backwards and forwards when inside a tile
                            if stomp_attack_node.reflected != True:
                                # Play the reflected projectile sound effect
                                self.game.play_manual_sound(sound_effect = "ReflectedProjectile")

                                # Reflect the stomp attack node, increasing its speed by 1.75
                                stomp_attack_node.horizontal_gradient *= -1.75 
                                stomp_attack_node.vertical_gradient *= -1.75
                                stomp_attack_node.reflected = True

                            # Take one life away from the building tile
                            collision_result[0].lives -= 1

                            # If the building tile has run out of lives
                            if collision_result[0].lives <= 0:

                                # "Create" an empty tile where the building tile was
                                self.game.empty_tiles_dict[self.game.player.sprite_groups["ReplacedEmptyTiles"][collision_result[0]]] = 0
                                
                                # Remove the building tile from the player's replaced empty tiles dict
                                self.game.player.sprite_groups["ReplacedEmptyTiles"].pop(collision_result[0])

                                # Remove the building tile from the world tiles group
                                self.game.world_tiles_group.remove(collision_result[0])

                                # Remove the building tile from the world tiles dictionary
                                self.game.world_tiles_dict.pop(collision_result[0])

                                # Remove the building tile from the existing building tiles list
                                self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"].remove(collision_result[0])

                                # If the building tile to remove is in the neighbouring tiles dictionary (keys)
                                if collision_result[0] in self.game.player.neighbouring_tiles_dict.keys():
                                    # Remove the building tile
                                    self.game.player.neighbouring_tiles_dict.pop(collision_result[0])

                                # Create many shattered bamboo pieces
                                self.game_ui.create_angled_polygons_effects(
                                                                            purpose = "ShatteredBambooPieces",
                                                                            position = (collision_result[0].rect.centerx, collision_result[0].rect.centery),
                                                                            specified_number_of_pieces = random_randrange(10, 20)
                                                                            )
                                                                            
                            # If the player's frenzy mode is not activated
                            if self.game.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                                # Increase the player's frenzy mode meter by the block damage increment amount, limiting it to the maximum frenzy mode value
                                self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                    self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.game.player.player_gameplay_info_dict["BlockDamageFrenzyModeIncrement"],
                                                                                                    self.game.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                )
                                # Create frenzy mode value increment effect text
                                self.game_ui.create_effect_text(
                                                                type_of_effect_text = "FrenzyModeValueIncrement",
                                                                target = "Player",
                                                                text = "+" + str(self.game.player.player_gameplay_info_dict["BlockDamageFrenzyModeIncrement"]),
                                                                larger_font = False
                                                                )                                                        
                        
                        # --------------------------------
                        # World tiles

                        # If the collided tile was a world tile
                        elif collision_result[1]  == "WorldTile":
                            # Remove the stomp attack node from the group if there is a collision
                            self.game.stomp_attack_nodes_group.remove(stomp_attack_node)
                    
                # --------------------------------
                # Player

                # Look for tile rect collisions between the stomp attack nodes and the player
                if stomp_attack_node.rect.colliderect(self.game.player.rect):
                    
                    # If the stomp attack node image is not the same as the diameter of the attack node 
                    """ Note: This is here instead of inside the stomp attack node's increase_size method to avoid resizing the image everytime the attack node's size is changed
                    - The rect has already been adjusted according to the changed radius
                    """
                    if stomp_attack_node.image.get_width() != (stomp_attack_node.radius * 2):
                        # Rescale the image for pixel-perfect collision
                        stomp_attack_node.rescale_image()

                    # Check for a pixel-perfect collision between the stomp attack node and the player
                    if pygame_sprite_collide_mask(stomp_attack_node, self.game.player) != None:

                        # Remove the stomp attack node from the group if there is a collision
                        self.game.stomp_attack_nodes_group.remove(stomp_attack_node)
                        
                        # Damage the player by the stomp attack node damage
                        self.game.player.player_gameplay_info_dict["CurrentHealth"] -= stomp_attack_node.damage_amount

                        # Play the player hurt sound effect
                        self.game.play_manual_sound(sound_effect = "PlayerHurt")

                        # If the player is alive / has more than 0 health
                        if self.game.player.player_gameplay_info_dict["CurrentHealth"] > 0:
                            # Create damage effect text
                            self.game_ui.create_effect_text(
                                                            type_of_effect_text = "Damage",
                                                            target = "Player",
                                                            text = "-" + str(stomp_attack_node.damage_amount),
                                                            larger_font = False
                                                        )
                                                        
                        # Set the damaged flash effect timer to the damage flash effect time set (damaged flashing effect)
                        self.game.player.player_gameplay_info_dict["DamagedFlashEffectTimer"] = self.game.player.player_gameplay_info_dict["DamagedFlashEffectTime"]

                        # If the player's frenzy mode is not activated
                        if self.game.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                            # Increase the player's frenzy mode meter by the take damage increment amount, limiting it to the maximum frenzy mode value
                            self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.game.player.player_gameplay_info_dict["TakeDamageFrenzyModeIncrement"],
                                                                                                self.game.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                )
                            # Create frenzy mode value increment effect text
                            self.game_ui.create_effect_text(
                                                            type_of_effect_text = "FrenzyModeValueIncrement",
                                                            target = "Player",
                                                            text = "+" + str(self.game.player.player_gameplay_info_dict["TakeDamageFrenzyModeIncrement"]),
                                                            larger_font = False
                                                            )
                # --------------------------------
                # Boss

                # Look for tile rect collisions between the stomp attack nodes and the current boss
                # Only enter if there is a rect collision and the stomp attack node was reflected
                if self.game.boss_group.sprite != None and stomp_attack_node.rect.colliderect(self.game.boss_group.sprite.rect) and stomp_attack_node.reflected == True:
                    
                    # If the stomp attack node image is not the same as the diameter of the attack node 
                    """ Note: This is here instead of inside the stomp attack node's increase_size method to avoid resizing the image everytime the attack node's size is changed
                    - The rect has already been adjusted according to the changed radius
                    """
                    if stomp_attack_node.image.get_width() != (stomp_attack_node.radius * 2):
                        # Rescale the image for pixel-perfect collision
                        stomp_attack_node.rescale_image()

                    # Check for a pixel-perfect collision between the bamboo projectile and the current boss
                    if pygame_sprite_collide_mask(stomp_attack_node, self.game.boss_group.sprite) != None:
                        
                        # Remove the stomp attack node from the group if there is a collision
                        self.game.stomp_attack_nodes_group.remove(stomp_attack_node)
                        
                        # Damage the boss by 5 times the stomp attack node damage
                        self.game.boss_group.sprite.extra_information_dict["CurrentHealth"] -= (stomp_attack_node.damage_amount * self.game.player.tools["BuildingTool"]["ReflectionDamageMultiplier"])

                        # If the boss is alive / has more than 0 health
                        if self.game.boss_group.sprite.extra_information_dict["CurrentHealth"] > 0:
                            # Create damage effect text
                            self.game_ui.create_effect_text(
                                                            type_of_effect_text = "Damage",
                                                            target = "Boss",
                                                            text = "-" + str(stomp_attack_node.damage_amount * self.game.player.tools["BuildingTool"]["ReflectionDamageMultiplier"]),
                                                            larger_font = False
                                                        )

                        # Set the damaged flash effect timer to the damage flash effect time set (damaged flashing effect)
                        self.game.boss_group.sprite.extra_information_dict["DamagedFlashEffectTimer"] = self.game.boss_group.sprite.extra_information_dict["DamagedFlashEffectTime"]

                        # If the player's frenzy mode is not activated
                        if self.game.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                            # Increase the player's frenzy mode meter by the reflect damage increment amount, limiting it to the maximum frenzy mode value
                            self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.game.player.player_gameplay_info_dict["ReflectDamageFrenzyModeIncrement"],
                                                                                                self.game.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                )
                            # Create frenzy mode value increment effect text
                            self.game_ui.create_effect_text(
                                                            type_of_effect_text = "FrenzyModeValueIncrement",
                                                            target = "Player",
                                                            text = "+" + str(self.game.player.player_gameplay_info_dict["ReflectDamageFrenzyModeIncrement"]),
                                                            larger_font = False
                                                            )

    def handle_chilli_projectiles_collisions(self):

        # Additional check because this group does not exist until the Golden Monkey boss has spawned
        if hasattr(self.game, "chilli_projectiles_dict") and len(self.game.chilli_projectiles_dict) > 0:

            # For each chilli projectile
            for chilli_projectile in self.game.chilli_projectiles_dict.copy().keys():

                # --------------------------------
                # World / building tiles

                # Look for tile rect collisions between the chilli projectiles and world / building tiles
                collision_result = chilli_projectile.rect.collidedict(self.game.world_tiles_dict)

                # If there were any rect collisions
                if collision_result != None:
                    
                    # --------------------------------
                    # Building tiles
                    
                    # Check for a pixel-perfect collision between the chilli projectile and the building tile
                    if pygame_sprite_collide_mask(chilli_projectile, collision_result[0]) != None:
                        
                        # If the chilli projectile was blocked by a building tile
                        if collision_result[1] == "BuildingTile":
                            
                            # Take one life away from the building tile
                            collision_result[0].lives -= 1

                            # If the building tile has run out of lives
                            if collision_result[0].lives <= 0:

                                # "Create" an empty tile where the building tile was
                                self.game.empty_tiles_dict[self.game.player.sprite_groups["ReplacedEmptyTiles"][collision_result[0]]] = 0
                                
                                # Remove the building tile from the player's replaced empty tiles dict
                                self.game.player.sprite_groups["ReplacedEmptyTiles"].pop(collision_result[0])

                                # Remove the building tile from the world tiles group
                                self.game.world_tiles_group.remove(collision_result[0])

                                # Remove the building tile from the world tiles dictionary
                                self.game.world_tiles_dict.pop(collision_result[0])

                                # Remove the building tile from the existing building tiles list
                                self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"].remove(collision_result[0])

                                # If the building tile to remove is in the neighbouring tiles dictionary (keys)
                                if collision_result[0] in self.game.player.neighbouring_tiles_dict.keys():
                                    # Remove the building tile
                                    self.game.player.neighbouring_tiles_dict.pop(collision_result[0])

                                # Play the sound effect for when a chilli projectile breaks a building tile
                                self.game.play_manual_sound(
                                                    sound_effect = "ChilliProjectileTileCollision", 
                                                    specific_cooldown_timer = self.game.boss_group.sprite.behaviour_patterns_dict["Chase"]["ChilliThrowingCooldown"]
                                                    )


                                # Create many shattered bamboo pieces
                                self.game_ui.create_angled_polygons_effects(
                                                                            purpose = "ShatteredBambooPieces",
                                                                            position = (collision_result[0].rect.centerx, collision_result[0].rect.centery),
                                                                            specified_number_of_pieces = random_randrange(10, 20)
                                                                            )
                                                                            
                            # If the player's frenzy mode is not activated
                            if self.game.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                                # Increase the player's frenzy mode meter by the block damage increment amount, limiting it to the maximum frenzy mode value
                                self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                    self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.game.player.player_gameplay_info_dict["BlockDamageFrenzyModeIncrement"],
                                                                                                    self.game.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                )
                                # Create frenzy mode value increment effect text
                                self.game_ui.create_effect_text(
                                                                type_of_effect_text = "FrenzyModeValueIncrement",
                                                                target = "Player",
                                                                text = "+" + str(self.game.player.player_gameplay_info_dict["BlockDamageFrenzyModeIncrement"]),
                                                                larger_font = False
                                                                )       

                            # Remove the chilli projectile from the group if there is a collision
                            self.game.chilli_projectiles_dict.pop(chilli_projectile)

                            # Go to the next chilli projectile
                            """ Note: This is because a copy of the chilli projectiles dictionary was made, and collisions with the player are checked straight after, 
                            which would output an error if there was a collision with a bamboo projectile and the player.
                            """
                            continue

                    # --------------------------------
                    # World tiles

                        # If the collided tile was a world tiles
                        elif collision_result[1]  == "WorldTile":
                            # Remove the chilli projectile from the dict if there is a collision
                            self.game.chilli_projectiles_dict.pop(chilli_projectile)

                            # Go to the next chilli projectile
                            """ Note: This is because a copy of the chilli projectiles dictionary was made, and collisions with the player are checked straight after, 
                            which would output an error if there was a collision with a bamboo projectile and the player.
                            """
                            continue
                    
                # --------------------------------
                # Player

                # Look for tile rect collisions between the chilli projectile and the player
                if chilli_projectile.rect.colliderect(self.game.player.rect):
                    
                    # Check for a pixel-perfect collision between the chilli projectile and the player
                    if pygame_sprite_collide_mask(chilli_projectile, self.game.player) != None:

                        # Remove the chilli projectile from the dict if there is a collision
                        self.game.chilli_projectiles_dict.pop(chilli_projectile)
                        
                        # Damage the player by the stomp attack node damage
                        self.game.player.player_gameplay_info_dict["CurrentHealth"] -= chilli_projectile.damage_amount

                        # Play the player hurt sound effect
                        self.game.play_manual_sound(sound_effect = "PlayerHurt")

                        # If the player is alive / has more than 0 health
                        if self.game.player.player_gameplay_info_dict["CurrentHealth"] > 0:
                            # Create damage effect text
                            self.game_ui.create_effect_text(
                                                            type_of_effect_text = "Damage",
                                                            target = "Player",
                                                            text = "-" + str(chilli_projectile.damage_amount),
                                                            larger_font = False
                                                        )
                                                        
                        # Set the damaged flash effect timer to the damage flash effect time set (damaged flashing effect)
                        self.game.player.player_gameplay_info_dict["DamagedFlashEffectTimer"] = self.game.player.player_gameplay_info_dict["DamagedFlashEffectTime"]

                        # If the player's frenzy mode is not activated
                        if self.game.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                            # Increase the player's frenzy mode meter by the take damage increment amount, limiting it to the maximum frenzy mode value
                            self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.game.player.player_gameplay_info_dict["TakeDamageFrenzyModeIncrement"],
                                                                                                self.game.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                )
                            # Create frenzy mode value increment effect text
                            self.game_ui.create_effect_text(
                                                            type_of_effect_text = "FrenzyModeValueIncrement",
                                                            target = "Player",
                                                            text = "+" + str(self.game.player.player_gameplay_info_dict["TakeDamageFrenzyModeIncrement"]),
                                                            larger_font = False
                                                            )

    def handle_dive_bomb_attack_circles_collisions(self):

        # If the boss just landed after performing a divebomb attack
        if self.game.boss_group.sprite.behaviour_patterns_dict["DurationTimer"] == self.game.boss_group.sprite.behaviour_patterns_dict["DiveBomb"]["Land"]["Duration"]:
        
            # Create a camera shake effect for when the boss lands onto the ground
            self.game.camera.camera_shake_info_dict["EventsList"].append("DiveBomb")

            # Play the dive bomb sound effect
            self.game.play_manual_sound(sound_effect = "DiveBomb")

            # --------------------------------------
            # Building tiles

            # If there is at least one existing building tile
            if (len(self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"]) > 0):
                
                # Find the index of the building tile in the existing building tiles list if there is a rect collision between the tile and the boss
                building_collision_result_indexes = self.game.boss_group.sprite.dive_bomb_attack_controller.rect.collidelistall(self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"])

                # If there are any rect collisions
                if len(building_collision_result_indexes) > 0:
                    
                    # Create a tuple with the indexes of building tiles inside the existing building tiles list, if there is pixel-perfect collision between the tile and the dive bomb attack circle
                    pixel_perfect_collision_indexes_tuple = tuple(
                                        building_collision_result_index for building_collision_result_index in building_collision_result_indexes 
                                        if pygame_sprite_collide_mask(self.game.boss_group.sprite.dive_bomb_attack_controller, self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"][building_collision_result_index]) != None
                                                            )

                    # For each building tile index
                    for building_collision_result_index in pixel_perfect_collision_indexes_tuple:

                        # Temporary variable for the building tile to remove
                        building_tile_to_remove = self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"][building_collision_result_index]

                        # "Create" an empty tile where the building tile was
                        self.game.empty_tiles_dict[self.game.player.sprite_groups["ReplacedEmptyTiles"][building_tile_to_remove]] = 0
                        
                        # Remove the building tile from the player's replaced empty tiles dict
                        self.game.player.sprite_groups["ReplacedEmptyTiles"].pop(building_tile_to_remove)

                        # Remove the building tile from the world tiles group
                        self.game.world_tiles_group.remove(building_tile_to_remove)

                        # Remove the building tile from the world tiles dictionary
                        self.game.world_tiles_dict.pop(building_tile_to_remove)

                        # If the building tile to remove is in the neighbouring tiles dictionary (keys)
                        if building_tile_to_remove in self.game.player.neighbouring_tiles_dict.keys():
                            # Remove the building tile
                            self.game.player.neighbouring_tiles_dict.pop(building_tile_to_remove)

                        # Create many shattered bamboo pieces
                        self.game_ui.create_angled_polygons_effects(
                                                                    purpose = "ShatteredBambooPieces",
                                                                    position = (building_tile_to_remove.rect.centerx, building_tile_to_remove.rect.centery),
                                                                    specified_number_of_pieces = random_randrange(10, 20)
                                                                    )

                    # Rebuild the existing building tiles list
                    # Note: This is because, popping whilst iterating over the list would cause an index error
                    self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"] = [
                        self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"][i] for i in range(0, len(self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"])) if i not in pixel_perfect_collision_indexes_tuple]

            # ------------------------------------------------------------------
            # Player

            # If there is pixel perfect collision and the player has not been knocked back yet
            if pygame_sprite_collide_mask(self.game.boss_group.sprite.dive_bomb_attack_controller, self.game.player) and self.game.player.player_gameplay_info_dict["InvincibilityTimer"] == None and (self.game.boss_group.sprite.movement_information_dict["KnockbackCollisionIdleTimer"] == None):
                
                # -------------------
                # Error prevention

                """Note: This occurs if the boss divebombs the player before its move method has been called"""
                try:
                    # Knockback the player
                    self.game.player.player_gameplay_info_dict["KnockbackAttackDirection"] = [self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatS"], self.game.boss_group.sprite.movement_information_dict["VerticalSuvatS"]]
                    self.game.player.player_gameplay_info_dict["KnockbackTimer"] = self.game.player.player_gameplay_info_dict["KnockbackTime"] * 2
                except:
                    # Set the horizontal distance travelled based on the current velocity of the boss
                    self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatS"] = ((self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatU"] * self.game.boss_group.sprite.movement_information_dict["DeltaTime"]) + (0.5 * self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatA"] * (self.game.boss_group.sprite.movement_information_dict["DeltaTime"] ** 2)))
                    # Set the vertical distance travelled based on the current velocity of the boss
                    self.game.boss_group.sprite.movement_information_dict["VerticalSuvatS"] = ((self.game.boss_group.sprite.movement_information_dict["VerticalSuvatU"] * self.game.boss_group.sprite.movement_information_dict["DeltaTime"]) + (0.5 * self.game.boss_group.sprite.movement_information_dict["VerticalSuvatA"] * (self.game.boss_group.sprite.movement_information_dict["DeltaTime"] ** 2)))
                    
                # Knockback the player
                self.game.player.player_gameplay_info_dict["KnockbackAttackDirection"] = [self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatS"], self.game.boss_group.sprite.movement_information_dict["VerticalSuvatS"]]
                self.game.player.player_gameplay_info_dict["KnockbackTimer"] = self.game.player.player_gameplay_info_dict["KnockbackTime"]

                # Set the horizontal and vertical distance the player should travel based on the angle the boss hit it
                # Note: Divided by 1000 because the knockback time is in milliseconds
                self.game.player.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] = (self.game.player.player_gameplay_info_dict["KnockbackDistanceTravelled"] * cos(self.game.boss_group.sprite.movement_information_dict["Angle"])) / (self.game.player.player_gameplay_info_dict["KnockbackTime"] / 1000)
                self.game.player.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] = (self.game.player.player_gameplay_info_dict["KnockbackDistanceTravelled"] * sin(self.game.boss_group.sprite.movement_information_dict["Angle"])) / (self.game.player.player_gameplay_info_dict["KnockbackTime"] / 1000)
                """Multipled by the divebomb knockback multiplier for a stronger knockback"""
                self.game.player.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] *= self.game.boss_group.sprite.dive_bomb_attack_controller.knockback_multiplier
                self.game.player.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] *= self.game.boss_group.sprite.dive_bomb_attack_controller.knockback_multiplier

                # Play the player hurt sound effect
                self.game.play_manual_sound(sound_effect = "PlayerHurt")

                # Set the player's invincibility timer to start counting down 
                self.game.player.player_gameplay_info_dict["InvincibilityTimer"] = self.game.player.player_gameplay_info_dict["InvincibilityTime"]

                # If the player is alive / has more than 0 health
                if self.game.player.player_gameplay_info_dict["CurrentHealth"] > 0:
                    # Create damage effect text
                    self.game_ui.create_effect_text(
                                                    type_of_effect_text = "Damage",
                                                    target = "Player",
                                                    text = "-" + str(self.game.boss_group.sprite.dive_bomb_attack_controller.damage_amount),
                                                    larger_font = True
                                                )

                # Set the boss to stop moving momentarily
                self.game.boss_group.sprite.movement_information_dict["KnockbackCollisionIdleTimer"] = self.game.boss_group.sprite.movement_information_dict["KnockbackCollisionIdleTime"]

                # Reset the boss' movement acceleration
                self.game.boss_group.sprite.reset_movement_acceleration(horizontal_reset = True, vertical_reset = True)

                # Damage the player by the amount of knockback damage the divebomb attack deals
                self.game.player.player_gameplay_info_dict["CurrentHealth"] = max(self.game.player.player_gameplay_info_dict["CurrentHealth"] - self.game.boss_group.sprite.dive_bomb_attack_controller.damage_amount, 0)

    def handle_charge_attack_collisions(self):

        # If there is an x or y world tile collision
        if self.game.boss_group.sprite.movement_information_dict["WorldTileCollisionResultsX"] == True or self.game.boss_group.sprite.movement_information_dict["WorldTileCollisionResultsY"] == True:
            # Play the sound effect for when the boss collides with a tile when charging
            self.game.play_manual_sound(sound_effect = "ChargeTileCollision")

            # Set the player to change into the "Stunned" state (this will be done inside the SikaDeer class)
            self.game.boss_group.sprite.behaviour_patterns_dict["Charge"]["EnterStunnedStateBoolean"] = True

            # Set the "Charge" duration timer to 0, to end the charge attack
            self.game.boss_group.sprite.behaviour_patterns_dict["DurationTimer"] = 0

            # Set the "Stunned" duration timer to start counting down from half the duration (should be shorter as the player did not block them)
            self.game.boss_group.sprite.behaviour_patterns_dict["DurationTimer"] = (self.game.boss_group.sprite.behaviour_patterns_dict["Stunned"]["Duration"] / 2)

            # Create a camera shake effect for when the boss collides with a tile
            self.game.camera.camera_shake_info_dict["EventsList"].append("BossTileCollide")

    def handle_boss_collisions(self):

        # Boss attacks (other than projectiles) and boss collisions
        
        # -------------------------------------------------------------------------------------- 
        # Bosses

        # If there is a current boss and they are alive
        if self.game.boss_group.sprite != None and self.game.boss_group.sprite.extra_information_dict["CurrentHealth"] > 0:

            # --------------------------------------
            # Building tiles

            # If there is at least one existing building tile
            if (len(self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"]) > 0):
            
                # Find the index of the building tile in the existing building tiles list if there is a rect collision between the tile and the boss
                building_collision_result_index = self.game.boss_group.sprite.rect.collidelist(self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"])
                
                # If there is a collision
                if building_collision_result_index != -1:
                    
                    # Check for pixel-perfect collision between the boss and the building tile
                    if pygame_sprite_collide_mask(self.game.boss_group.sprite, self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"][building_collision_result_index]) != None:
                        
                        # Temporary variable for the building tile to remove
                        building_tile_to_remove = self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"][building_collision_result_index]

                        # "Create" an empty tile where the building tile was
                        self.game.empty_tiles_dict[self.game.player.sprite_groups["ReplacedEmptyTiles"][building_tile_to_remove]] = 0
                        
                        # Remove the building tile from the player's replaced empty tiles dict
                        self.game.player.sprite_groups["ReplacedEmptyTiles"].pop(building_tile_to_remove)

                        # Remove the building tile from the world tiles group
                        self.game.world_tiles_group.remove(building_tile_to_remove)

                        # Remove the building tile from the world tiles dictionary
                        self.game.world_tiles_dict.pop(building_tile_to_remove)

                        # Remove the building tile from the existing building tiles list
                        self.game.player.tools["BuildingTool"]["ExistingBuildingTilesList"].pop(building_collision_result_index)

                        # If the building tile to remove is in the neighbouring tiles dictionary (keys)
                        if building_tile_to_remove in self.game.player.neighbouring_tiles_dict.keys():
                            # Remove the building tile
                            self.game.player.neighbouring_tiles_dict.pop(building_tile_to_remove)

                        # ------------------------------------------------------------------
                        # Additional effects
                        
                        # Create many shattered bamboo pieces
                        self.game_ui.create_angled_polygons_effects(
                                                                    purpose = "ShatteredBambooPieces",
                                                                    position = (building_tile_to_remove.rect.centerx, building_tile_to_remove.rect.centery),
                                                                    specified_number_of_pieces = random_randrange(10, 20)
                                                                    )

                        # If the boss is currently chasing the player
                        if self.game.boss_group.sprite.current_action == "Chase":
                            # Reset the boss' movement acceleration, so that they slow down
                            self.game.boss_group.sprite.reset_movement_acceleration(horizontal_reset = True, vertical_reset = True)
                            # Play the sound effect when the boss runs into a tile
                            self.game.play_manual_sound(sound_effect = "BossTileSmallCollision")

                        # If the boss is the "SikaDeer" and collided with the player whilst charge attacking
                        elif self.game.bosses_dict["CurrentBoss"] == "SikaDeer" and self.game.boss_group.sprite.current_action == "Charge":

                            # Play the sound effect for when the boss collides with a tile when charging
                            self.game.play_manual_sound(sound_effect = "ChargeTileCollision")

                            # Reset the boss' movement acceleration, so that they slow down
                            self.game.boss_group.sprite.reset_movement_acceleration(horizontal_reset = True, vertical_reset = True)

                            # Set the player to change into the "Stunned" state (this will be done inside the SikaDeer class)
                            self.game.boss_group.sprite.behaviour_patterns_dict["Charge"]["EnterStunnedStateBoolean"] = True

                            # Set the "Charge" duration timer to 0, to end the charge attack
                            self.game.boss_group.sprite.behaviour_patterns_dict["DurationTimer"] = 0

                            # Damage the current boss by the amount of damage dealt from being stunned
                            self.game.boss_group.sprite.extra_information_dict["CurrentHealth"] -= self.game.boss_group.sprite.behaviour_patterns_dict["Stunned"]["StunnedDamageAmount"]

                            # Create damage effect text
                            self.game_ui.create_effect_text(
                                                            type_of_effect_text = "Damage",
                                                            target = "Boss",
                                                            text = "-" + str(self.game.boss_group.sprite.behaviour_patterns_dict["Stunned"]["StunnedDamageAmount"]),
                                                            larger_font = True
                                                            )
                            
                            # If the player's frenzy mode is not activated
                            if self.game.player.player_gameplay_info_dict["FrenzyModeTimer"] == None:
                                # Increase the player's frenzy mode meter by the stun enemy increment amount, limiting it to the maximum frenzy mode value
                                self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] = min(
                                                                                                    self.game.player.player_gameplay_info_dict["CurrentFrenzyModeValue"] + self.game.player.player_gameplay_info_dict["StunEnemyFrenzyModeIncrement"],
                                                                                                    self.game.player.player_gameplay_info_dict["MaximumFrenzyModeValue"]
                                                                                                    )

                                # Create frenzy mode value increment effect text
                                self.game_ui.create_effect_text(
                                                                type_of_effect_text = "FrenzyModeValueIncrement",
                                                                target = "Player",
                                                                text = "+" + str(self.game.player.player_gameplay_info_dict["StunEnemyFrenzyModeIncrement"]),
                                                                larger_font = True
                                                                )
                                        
                            # Create a camera shake effect for when the boss collides with a tile
                            self.game.camera.camera_shake_info_dict["EventsList"].append("BossTileCollide")

            # --------------------------------------
            # World tiles while charging

            # Only if the boss is the "SikaDeer" and the current action is "Charge"
            if self.game.bosses_dict["CurrentBoss"] == "SikaDeer" and self.game.boss_group.sprite.current_action == "Charge":
                self.handle_charge_attack_collisions()

            # --------------------------------------
            # Dive bomb attack circles

            # Only if the boss is the "SikaDeer" and the current action is "DiveBomb"
            if self.game.bosses_dict["CurrentBoss"] == "GoldenMonkey" and self.game.boss_group.sprite.current_action == "DiveBomb":
                self.handle_dive_bomb_attack_circles_collisions()

            # --------------------------------------
            # Player

            # If there is a rect collision between the player and the boss is not currently idling after the knockback and the boss is not currently stunned

            """ Checks:
            - If the boss collides with the player
            - If the boss is not idling after knocking back the player (so that the player doesn't keep setting off the idle timer in quick succession)
            - If the boss is not currently stunned 
            - If the player is not invincible (after getting knocked back recently)
            - The boss is the Golden Monkey and they are not currently performing the dive bomb attack, and is currently launching
            - If the boss' current action is not "Sleep"
            """
            if self.game.boss_group.sprite.rect.colliderect(self.game.player.rect) == True and \
                (self.game.boss_group.sprite.movement_information_dict["KnockbackCollisionIdleTimer"] == None) and \
                    self.game.boss_group.sprite.current_action != "Stunned" and \
                        self.game.player.player_gameplay_info_dict["InvincibilityTimer"] == None and \
                            (self.game.boss_group.sprite.current_action == "DiveBomb" and self.game.boss_group.sprite.behaviour_patterns_dict["DiveBomb"]["CurrentDiveBombStage"] == "Launch") == False and \
                                self.game.boss_group.sprite.current_action != "Sleep":

                # If there is pixel-perfect collision 
                if pygame_sprite_collide_mask(self.game.boss_group.sprite, self.game.player):
                    # -------------------
                    # Error prevention
                    """Note: This occurs if the boss has collided with the player before its move method has been called"""
                    try:
                        # Knockback the player
                        self.game.player.player_gameplay_info_dict["KnockbackAttackDirection"] = [self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatS"], self.game.boss_group.sprite.movement_information_dict["VerticalSuvatS"]]
                        self.game.player.player_gameplay_info_dict["KnockbackTimer"] = self.game.player.player_gameplay_info_dict["KnockbackTime"]
                    except:
                        # Set the horizontal distance travelled based on the current velocity of the boss
                        self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatS"] = ((self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatU"] * self.game.boss_group.sprite.movement_information_dict["DeltaTime"]) + (0.5 * self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatA"] * (self.game.boss_group.sprite.movement_information_dict["DeltaTime"] ** 2)))
                        # Set the vertical distance travelled based on the current velocity of the boss
                        self.game.boss_group.sprite.movement_information_dict["VerticalSuvatS"] = ((self.game.boss_group.sprite.movement_information_dict["VerticalSuvatU"] * self.game.boss_group.sprite.movement_information_dict["DeltaTime"]) + (0.5 * self.game.boss_group.sprite.movement_information_dict["VerticalSuvatA"] * (self.game.boss_group.sprite.movement_information_dict["DeltaTime"] ** 2)))
                        
                        # Knockback the player
                        self.game.player.player_gameplay_info_dict["KnockbackAttackDirection"] = [self.game.boss_group.sprite.movement_information_dict["HorizontalSuvatS"], self.game.boss_group.sprite.movement_information_dict["VerticalSuvatS"]]
                        self.game.player.player_gameplay_info_dict["KnockbackTimer"] = self.game.player.player_gameplay_info_dict["KnockbackTime"]

                    # Set the horizontal and vertical distance the player should travel based on the angle the boss hit it
                    # Note: Divided by 1000 because the knockback time is in milliseconds
                    self.game.player.player_gameplay_info_dict["KnockbackHorizontalDistanceTimeGradient"] = (self.game.player.player_gameplay_info_dict["KnockbackDistanceTravelled"] * cos(self.game.boss_group.sprite.movement_information_dict["Angle"])) / (self.game.player.player_gameplay_info_dict["KnockbackTime"] / 1000)
                    self.game.player.player_gameplay_info_dict["KnockbackVerticalDistanceTimeGradient"] = (self.game.player.player_gameplay_info_dict["KnockbackDistanceTravelled"] * sin(self.game.boss_group.sprite.movement_information_dict["Angle"])) / (self.game.player.player_gameplay_info_dict["KnockbackTime"] / 1000)

                    # Set the player's invincibility timer to start counting down 
                    self.game.player.player_gameplay_info_dict["InvincibilityTimer"] = self.game.player.player_gameplay_info_dict["InvincibilityTime"]

                    # If the player is alive / has more than 0 health
                    if self.game.player.player_gameplay_info_dict["CurrentHealth"] > 0:
                        # Create damage effect text
                        self.game_ui.create_effect_text(
                                                        type_of_effect_text = "Damage",
                                                        target = "Player",
                                                        text = "-" + str(self.game.boss_group.sprite.extra_information_dict["KnockbackDamage"]),
                                                        larger_font = False
                                                    )
                    
                    # Play the player hurt sound effect
                    self.game.play_manual_sound(sound_effect = "PlayerHurt")

                    # If the boss is the "SikaDeer" and collided with the player whilst charge attacking
                    if self.game.bosses_dict["CurrentBoss"] == "SikaDeer" and self.game.boss_group.sprite.current_action == "Charge":
                        # Set the duration timer to 0 (to end the charge attack)
                        self.game.boss_group.sprite.behaviour_patterns_dict["DurationTimer"] = 0

                    # Set the boss to stop moving momentarily
                    self.game.boss_group.sprite.movement_information_dict["KnockbackCollisionIdleTimer"] = self.game.boss_group.sprite.movement_information_dict["KnockbackCollisionIdleTime"]

                    # Reset the boss' movement acceleration
                    self.game.boss_group.sprite.reset_movement_acceleration(horizontal_reset = True, vertical_reset = True)

                    # Damage the player by the amount of knockback damage the current boss deals
                    self.game.player.player_gameplay_info_dict["CurrentHealth"] = max(self.game.player.player_gameplay_info_dict["CurrentHealth"] - self.game.boss_group.sprite.extra_information_dict["KnockbackDamage"], 0)

    def handle_collisions(self):
        
        # Calls the methods to handle collisions between objects
        
        self.handle_bamboo_projectiles_collisions()

        self.handle_bamboo_piles_collisions()

        self.handle_stomp_attack_nodes_collisions()

        self.handle_chilli_projectiles_collisions()
        
        self.handle_boss_collisions()