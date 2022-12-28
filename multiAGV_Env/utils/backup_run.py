# 运行RMFS系统
# from RMFS import RMFSModel as rmfs
from components.Layout import Layout  # layout
from components.Explorer import Explorer  # explorer
from components.Scene import Scene  # Scene
# from AGDQN_Agent import DQN_Rule_Controller as rmfs_controller_DQN
# from DQN_RMFS_TwoVeh import DQN_Rule_Controller as rmfs_controller_DQN

def main():
    """--------------create multiAGV object--------------"""
    """ 1.create layout """
    ss_x_width, ss_y_width, ss_x_num, ss_y_num, ps_num = 3, 2, 2, 2, 1
    layout_list = None
    task_list = None
    layout = Layout(storage_station_x_width=ss_x_width, storage_station_y_width=ss_y_width,
                    storage_station_x_num=ss_x_num, storage_station_y_num=ss_y_num,
                    picking_station_number=ps_num, layout_list=layout_list, task_list=task_list)
    """ 2. create vehicles """
    explorer_num = 3
    explorer_group = []
    for i in range(explorer_num):
        veh_name = "veh" + str(i + 1)
        explorer = Explorer(layout, veh_name=veh_name, icon_name=veh_name)
        explorer_group.append(explorer)
    """ 3. create scene """
    multi_agv_scene = Scene(layout, explorer_group)

    """--------------choose different controller--------------"""
    control_type = {0: "train_NN", 1: "use_NN", 2: "A_star", 3: "auto", 4: "manual"}
    control_mode = 3

    """--------------run model--------------"""
    if control_mode in [2, 3, 4]:
        multi_agv_scene.run_game(control_pattern=control_type[control_mode])
    else:
        map_xdim = layout.scene_x_width
        map_ydim = layout.scene_y_width
        max_task = len(layout.storage_station_list)
        rmfs_ctrl = rmfs_controller_DQN(multi_agv_scene, map_xdim=map_xdim, map_ydim=map_ydim, max_task=max_task,
                                        control_mode=control_mode, state_number=3, matrix_padding=0)
        rmfs_ctrl.model_run()


if __name__ == '__main__':
    """
    The main function called when RMFS.py is run
    from the command line:

    > python RMFS.py

    See the usage string for more details.

    > python RMFS.py --help
    """

    # args = readCommand(sys.argv[1:])  # Get game components based on input
    main()


    # layout_list = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                [0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0],
    #                [0, 1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                [0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    #                [0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0],
    #                [0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0],
    #                [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    #                [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    #                [0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0],
    #                [0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #                [0, 0, 0, 2, 0, 0, 0, 0, 0, 2, 0, 0, 0],
    #                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

    # task_list = [(9, 2, 4, 13), (4, 3, 10, 13), (11, 8, 4, 13), (12, 2, 4, 13), (2, 2, 10, 13), (8, 6, 10, 13), (
    # 11, 11, 10, 13), (12, 9, 4, 13), (3, 8, 4, 13), (3, 11, 4, 13), (9, 10, 4, 13), (10, 3, 4, 13), (6, 11, 10, 13), (
    #                3, 9, 10, 13), (12, 6, 10, 13), (9, 8, 4, 13), (2, 3, 10, 13), (12, 5, 4, 13), (9, 11, 4, 13), (
    #                8, 11, 4, 13), (5, 2, 10, 13), (2, 6, 10, 13), (11, 5, 10, 13), (2, 5, 4, 13), (5, 10, 4, 13), (
    #                11, 9, 4, 13), (5, 8, 4, 13), (10, 2, 4, 13), (4, 2, 4, 13), (5, 3, 4, 13), (2, 9, 10, 13), (
    #                11, 3, 10, 13), (11, 2, 4, 13), (3, 5, 4, 13), (6, 2, 4, 13), (3, 2, 4, 13), (8, 8, 10, 13), (
    #                2, 8, 4, 13), (6, 8, 4, 13), (5, 7, 4, 13), (8, 7, 4, 13), (6, 6, 10, 13), (8, 2, 4, 13), (
    #                6, 9, 4, 13), (5, 11, 10, 13), (12, 3, 4, 13), (6, 10, 4, 13), (12, 8, 10, 13), (8, 10, 10, 13), (
    #                9, 9, 4, 13), (4, 5, 10, 13), (11, 6, 4, 13), (3, 6, 4, 13), (10, 5, 10, 13), (8, 9, 10, 13), (
    #                5, 9, 4, 13), (3, 3, 10, 13), (9, 7, 4, 13), (2, 11, 10, 13), (6, 7, 4, 13), (9, 3, 4, 13), (
    #                12, 11, 4, 13)]





