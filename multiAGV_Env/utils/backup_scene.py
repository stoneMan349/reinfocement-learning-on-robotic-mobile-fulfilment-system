import copy
import random
import sys
import pygame
from utils.utils import Direction as dir
from utils.utils import ColorBox as colorbox
from collections import namedtuple
import os

sys.path.append(os.path.dirname(__file__))
import utils.astar as astar


# from . import astar
# import astar as ass


class Scene:
    def __init__(self, layout, explorer_group):
        """"all parameters about drawing scene"""
        self.layout = layout
        self.control_pattern = ""
        self.clock = None
        self.FPS = 5  # 300
        self.x_width = self.layout.scene_x_width
        self.y_width = self.layout.scene_y_width
        # other parameters related to scene
        self.border_width = 30
        self.line_width = 2
        self.color_box = colorbox()
        # size of main interface
        self.cell_width = 36
        self.interface_width = self.x_width * self.cell_width - (self.x_width - 1) * self.line_width
        self.interface_height = self.y_width * self.cell_width - (self.y_width - 1) * self.line_width
        self.interface_start_x = self.border_width
        self.interface_start_y = self.border_width
        # size of sidebar
        self.sidebar_width = 200
        self.sidebar_height = self.interface_height + 2 * self.border_width
        self.sidebar_start_x = self.interface_width + 2 * self.border_width
        self.sidebar_start_y = 0
        # size of screen
        self.screen_width = self.interface_width + 2 * self.border_width + self.sidebar_width
        self.screen_height = self.interface_height + 2 * self.border_width
        # parameters related to AGV
        self.AGV_icon_scale = 0.9
        self.explorer_group = explorer_group
        if len(self.explorer_group) == 0:
            print("the number of veh is zero")
            return
        # all surfaces
        self.screen = None
        self.interface = None
        self.sidebar = None
        """"all parameters about training"""
        self.dir = dir()
        self.action_number = self.dir.action_num()
        self.smart_controller = None

    def init(self):
        self.layout.init()
        for explorer in self.explorer_group:
            explorer.init()
        """observations"""

    def run_game(self, control_pattern="manual", smart_controller=None):
        pygame.init()
        pygame.display.set_caption('multiAGV World')
        self.control_pattern = control_pattern  # 0: "train_NN", 1: "use_NN", 2: "A_star", 3: "auto", 4: "manual"
        self.explorer_group[0].create_explorer()  # 创建第一辆veh实体，后续车辆需要在画面刷新后创建
        """"--screen--"""
        # screen
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.screen.fill(self.color_box.GRAY_Color)
        # screen display
        self.refresh_screen(self.explorer_group[0])

        self.clock = pygame.time.Clock()
        running_time = 0

        if self.control_pattern == "intelligent":
            """训练开始"""
            self.smart_controller = smart_controller
            while True:
                running_time += 1
                # print("running_time", running_time)
                self.clock.tick(self.FPS)
                """standard code: exit game"""
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                """mode=intelligent"""
                """"
                1.统一采集全场信息
                2.逐个进行动作选择和执行
                """
                # update interface
                self.create_interface()
                # update sidebar
                self.create_sidebar()
                for explorer in self.explorer_group:
                    if explorer.has_created == False:
                        break
                    if explorer.all_assigned == True:
                        agv_position = self.position_rectify(explorer.current_place[0], explorer.current_place[1])
                        agv_image = pygame.image.load(explorer.icon_path)
                        agv_image = pygame.transform.scale(agv_image, (
                        self.cell_width * self.AGV_icon_scale, self.cell_width * self.AGV_icon_scale))  # 图像缩放
                        self.interface.blit(agv_image, agv_position)
                        continue
                    if explorer.Working:
                        if explorer.time_counting == explorer.Working_Time[explorer.working_type]:
                            explorer.continue_working()
                            if self.layout.task_finished:
                                return running_time
                            if explorer.all_assigned == True:
                                agv_position = self.position_rectify(explorer.current_place[0],
                                                                     explorer.current_place[1])
                                agv_image = pygame.image.load(explorer.icon_path)
                                agv_image = pygame.transform.scale(agv_image, (
                                    self.cell_width * self.AGV_icon_scale,
                                    self.cell_width * self.AGV_icon_scale))  # 图像缩放
                                self.interface.blit(agv_image, agv_position)
                                continue
                        else:
                            explorer.time_counting += 1
                            agv_position = self.position_rectify(explorer.current_place[0], explorer.current_place[1])
                            agv_image = pygame.image.load(explorer.icon_path)
                            agv_image = pygame.transform.scale(agv_image, (
                                self.cell_width * self.AGV_icon_scale, self.cell_width * self.AGV_icon_scale))  # 图像缩放
                            self.interface.blit(agv_image, agv_position)
                            continue

                    # input_action = self.explorer.find_path_astar()  # through strategy
                    all_info = self.create_info()  # all_info=[layout, [veh1_details], [veh2_details]...]
                    input_action = self.smart_controller.choose_action(all_info, explorer.explorer_name)  # get action

                    """execute action"""
                    reward, is_end, all_info_ = explorer.execute_action(input_action, all_info)
                    agv_position = self.position_rectify(explorer.current_place[0], explorer.current_place[1])
                    # add AGV to screen
                    agv_image = pygame.image.load(explorer.icon_path)
                    agv_image = pygame.transform.scale(agv_image, (
                    self.cell_width * self.AGV_icon_scale, self.cell_width * self.AGV_icon_scale))  # 图像缩放
                    self.interface.blit(agv_image, agv_position)
                    # 需要对is_end进行矫正
                    if self.layout.task_finished:
                        is_end = True
                    all_info = self.create_info()  # all_info=[layout, [veh1_details], [veh2_details]...]
                    self.smart_controller.store_info(all_info_, reward, is_end, explorer.explorer_name)
                    if is_end:
                        print("running_time", running_time)
                        return running_time
                """查看是否可以创建新的veh（初始位置空出）"""
                flags = self.check_new_veh()
                if flags == 0:
                    pass
                else:
                    # 创建了一辆新车
                    explorer = self.explorer_group[flags]
                    agv_position = self.position_rectify(explorer.current_place[0], explorer.current_place[1])
                    agv_image = pygame.image.load(explorer.icon_path)
                    agv_image = pygame.transform.scale(agv_image, (
                    self.cell_width * self.AGV_icon_scale, self.cell_width * self.AGV_icon_scale))  # 图像缩放
                    self.interface.blit(agv_image, agv_position)

                # update screen
                self.screen.blit(self.interface, (self.interface_start_x, self.interface_start_y))
                self.screen.blit(self.sidebar, (self.sidebar_start_x, self.sidebar_start_y))

                pygame.display.flip()  # 更新屏幕内容
        else:
            if self.control_pattern == "manual":
                self.run_mode_manual()
            if self.control_pattern in ["A_star", "auto"]:
                self.run_mode_auto()

    def run_mode_manual(self):
        print("Control by manual mode")
        if len(self.explorer_group) > 1:
            print("manual mode can only control one AGV")
            return
        while True:
            input_action = ""
            self.clock.tick(self.FPS)
            explorer = self.explorer_group[0]
            """"judge if explorer is working"""
            if explorer.Working:
                if explorer.time_counting == explorer.Working_Time[explorer.working_type]:
                    explorer.continue_working()
                    self.refresh_screen(explorer)
                else:
                    explorer.time_counting += 1
                    continue
            """recieve action"""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        input_action = self.dir.value_str[0]
                    if event.key == pygame.K_DOWN:
                        input_action = self.dir.value_str[2]
                    if event.key == pygame.K_LEFT:
                        input_action = self.dir.value_str[3]
                    if event.key == pygame.K_RIGHT:
                        input_action = self.dir.value_str[1]
            """execute action"""
            if input_action != "":
                explorer.execute_action(input_action)
                self.refresh_screen(explorer)

    def run_mode_auto(self):
        print("Control by auto mode")
        while True:
            input_action = ""
            self.clock.tick(self.FPS)
            """standard code: exit game"""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            self.create_interface()  # update interface
            self.create_sidebar()   # update sidebar

            for explorer in self.explorer_group:
                if not explorer.has_created:
                    break
                if explorer.Working:
                    if explorer.time_counting == explorer.Working_Time[explorer.working_type]:
                        explorer.continue_working()
                        if self.layout.task_finished:
                            return
                        if explorer.all_assigned:
                            self.patch_agv_icon(explorer)
                            continue
                    else:
                        explorer.time_counting += 1
                        self.patch_agv_icon(explorer)
                        continue

                if not self.layout.task_finished:
                    # input_action = random.randint(0, 3)  # random
                    input_action = explorer.find_path_astar(self.explorer_group)  # through strategy
                """execute action"""
                if input_action != "":
                    explorer.execute_action(input_action)
                    self.patch_agv_icon(explorer)

            """查看是否可以创建新的veh（初始位置空出）"""
            flags = self.check_new_veh()
            if flags != 0:
                explorer = self.explorer_group[flags]
                self.patch_agv_icon(explorer)

            self.screen.blit(self.interface, (self.interface_start_x, self.interface_start_y))
            self.screen.blit(self.sidebar, (self.sidebar_start_x, self.sidebar_start_y))
            pygame.display.flip()  # 更新屏幕内容

    def refresh_screen(self, explorer):
        self.create_interface()  # update interface
        self.patch_agv_icon(explorer)  # update AGV
        self.create_sidebar()  # update sidebar
        # update screen
        self.screen.blit(self.interface, (self.interface_start_x, self.interface_start_y))
        self.screen.blit(self.sidebar, (self.sidebar_start_x, self.sidebar_start_y))
        pygame.display.flip()  # 更新屏幕内容

    def patch_agv_icon(self, explore_group):
        if not isinstance(explore_group, list):
            explore_group = [explore_group]
        for explore in explore_group:
            agv_image = pygame.image.load(explore.icon_path)
            agv_image = pygame.transform.scale(agv_image, (
            self.cell_width * self.AGV_icon_scale, self.cell_width * self.AGV_icon_scale))  # 图像缩放
            agv_position = self.position_rectify(explore.current_place[0], explore.current_place[1])
            self.interface.blit(agv_image, agv_position)

    def create_interface(self):
        # interface
        self.interface = pygame.Surface((self.interface_width, self.interface_height), flags=pygame.HWSURFACE)
        self.interface.fill(color=self.color_box.WHITE_COLOR)
        # draw blocks
        for y_dim in range(self.y_width):
            for x_dim in range(self.x_width):
                pygame.draw.rect(self.interface, self.color_box.BLACK_COLOR, (
                x_dim * (self.cell_width - self.line_width), y_dim * (self.cell_width - self.line_width),
                self.cell_width, self.cell_width), self.line_width)
                # draw picking_station and storage_station
                if (x_dim + 1, y_dim + 1) in self.layout.picking_station_list:
                    self.draw_block(self.interface, self.color_box.BLACK_COLOR, x_dim, y_dim)
                    # img = pygame.image.load("icons/cart.png")
                    # img = pygame.transform.scale(img, (self.cell_width*self.AGV_icon_scale, self.cell_width*self.AGV_icon_scale))
                    # self.interface.blit(img, self.position_rectify(x_dim+1, y_dim+1))
                if (x_dim + 1, y_dim + 1) in self.layout.storage_station_list:
                    if self.layout.layout[y_dim][x_dim] == 1.8:
                        self.draw_block(self.interface, self.color_box.PINK_COLOR, x_dim, y_dim)
                    elif self.layout.layout[y_dim][x_dim] == 1.3:
                        self.draw_block(self.interface, self.color_box.GREEN_COLOR, x_dim, y_dim)
                    else:
                        self.draw_block(self.interface, self.color_box.RED_COLOR, x_dim, y_dim)
                # draw axis value
                if x_dim == 0:
                    self.draw_scale(self.screen, float(y_dim), "y")
                if y_dim == 0:
                    self.draw_scale(self.screen, float(x_dim), "x")
        # self.draw_scale(self.screen, float(self.x_width), "x")
        # self.draw_scale(self.screen, float(self.y_width), "y")

    def create_sidebar(self):
        """"--sidebar--"""
        # sidebar
        self.sidebar = pygame.Surface((self.sidebar_width, self.sidebar_height), flags=pygame.HWSURFACE)
        self.sidebar.fill(color=self.color_box.GRAY_Color)
        # title
        font_title = pygame.font.SysFont("Times New Roman", 30)
        title = font_title.render(str("RMFS World"), True, self.color_box.BLACK_COLOR)
        title_rect = title.get_rect()
        self.sidebar.blit(title, (self.sidebar_width / 2 - title_rect.width / 2, self.sidebar_height / 15))
        # title
        font_agv = pygame.font.SysFont("Times New Roman", 15)
        t_l = font_agv.render(str("target_: " + str(self.explorer_group[0].target_position)), True,
                              self.color_box.BLACK_COLOR)  # target location
        c_l = font_agv.render(str("current: " + str(self.explorer_group[0].current_place)), True,
                              self.color_box.BLACK_COLOR)  # current location
        l_l = font_agv.render(str("last___: " + str(self.explorer_group[0].last_place)), True,
                              self.color_box.BLACK_COLOR)  # last location
        act = font_agv.render(str("action_: " + str(self.explorer_group[0].action_str)), True,
                              self.color_box.BLACK_COLOR)  # action
        r_s = font_agv.render(str("state__: " + str(self.explorer_group[0].running_state)), True,
                              self.color_box.BLACK_COLOR)  # running_state
        self.sidebar.blit(t_l, (20, self.sidebar_height / 3))
        self.sidebar.blit(c_l, (20, self.sidebar_height / 3 + 20))
        self.sidebar.blit(l_l, (20, self.sidebar_height / 3 + 40))
        self.sidebar.blit(act, (20, self.sidebar_height / 3 + 60))
        self.sidebar.blit(r_s, (20, self.sidebar_height / 3 + 80))
        # title
        font_author = pygame.font.SysFont("Times New Roman", 15)
        author_detail = font_author.render(str("Author: Stone"), True, self.color_box.BLACK_COLOR)
        self.sidebar.blit(author_detail, (20, 5 * self.sidebar_height / 6))

    def draw_scale(self, screen, value, axis):
        font = pygame.font.SysFont("Times New Roman", 12)
        rect = font.render(str(value + 1), True, self.color_box.BLACK_COLOR)
        if axis == "x":
            screen.blit(rect, (value * (
                        self.cell_width - self.line_width) + self.interface_start_x - rect.get_width() / 2 + self.cell_width / 2,
                               self.border_width / 3))
        elif axis == "y":
            screen.blit(rect, (self.border_width / 4, value * (
                        self.cell_width - self.line_width) + self.interface_start_y - rect.get_height() / 2 + self.cell_width / 2))

    def draw_block(self, interface, color, x_dim, y_dim):
        pygame.draw.rect(interface, color, (x_dim * (self.cell_width - self.line_width) + self.line_width,
                                            y_dim * (self.cell_width - self.line_width) + self.line_width,
                                            self.cell_width - self.line_width,
                                            self.cell_width - self.line_width))

    def position_rectify(self, x_dim, y_dim):
        x_position = (x_dim - 1) * (self.cell_width - self.line_width) + self.line_width
        y_position = (y_dim - 1) * (self.cell_width - self.line_width) + self.line_width
        position = (x_position, y_position)
        return position

    """utils for reinforcement learning"""

    def create_info(self):
        layout = self.layout.layout_original
        all_info = [layout]
        for explorer in self.explorer_group:
            if explorer.has_created:
                one_explorer = [explorer.explorer_name, explorer.current_place, explorer.target_position,
                                explorer.loaded]
                all_info.append(one_explorer)
            else:
                break
        # print("all_info", all_info)
        return all_info

    def check_new_veh(self):
        init_pos_occupy = False
        flags = 0
        for explore_num in range(len(self.explorer_group)):
            if self.explorer_group[explore_num].has_created:
                if self.explorer_group[explore_num].current_place == [1, 1]:
                    init_pos_occupy = True
            else:  # 所有被创建的车辆都已经检查过了
                if init_pos_occupy == False:
                    self.explorer_group[explore_num].create_explorer()
                    flags = explore_num
                    break
        return flags
