import launch
from launch.actions import DeclareLaunchArgument
from launch.conditions import LaunchConfigurationEquals
from launch.conditions import LaunchConfigurationNotEquals
from launch_ros.actions import ComposableNodeContainer
from launch_ros.actions import LoadComposableNodes
from launch_ros.actions import Node
from launch_ros.descriptions import ComposableNode
from launch.substitutions import LaunchConfiguration

from pathlib import Path

project_path = Path("workspaces/Slam/SLAM")

right_camera_config_path = project_path / "CameraCalibration" / "right_camera.yaml"
left_camera_config_path = project_path / "CameraCalibration" / "left_camera.yaml"
image_proc_rectify_config_path = project_path / "ImageProcRectify" / "image_proc_rectify_parameters.yaml"

####################################################
###################### TO DO  ######################
#################################################### 

def generate_launch_description():
    
    left_namespace = 'stereo/left',
    right_namespace = 'stereo/right',  


    ####################################################
    ################# USB CAMERA NODES #################
    #################################################### 

    #Right Usb Camera
    usb_cam_right = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        namespace=right_namespace,
        output='screen',
        parameters=[right_camera_config_path],
     
    )

    #Left Usb Camera
    usb_cam_left = Node(
        package='usb_cam',
        executable='usb_cam_node_exe',
        namespace=left_namespace,
        output='screen',
        parameters=[left_camera_config_path],
      
    )

    ####################################################
    ################# IMAGE PROC NODES #################
    #################################################### 

    #Right Camera Processing
    composable_nodes = [
        ComposableNode(
            package='image_proc',
            plugin='image_proc::DebayerNode',
            name='debayer_node',
            namespace= right_namespace,
            parameters=[{'debayer' : 0
                         
                         }],
           
        ),
    #Left Camera Processing
        ComposableNode(
            package='image_proc',
            plugin='image_proc::DebayerNode',
            name='debayer_node',
            namespace= left_namespace,
            parameters=[{'debayer' : 0
                
                        }],
       
        ),
        
    ]


    #Container Generation
    arg_container = DeclareLaunchArgument(
        name = 'container', default_value='',
        description=(
            'Name of an existing node container to load launched nodes into. '
            'If unset, a new container will be created'
        )
    )

      # If an existing container is not provided, start a container and load nodes into it
    image_processing_container = ComposableNodeContainer(
        condition=LaunchConfigurationEquals('container', ''),
        name='image_proc_container',
        namespace="image_proc_container",
        package='rclcpp_components',
        executable='component_container',
        composable_node_descriptions=composable_nodes,
        output='screen'
    )

    # If an existing container name is provided, load composable nodes into it
    # This will block until a container with the provided name is available and nodes are loaded
    load_composable_nodes = LoadComposableNodes(
        condition=LaunchConfigurationNotEquals('container', ''),
        composable_node_descriptions=composable_nodes,
        target_container=LaunchConfiguration('container'),
    )

    ####################################################
    ################## TRANSFORM NODES #################
    #################################################### 

    #Camera base link to odom frame
    camera_base_tf = Node(
        package = 'tf2_ros',
        executable='static_transform_publisher',
        output= 'screen',
        arguments = [
            "--x", "0",
            "--y", "0",
            "--z", "0",
            "--roll", "0",
            "--pitch", "0",
            "--yaw", "0",
            "--frame-id", "odom",
            "--child-frame-id", "camera_link"

             ]
        )

    #Right camera to base link
    right_base_tf = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            output='screen',
            arguments=[
                "--x", ".040",
                "--y", "0.029",
                "--z", "0",
                "--roll", "0",
                "--pitch", "0",
                "--yaw", "0",
                "--frame-id", "camera_link",
                "--child-frame-id", "camera2"
                ]
        )
    
    #Left camera to base link
    left_base_tf = Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            output='screen',
            arguments=[
                "--x", "-.040",
                "--y", ".029",
                "--z", "0",
                "--roll", "0",
                "--pitch", "0",
                "--yaw", "0",
                "--frame-id", "camera_link",
                "--child-frame-id", "camera1"
                ]
        )
    
    return launch.LaunchDescription([
        usb_cam_right,
        usb_cam_left,
        camera_base_tf,
        left_base_tf,
        right_base_tf,
        arg_container,
        image_processing_container,
        load_composable_nodes
    ])
