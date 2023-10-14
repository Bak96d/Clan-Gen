#!/usr/bin/env python3
# -*- coding: ascii -*-
import os
from random import choice, randint

import pygame
import ujson

from scripts.utility import event_text_adjust, scale, ACC_DISPLAY, process_text, chunks

from .Screens import Screens

from scripts.utility import get_text_box_theme, scale_dimentions, shorten_text_to_fit, generate_sprite
from scripts.cat.cats import Cat, BACKSTORIES
from scripts.cat.pelts import Pelt
from scripts.game_structure import image_cache
import pygame_gui
from re import sub
from scripts.game_structure.image_button import UIImageButton, UITextBoxTweaked, UISpriteButton
from scripts.game_structure.game_essentials import game, MANAGER
from scripts.clan_resources.freshkill import FRESHKILL_ACTIVE


from scripts.game_structure.game_essentials import game, screen

class CustomizeScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.elements = {}
        self.name="SingleColour"
        self.length="short"
        self.colour="WHITE"
        self.white_patches=None
        self.eye_color="BLUE"
        self.eye_colour2=None
        self.tortiebase=None
        self.tortiecolour=None
        self.pattern=None
        self.tortiepattern=None
        self.vitiligo=None
        self.points=None
        self.accessory=None
        self.paralyzed=False
        self.opacity=100
        self.scars=None
        self.tint="none"
        self.skin="BLACK"
        self.white_patches_tint="none"
        self.kitten_sprite=None
        self.adol_sprite=None
        self.adult_sprite=None
        self.senior_sprite=None
        self.para_adult_sprite=None
        self.reverse=False
        self.accessories=[]
        
    def screen_switches(self):
        # handle screen switch
        pelt2 = Pelt(
            name=self.name,
            length=self.length,
            colour=self.colour,
            white_patches=self.white_patches,
            eye_color=self.eye_color,
            eye_colour2=self.eye_colour2,
            tortiebase=self.tortiebase,
            tortiecolour=self.tortiecolour,
            pattern=self.pattern,
            tortiepattern=self.tortiepattern,
            vitiligo=self.vitiligo,
            points=self.points,
            accessory=self.accessory,
            paralyzed=self.paralyzed,
            opacity=self.opacity,
            scars=self.scars,
            tint=self.tint,
            skin=self.skin,
            white_patches_tint=self.white_patches_tint,
            kitten_sprite=self.kitten_sprite,
            adol_sprite=self.adol_sprite,
            adult_sprite=self.adult_sprite,
            senior_sprite=self.senior_sprite,
            para_adult_sprite=self.para_adult_sprite,
            reverse=self.reverse,
            accessories=self.accessories
        )
        your_cat = Cat(moons = 1, pelt=pelt2, loading_cat=True)
        your_cat.sprite = generate_sprite(your_cat)
        self.elements["sprite"] = UISpriteButton(scale(pygame.Rect
                                         ((500,100), (200, 200))),
                                   your_cat.sprite,
                                   your_cat.ID,
                                   starting_height=0, manager=MANAGER)
        

        self.elements['pelt dropdown'] = pygame_gui.elements.UIDropDownMenu(Pelt.sprites_names.keys(), "SingleColour", scale(pygame.Rect((300,500),(200,100))), manager=MANAGER)
        self.elements['pelt color'] = pygame_gui.elements.UIDropDownMenu(Pelt.pelt_colours, "WHITE", scale(pygame.Rect((300,600),(200,100))), manager=MANAGER)


    def handle_event(self, event):
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.elements['pelt dropdown']:
                self.name = event.text
                self.update_sprite()
            if event.ui_element == self.elements['pelt color']:
                self.colour = event.text
                self.update_sprite()
                
    def update_sprite(self):
        pelt2 = Pelt(
            name=self.name,
            length=self.length,
            colour=self.colour,
            white_patches=self.white_patches,
            eye_color=self.eye_color,
            eye_colour2=self.eye_colour2,
            tortiebase=self.tortiebase,
            tortiecolour=self.tortiecolour,
            pattern=self.pattern,
            tortiepattern=self.tortiepattern,
            vitiligo=self.vitiligo,
            points=self.points,
            accessory=self.accessory,
            paralyzed=self.paralyzed,
            opacity=self.opacity,
            scars=self.scars,
            tint=self.tint,
            skin=self.skin,
            white_patches_tint=self.white_patches_tint,
            kitten_sprite=self.kitten_sprite,
            adol_sprite=self.adol_sprite,
            adult_sprite=self.adult_sprite,
            senior_sprite=self.senior_sprite,
            para_adult_sprite=self.para_adult_sprite,
            reverse=self.reverse,
            accessories=self.accessories
        )
        your_cat = Cat(moons = 1, pelt=pelt2, loading_cat=True)
        your_cat.sprite = generate_sprite(your_cat)
        self.elements['sprite'].kill()
        self.elements["sprite"] = UISpriteButton(scale(pygame.Rect
                                         ((500,100), (200, 200))),
                                   your_cat.sprite,
                                   your_cat.ID,
                                   starting_height=0, manager=MANAGER)
        

        