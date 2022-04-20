import math

import rclpy
from rclpy.node import Node

from tf2_ros import LookupException, ConnectivityException, ExtrapolationException, TransformException
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener
from geometry_msgs.msg import PoseStamped
from rclpy.duration import Duration

class FrameListener(Node):

    def __init__(self):
        super().__init__('camera_tf2_frame_listener')

        self.target_frame = 'MarkerTree'
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.pose_publisher = self.create_publisher(PoseStamped, 'MarkerTreePose', 10)
        self.timer = self.create_timer(0.05, self.on_timer)

    def on_timer(self):
        from_frame_rel = self.target_frame
        to_frame_rel = 'Camera'

        try:
            now = rclpy.time.Time()
            trans = self.tf_buffer.lookup_transform(
                to_frame_rel,
                from_frame_rel,
                now,
                timeout=Duration(seconds=1.0))
        except TransformException as ex:
            self.get_logger().info(
                f'couldnt tf {to_frame_rel} to {from_frame_rel}: {ex}')
            return
            
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.pose.position.x = trans.transform.translation.x
        msg.pose.position.y = trans.transform.translation.y
        msg.pose.position.z = trans.transform.translation.z
        msg.pose.orientation.x = trans.transform.rotation.x
        msg.pose.orientation.y = trans.transform.rotation.y
        msg.pose.orientation.z = trans.transform.rotation.z
        msg.pose.orientation.w = trans.transform.rotation.w
        self.pose_publisher.publish(msg)
        self.get_logger().info("Publishing pose")

def main():
    rclpy.init()
    node = FrameListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()