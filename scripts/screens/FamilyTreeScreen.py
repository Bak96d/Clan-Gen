import pygame.transform
import pygame_gui.elements

from .Screens import Screens

from scripts.utility import get_text_box_theme, scale, shorten_text_to_fit
from scripts.cat.cats import Cat
from scripts.game_structure import image_cache
from scripts.game_structure.image_button import UIImageButton, UISpriteButton
from scripts.game_structure.game_essentials import game, MANAGER


class FamilyTreeScreen(Screens):
    # Page numbers for siblings and offspring

    def __init__(self, name=None):
        super().__init__(name)
        self.next_cat = None
        self.previous_cat = None

        self.next_group_page = None
        self.previous_group_page = None
        self.root_cat = None
        self.family_tree = None
        self.center_cat_frame = None
        self.root_cat_frame = None
        self.relation_backdrop = None
       
        self.back_button = None
        self.next_cat_button = None
        self.previous_cat_button = None
        self.the_cat = None

        self.cat_elements = {}
        self.relation_elements = {}
        self.tabs = {}

        self.group_page_number = 1
        self.current_group = None
        self.current_group_name = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            if event.ui_element == self.back_button:
                self.change_screen('profile screen')
                game.switches['root_cat'] = None
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    game.switches['cat'] = self.previous_cat
                    game.switches['root_cat'] = Cat.all_cats[self.previous_cat]
                    self.exit_screen()
                    self.screen_switches()
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    game.switches['cat'] = self.next_cat
                    game.switches['root_cat'] = Cat.all_cats[self.next_cat]
                    self.exit_screen()
                    self.screen_switches()
                else:
                    print("invalid next cat", self.next_cat)
            
            elif event.ui_element == self.previous_group_page:
                self.group_page_number -= 1
                self.handle_relation_groups()
            elif event.ui_element == self.next_group_page:
                self.group_page_number += 1
                self.handle_relation_groups()
           
            elif event.ui_element in self.relation_elements.values() or self.cat_elements.values():
                try:
                    id = event.ui_element.return_cat_id()
                    if Cat.fetch_cat(id).faded:
                        return
                    game.switches['cat'] = id
                except AttributeError:
                    return
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.change_screen('profile screen')
                    game.switches['root_cat'] = None
                else:
                    self.exit_screen()
                    self.screen_switches()

    def screen_switches(self):
        """Set up things that are always on the page"""

        self.current_group = None
        self.current_group_name = None
        # prev/next and back buttons
        self.previous_cat_button = UIImageButton(scale(pygame.Rect((50, 50), (306, 60))), "",
                                                 object_id="#previous_cat_button", manager=MANAGER)
        self.next_cat_button = UIImageButton(scale(pygame.Rect((1244, 50), (306, 60))), "",
                                             object_id="#next_cat_button", manager=MANAGER)
        self.back_button = UIImageButton(scale(pygame.Rect((50, 120), (210, 60))), "",
                                         object_id="#back_button", manager=MANAGER)

        # our container for the family tree, this will center itself based on visible relation group buttons
        # it starts with just the center cat frame inside it, since that will always be visible
        self.family_tree = pygame_gui.core.UIContainer(
            scale(pygame.Rect((720, 450), (160, 180))),
            MANAGER)

        # now grab the other necessary UI elements
        self.previous_group_page = UIImageButton(scale(pygame.Rect((941, 1281), (68, 68))),
                                                 "",
                                                 object_id="#arrow_left_button",
                                                 manager=MANAGER)
        self.previous_group_page.disable()
        self.next_group_page = UIImageButton(scale(pygame.Rect((1082, 1281), (68, 68))),
                                             "",
                                             object_id="#arrow_right_button",
                                             manager=MANAGER)
        self.next_group_page.disable()
        self.relation_backdrop = pygame_gui.elements.UIImage(scale(pygame.Rect((628, 950), (841, 342))),
                                                             pygame.transform.scale(
                                                                 image_cache.load_image(
                                                                     "resources/images/familytree_relationbackdrop.png").convert_alpha(),
                                                                 (841, 342)), manager=MANAGER)
        self.relation_backdrop.disable()

        if not game.switches['root_cat']:
            game.switches['root_cat'] = Cat.all_cats[game.switches['cat']]
        self.root_cat_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((129, 950), (452, 340))),
                                                          pygame.transform.scale(
                                                              image_cache.load_image(
                                                                  "resources/images/familytree_bigcatbox.png").convert_alpha(),
                                                              (452, 340)), manager=MANAGER)
        self.cat_elements["root_cat_image"] = UISpriteButton(scale(pygame.Rect((462, 1151), (100, 100))),
                                                             game.switches['root_cat'].sprite,
                                                             cat_id=game.switches['root_cat'].ID,
                                                             manager=MANAGER,
                                                             tool_tip_text=f'Started viewing tree at {game.switches["root_cat"].name}')

        self.root_cat_frame.disable()

        self.center_cat_frame = pygame_gui.elements.UIImage(scale(pygame.Rect((0, 0), (160, 180))),
                                                            pygame.transform.scale(
                                                                image_cache.load_image(
                                                                    "resources/images/familytree_smallcatbox.png").convert_alpha(),
                                                                (160, 180)),
                                                            manager=MANAGER,
                                                            container=self.family_tree)
        self.center_cat_frame.disable()
        self.group_page_number = 1
        # self.family_setup()
        self.create_family_tree()
        self.get_previous_next_cat()

    def create_family_tree(self):
        """
        this function handles creating the family tree, both collecting the relation groups and displaying the buttons
        """
        # everything in here is held together by duct tape and hope, TAKE CARE WHEN EDITING

        # the cat whose family tree is being viewed
        self.the_cat = Cat.all_cats[game.switches['cat']]

        self.cat_elements["screen_title"] = pygame_gui.elements.UITextBox(f"{self.the_cat.name}'s Family Tree",
                                                                          scale(
                                                                              pygame.Rect((300, 50),
                                                                                          (1000, 100))),
                                                                          object_id=get_text_box_theme("#text_box_30_horizcenter"),
                                                                          manager=MANAGER, )

        # will need these later to adjust positioning
        # as the various groups are collected, the x_pos and y_pos are adjusted to account for the new buttons,
        # these affect the positioning of all the buttons
        x_pos = 700
        y_pos = 500

        # as the various groups are collected, the x_dim and y_dim are adjusted to account for the new button,
        # these affect the size and positioning of the UIContainer holding the family tree
        x_dim = 160
        y_dim = 180

        if not self.the_cat.inheritance:
            self.the_cat.create_inheritance_new_cat()

        
        self.family_tree.kill()
        self.family_tree = pygame_gui.core.UIContainer(
            scale(pygame.Rect((0, 0), (2000, 2000))),
            MANAGER)

        # creating the center frame, cat, and name
        self.cat_elements["the_cat_image"] = UISpriteButton(scale(pygame.Rect((150, 969), (300, 300))),
                                                            self.the_cat.sprite,
                                                            cat_id=self.the_cat.ID,
                                                            manager=MANAGER)
        name = str(self.the_cat.name)
        short_name = shorten_text_to_fit(name, 260, 22)
        self.cat_elements["viewing_cat_text"] = pygame_gui.elements.UITextBox(f"Viewing {short_name}'s Lineage",
                                                                              scale(
                                                                                  pygame.Rect((150, 1282), (300, 150))),
                                                                              object_id=get_text_box_theme(
                                                                                  "#text_box_22_horizcenter_spacing_95"),
                                                                              manager=MANAGER, )
        
        focus_cat = self.the_cat
        self.add_family_elements(focus_cat, x_pos, y_pos, 1, direction="ancestor")
        self.add_family_elements(focus_cat, x_pos, y_pos, 1, direction="descendant")  

    def add_family_elements(self, focus_cat, x_pos, y_pos, depth=1, max_depth=5, direction="ancestor"):
        if focus_cat is None or depth > max_depth:
            return

        # Display the current cat (excluding sibling calls to avoid duplication)
        if direction != "sibling":
            name = str(focus_cat.name)
            short_name = shorten_text_to_fit(name, 260, 22)
            # self.cat_elements[f"{direction}_{depth}_{focus_cat.name}"] = pygame_gui.elements.ui_label.UILabel(
            #     scale(pygame.Rect((x_pos, y_pos), (145, 100))),
            #     short_name,
            #     object_id="#text_box_22_horizcenter",
            #     manager=MANAGER,
            #     container=self.family_tree
            # )
            self.cat_elements[f"{direction}_{depth}_{focus_cat.name}"] = UISpriteButton(scale(pygame.Rect((x_pos, y_pos), (100, 100))),
                                                            focus_cat.sprite,
                                                            cat_id=focus_cat.ID,
                                                            container=self.family_tree,
                                                            manager=MANAGER)

        # Sibling handling should not increase depth or cause further recursive calls
        if depth == 1 and direction != "sibling":
            siblings = [cat for cat_id, cat in Cat.all_cats.items() if (cat.parent1 == focus_cat.parent1 or cat.parent2 == focus_cat.parent2) and cat_id != focus_cat.name]
            sibling_spacing = 200
            # Adjust x_pos for siblings to spread out horizontally without changing y_pos
            for i, sibling in enumerate(siblings, start=1):
                sibling_x_pos = x_pos + (sibling_spacing * i) - (sibling_spacing * len(siblings) / 2)
                self.add_family_elements(sibling, sibling_x_pos, y_pos, depth, max_depth, "sibling")

        if direction == "ancestor":
            # Adjust y_pos for ancestors
            new_y_pos = y_pos - 150
            if focus_cat.parent1:
                parent1 = Cat.all_cats.get(focus_cat.parent1)
                self.add_family_elements(parent1, x_pos - 200, new_y_pos, depth + 1, max_depth, "ancestor")
            if focus_cat.parent2:
                parent2 = Cat.all_cats.get(focus_cat.parent2)
                self.add_family_elements(parent2, x_pos + 100, new_y_pos, depth + 1, max_depth, "ancestor")

        elif direction == "descendant":
            # Adjust y_pos for descendants
            children = [cat for cat_id, cat in Cat.all_cats.items() if cat.parent1 == focus_cat.ID or cat.parent2 == focus_cat.ID]
            new_y_pos = y_pos + 150
            child_spacing = 200
            # Spread children horizontally
            for i, child in enumerate(children):
                child_x_pos = x_pos + (child_spacing * i) - (child_spacing * (len(children) - 1) / 2)
                self.add_family_elements(child, child_x_pos, new_y_pos, depth + 1, max_depth, "descendant")





    def handle_relation_groups(self):
        """Updates the given group"""
        for ele in self.relation_elements:
            self.relation_elements[ele].kill()
        self.relation_elements = {}

        self.update_tab()
        if not self.current_group:
            self.relation_elements["no_cats_notice"] = pygame_gui.elements.UITextBox("None",
                                                                                     scale(
                                                                                         pygame.Rect(
                                                                                             (550, 1080),
                                                                                             (900, 60))),
                                                                                     object_id=get_text_box_theme(
                                                                                         "#text_box_30_horizcenter"),
                                                                                     manager=MANAGER)
        _current_group = self.chunks(self.current_group, 24)

        if self.group_page_number > len(_current_group):
            self.group_page_number = max(len(_current_group), 1)

        if _current_group:
            display_cats = _current_group[self.group_page_number - 1]
        else:
            display_cats = []

        pos_x = 0
        pos_y = 0
        i = 0
        for kitty in display_cats:
            _kitty = Cat.fetch_cat(kitty)
            info_text = f"{str(_kitty.name)}"
            additional_info = self.the_cat.inheritance.get_cat_info(kitty)
            if len(additional_info["type"]) > 0: # types is always real
                rel_types = [str(rel_type.value) for rel_type in additional_info["type"]]
                rel_types = set(rel_types) # remove duplicates
                if "" in rel_types: 
                    rel_types.remove("")       # removes empty
                if len(rel_types) > 0:
                    info_text += "\n"
                    info_text += ', '.join(rel_types)
                if len(additional_info["additional"]) > 0:
                    add_info = set(additional_info["additional"]) # remove duplicates
                    info_text += "\n"
                    info_text += ', '.join(add_info)

            self.relation_elements["cat" + str(i)] = UISpriteButton(
                scale(pygame.Rect((649 + pos_x, 970 + pos_y), (100, 100))),
                _kitty.sprite,
                cat_id=_kitty.ID,
                manager=MANAGER,
                tool_tip_text=info_text,
                starting_height=2
            )

            pos_x += 100
            if pos_x > 700:
                pos_y += 100
                pos_x = 0
            i += 1

        # Enable and disable page buttons.
        if len(_current_group) <= 1:
            self.previous_group_page.disable()
            self.next_group_page.disable()
        elif self.group_page_number >= len(_current_group):
            self.previous_group_page.enable()
            self.next_group_page.disable()
        elif self.group_page_number == 1 and len(self.current_group) > 1:
            self.previous_group_page.disable()
            self.next_group_page.enable()
        else:
            self.previous_group_page.enable()
            self.next_group_page.enable()

    def update_tab(self):
        for ele in self.tabs:
            self.tabs[ele].kill()
        self.tabs = {}

        if self.current_group_name == "grandparents":
            self.tabs['grandparents_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1164, 890), (256, 60))),
                                                                        pygame.transform.scale(
                                                                            image_cache.load_image(
                                                                                "resources/images/grandparents_tab.png").convert_alpha(),
                                                                            (256, 60)),
                                                                        manager=MANAGER)
        elif self.current_group_name == "parents":
            self.tabs['parents_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1246, 890), (174, 60))),
                                                                   pygame.transform.scale(
                                                                       image_cache.load_image(
                                                                           "resources/images/parents_tab.png").convert_alpha(),
                                                                       (174, 60)),
                                                                   manager=MANAGER)
        elif self.current_group_name == "parents_siblings":
            self.tabs['parents_siblings_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1123, 890), (296, 60))),
                                                                            pygame.transform.scale(
                                                                                image_cache.load_image(
                                                                                    "resources/images/parentsibling_tab.png").convert_alpha(),
                                                                                (296, 60)),
                                                                            manager=MANAGER)
        elif self.current_group_name == "cousins":
            self.tabs['cousins_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1254, 890), (166, 60))),
                                                                   pygame.transform.scale(
                                                                       image_cache.load_image(
                                                                           "resources/images/cousins_tab.png").convert_alpha(),
                                                                       (166, 60)),
                                                                   manager=MANAGER)
        elif self.current_group_name == "siblings":
            self.tabs['siblings_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1256, 890), (164, 60))),
                                                                    pygame.transform.scale(
                                                                        image_cache.load_image(
                                                                            "resources/images/siblings_tab.png").convert_alpha(),
                                                                        (164, 60)),
                                                                    manager=MANAGER)
        elif self.current_group_name == "siblings_mates":
            self.tabs['siblings_mates_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1146, 890), (274, 60))),
                                                                          pygame.transform.scale(
                                                                              image_cache.load_image(
                                                                                  "resources/images/siblingsmate_tab.png").convert_alpha(),
                                                                              (274, 60)),
                                                                          manager=MANAGER)
        elif self.current_group_name == "siblings_kits":
            self.tabs['siblings_kits_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1170, 890), (250, 60))),
                                                                         pygame.transform.scale(
                                                                             image_cache.load_image(
                                                                                 "resources/images/siblingkits_tab.png").convert_alpha(),
                                                                             (250, 60)),
                                                                         manager=MANAGER)
        elif self.current_group_name == "mates":
            self.tabs['mates_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1270, 890), (150, 60))),
                                                                 pygame.transform.scale(
                                                                     image_cache.load_image(
                                                                         "resources/images/mates_tab.png").convert_alpha(),
                                                                     (150, 60)),
                                                                 manager=MANAGER)
        elif self.current_group_name == "kits":
            self.tabs['kits_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1306, 890), (114, 60))),
                                                                pygame.transform.scale(
                                                                    image_cache.load_image(
                                                                        "resources/images/kits_tab.png").convert_alpha(),
                                                                    (114, 60)),
                                                                manager=MANAGER)
        elif self.current_group_name == "kits_mates":
            self.tabs['kits_mates_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1196, 890), (224, 60))),
                                                                      pygame.transform.scale(
                                                                          image_cache.load_image(
                                                                              "resources/images/kitsmate_tab.png").convert_alpha(),
                                                                          (224, 60)),
                                                                      manager=MANAGER)
        elif self.current_group_name == "grandkits":
            self.tabs['grandkits_tab'] = pygame_gui.elements.UIImage(scale(pygame.Rect((1220, 890), (200, 60))),
                                                                     pygame.transform.scale(
                                                                         image_cache.load_image(
                                                                             "resources/images/grandkits_tab.png").convert_alpha(),
                                                                         (200, 60)),
                                                                     manager=MANAGER)

    def get_previous_next_cat(self):
        """Determines where the previous and next buttons should lead, and enables/disables them"""

        is_instructor = False
        if self.the_cat.dead and game.clan.instructor.ID == self.the_cat.ID:
            is_instructor = True

        previous_cat = 0
        next_cat = 0
        if self.the_cat.dead and not is_instructor and not self.the_cat.df:
            previous_cat = game.clan.instructor.ID

        if is_instructor:
            next_cat = 1

        for check_cat in Cat.all_cats_list:
            if check_cat.ID == self.the_cat.ID:
                next_cat = 1
            else:
                if next_cat == 0 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                        check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    previous_cat = check_cat.ID

                elif next_cat == 1 and check_cat.ID != self.the_cat.ID and check_cat.dead == self.the_cat.dead and \
                        check_cat.ID != game.clan.instructor.ID and check_cat.outside == self.the_cat.outside and \
                        check_cat.df == self.the_cat.df and not check_cat.faded:
                    next_cat = check_cat.ID

                elif int(next_cat) > 1:
                    break

        if next_cat == 1:
            next_cat = 0

        self.next_cat = next_cat
        self.previous_cat = previous_cat

        if self.next_cat == 0:
            self.next_cat_button.disable()
        else:
            self.next_cat_button.enable()

        if self.previous_cat == 0:
            self.previous_cat_button.disable()
        else:
            self.previous_cat_button.enable()

    def chunks(self, L, n):
        return [L[x: x + n] for x in range(0, len(L), n)]

    def exit_screen(self):
        for ele in self.cat_elements:
            self.cat_elements[ele].kill()
        self.cat_elements = {}

        for ele in self.relation_elements:
            self.relation_elements[ele].kill()
        self.relation_elements = {}

        for ele in self.tabs:
            self.tabs[ele].kill()
        self.tabs = {}

        self.grandparents = []
        self.parents = []
        self.parents_siblings = []
        self.cousins = []
        self.siblings = []
        self.siblings_mates = []
        self.siblings_kits = []
        self.mates = []
        self.kits = []
        self.kits_mates = []
        self.grandkits = []
        self.current_group = None

        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.back_button.kill()
        del self.back_button
        self.family_tree.kill()
        del self.family_tree
        self.relation_backdrop.kill()
        del self.relation_backdrop
        self.root_cat_frame.kill()
        del self.root_cat_frame
        self.next_group_page.kill()
        del self.next_group_page
        self.previous_group_page.kill()
        del self.previous_group_page

