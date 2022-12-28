import copy
import sys
import utils.astar as astar
from utils.utils import Direction as dir
import os
sys.path.append(os.path.dirname(__file__))


class Explorer:
    def __init__(self, layout, veh_name="veh1", icon_name="veh1"):
        self.layout = layout
        """--------------init attributes--------------"""
        """work time """
        # 从储位取货架,在拣货台放货架,在储位放货架 {"GET": 5, "PUT": 5, "RET": 5}
        self.Working_Time = {0: 5, 1: 5, 2: 5}
        self.Working = False
        self.working_type = 0
        self.time_counting = 0
        """basic information"""
        self.action_value = 0
        self.action_str = "UP"
        self.current_place = [1, 1]
        self.target_position = [1, 1]
        self.last_place = [1, 1]
        self.icon_path = "icons/"+icon_name+".png"
        self.dir = dir()
        self.task_order = 0
        self.task_stage = 0
        self.running_state = "Normal"
        self.loaded = False
        self.explorer_name = veh_name
        self.has_created = False
        self.all_assigned = False
        """"special parameters"""
        self.always_loaded = False
        self.always_empty = False
        """"init"""
        self.init()

    def init(self):
        self.last_place = [1, 1]
        self.current_place = [1, 1]
        self.task_order = 0
        self.task_stage = 0
        self.running_state = "Normal"
        self.loaded = False
        self.has_created = False
        self.all_assigned = False

        self.Working = False
        self.working_type = 0
        self.time_counting = 0

    def create_explorer(self):
        self.has_created = True
        self.get_task()

    def get_task(self):
        """"has veh created"""
        if not self.has_created:
            # veh entity has not been build
            return

        """judge if has unassigned tasks"""
        if len(self.layout.task_list) == len(self.layout.task_arrangement[0]) and self.task_stage == 0:
            self.all_assigned = True  # 所有任务已经分配
            # 判断任务是否全部完成
            if len(self.layout.task_list) == sum(self.layout.task_arrangement[2]):
                self.layout.task_finished = True
                self.running_state = "AllTaskFinished"
            return

        """"assign task"""
        if self.task_stage == 0:
            # 获取任务编号，将以分配的任务进行添加
            self.task_order = len(self.layout.task_arrangement[0])
            self.layout.task_arrangement[0].append(self.task_order)
            self.layout.task_arrangement[1].append(self.explorer_name)
            self.layout.task_arrangement[2].append(0)

            self.target_position = [self.layout.task_list[self.task_order][0], self.layout.task_list[self.task_order][1]]
            self.layout.change_layout(self.layout.task_list[self.task_order][0] - 1,
                                      self.layout.task_list[self.task_order][1] - 1, 1.3)
        elif self.task_stage == 1:
            self.target_position = [self.layout.task_list[self.task_order][2], self.layout.task_list[self.task_order][3]]
        elif self.task_stage == 2:
            self.target_position = [self.layout.task_list[self.task_order][0], self.layout.task_list[self.task_order][1]]
        self.load_condition(self.task_stage)

    def load_condition(self, task_stage):
        # change by parameter
        if self.always_loaded:
            self.loaded = True
            return
        if self.always_empty:
            self.loaded = False
            return
        # change by task_stage
        if task_stage == 0:
            self.loaded = False
        elif task_stage == 1:
            self.loaded = True
        elif task_stage == 2:
            self.loaded = True

    def action_format(self, input_action):
        """transfer action format to int"""
        if isinstance(input_action, str):
            action_value = self.dir.action_str_value(input_action)
        else:
            action_value = input_action
        action_str = self.dir.action_value_str(action_value)
        return action_value, action_str

    def action_logical(self):
        action_value_dict = {0: [0, -1], 1: [1, 0], 2: [0, 1], 3: [-1, 0], 4: [0, 0]}
        return action_value_dict[self.action_value]

    def execute_action(self, input_action, all_info=[]):
        # execute action
        self.last_place = copy.deepcopy(self.current_place)
        all_info_ = copy.deepcopy(all_info)  # 执行动作之后的状态（错误的动作不会被矫正）
        self.action_value, self.action_str = self.action_format(input_action)
        action_result = self.action_logical()
        self.current_place[0] = self.current_place[0] + action_result[0]
        self.current_place[1] = self.current_place[1] + action_result[1]
        real_current_place = copy.deepcopy(self.current_place)
        # check action result
        if self.action_value == 4:  # 原地不动
            reward, is_end = 0, False
        else:
            reward, is_end, remain_pos = self.check_state(all_info)  # all_info is a list including all vehs' info
            for i in range(1, len(all_info_)):
                """judge whether to remain former current_place in all_info"""
                one_veh = all_info_[i]
                veh_name_, current_place_ = one_veh[0], one_veh[1]
                if veh_name_ == self.explorer_name:  # target_veh
                    if remain_pos:
                        one_veh[1] = copy.deepcopy(real_current_place)
                    else:
                        one_veh[1] = copy.deepcopy(self.current_place)
                    break
        return reward, is_end, all_info_

    def check_state(self, all_info):
        """Legitimacy test"""
        reward, is_end, remain_pos = 0, False, False
        self.running_state = "Normal"
        """out of boundary"""
        if self.current_place[0] < 1 or self.current_place[1] < 1 or \
                self.current_place[0] > self.layout.scene_x_width or self.current_place[1] > self.layout.scene_y_width:
            self.running_state = "illegal action"
            self.current_place = copy.deepcopy(self.last_place)
            reward, is_end, remain_pos = -1, True, False
            print("out of boundary")
            return reward, is_end, remain_pos

        """"hit storage position or picking station """
        # hit storage position
        if (self.current_place[0], self.current_place[1]) in self.layout.storage_station_list and \
                self.loaded is True and self.current_place != self.target_position:
            self.running_state = "hit s_station"
            self.current_place = copy.deepcopy(self.last_place)
            reward, is_end, remain_pos = -1, True, True  # 这个remain_pos可以进行更多研究
            print("hit s_station")
            return reward, is_end, remain_pos
        # hit picking position
        if (self.current_place[0], self.current_place[1]) in self.layout.picking_station_list and \
                self.current_place != self.target_position:  # no need to check load condition
            self.running_state = "hit p_station"
            self.current_place = copy.deepcopy(self.last_place)
            reward, is_end, remain_pos = -1, True, True
            print("hit p_station")
            return reward, is_end, remain_pos
        """"hit other veh """
        for i in range(1, len(all_info)):  # the first position of info is layout
            one_veh = all_info[i]
            veh_name_, current_place_ = one_veh[0], one_veh[1]
            if veh_name_ == self.explorer_name:  # target_veh
                continue
            else:
                if self.current_place == current_place_:
                    # print("vehicle collied")
                    reward, is_end, remain_pos = -1, True, True
                    print("hit other veh")
                    return reward, is_end, remain_pos

        """reach target place"""
        if self.current_place[0] == self.target_position[0] and self.current_place[1] == self.target_position[1]:
            self.running_state = "target reached"

            self.Working = True
            self.working_type = self.task_stage
            self.time_counting = 0
            reward, is_end = 1, False

        return reward, is_end, remain_pos

    def continue_working(self):
        self.Working = False
        self.time_counting = 0

        self.task_stage = self.task_stage+1
        if self.task_stage == 3:
            self.layout.change_layout(self.layout.task_list[self.task_order][0] - 1,
                                      self.layout.task_list[self.task_order][1] - 1, 1.8)
            self.task_stage = 0
            self.layout.task_arrangement[2][self.task_order] = 1
        self.get_task()

    def valid_matrix(self, explorer_group):
        valid_matrix = []
        valid_matrix_one = []
        value = 0
        for j in range(len(self.layout.layout_original)):
            for i in range(len(self.layout.layout_original[0])):
                cell_value = self.layout.layout_original[j][i]
                if cell_value == 0:
                    value = 1
                elif cell_value == 1:
                    if self.loaded:  # 目标储位依然允许到达
                        value = 0
                    else:
                        value = 1
                elif cell_value == 2:
                    value = 0
                if self.target_position[0] - 1 == i and self.target_position[1] - 1 == j:
                    value = 1
                valid_matrix_one.append(value)
            valid_matrix.append(valid_matrix_one)
            valid_matrix_one = []
        # adjust according to the position of other AGV
        if explorer_group is not None:
            if len(explorer_group) > 1:
                for explorer in explorer_group:
                    valid_matrix[explorer.current_place[1] - 1][explorer.current_place[0]-1] = 0
            # valid_matrix[self.current_place[1]-1][self.current_place[0]-1] = 0
        # print("valid_matrix", valid_matrix)
        return valid_matrix

    def find_path_astar(self, explorer_group=None):
        path_founder = astar.FindPathAstar(self.valid_matrix(explorer_group),
                                           (self.current_place[0]-1, self.current_place[1]-1),
                                           (self.target_position[0]-1, self.target_position[1]-1))
        find_target, path_list, path_map, action_list = path_founder.run_astar_method()
        if find_target == False or len(action_list) == 0:
            action_str = "STOP"
        else:
            action_str = action_list[0]
        # print(action_list)
        return action_str




