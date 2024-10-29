import os

from ament_index_python.packages import get_package_share_directory


from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    package_name='apricotka-robot-car'
    ros_gz_sim = get_package_share_directory('ros_gz_sim')

    x_pose = LaunchConfiguration('x_pose', default='-1.0')
    y_pose = LaunchConfiguration('y_pose', default='1.5')
    z_pose = LaunchConfiguration('z_pose', default='0.5')
    
    set_env_vars_resources = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.join(get_package_share_directory(package_name),
                     'worlds',
                     'models'))

    world = os.path.join(
        get_package_share_directory(package_name),
        'worlds',
        'empty.world'
    )

    gzserver_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': ['-r -s -v4 ', world], 'on_exit_shutdown': 'true'}.items()
    )
    gzclient_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(ros_gz_sim, 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={'gz_args': '-g -v4 '}.items()
    )
    rsp_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(package_name),'launch','rsp.launch.py')]
        ),
        launch_arguments={'use_sim_time': 'true', 'use_ros2_control': 'true'}.items()
    )
    spawn_robot_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(package_name),'launch', 'spawn_robot.launch.py')
        ),
        launch_arguments={
            'x_pose': x_pose,
            'y_pose': y_pose,
            'z_pose': z_pose
        }.items()
    )

    load_joint_state_broadcaster = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_broadcaster'],
        output='screen'
    )

    load_diff_drive_controller = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'diff_drive_controller'],
        output='screen'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', get_package_share_directory(package_name) + '/config/view_bot.rviz'],
        output='screen'
    )

    # Launch them all!
    ld = LaunchDescription()

    ld.add_action(set_env_vars_resources)
    ld.add_action(gzserver_cmd)
    ld.add_action(gzclient_cmd)
    ld.add_action(rsp_cmd)
    ld.add_action(spawn_robot_cmd)
    ld.add_action(load_joint_state_broadcaster)
    ld.add_action(load_diff_drive_controller)
    ld.add_action(rviz)
    
    return ld