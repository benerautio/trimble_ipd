#from turtle import TurtleScreenBase
from trimble_ipd.pnp_modular import pipeline
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import cv2
import os
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
import transforms3d



CAL_FILE = 'cam_cal.yaml'
SAVE_PATH = '/home'
USER = ''
CAL_PATH = os.path.join(SAVE_PATH, USER,CAL_FILE)

class PoseEstimator(Node):
    def __init__(self):
        super().__init__('ipd_pose_estimator')
        self.subscription = self.create_subscription(
            Image,
            'csi_raw',
            self.img_callback,
            10)
        self.subscription
        self.bridge = CvBridge()
        self.pipeline = pipeline()

        self.br = TransformBroadcaster(self)

        self.pipeline.tryLink()
        self.pipeline.getCalibration()
    
    def img_callback(self, CsiImg):
        self.get_logger().info('img callback triggered')
        try:
            #or mono8 or gray8
            cv_img = self.bridge.imgmsg_to_cv2(CsiImg, '8UC1')
        except CvBridgeError as e:
            print(e)
        print(cv_img)
        ret, euler, tvec = self.pipeline.Find_Pose(cv_img)
        print("ret pnp: " + str(ret))
        if ret:
            print("DEBUG: R: " +str(euler)+"T: "+str(tvec))
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = 'MarkerTree'
            t.child_frame_id = 'Camera'
            t.transform.translation.x = tvec[0]
            t.transform.translation.y = tvec[1]
            t.transform.translation.z = tvec[2]
            q = transforms3d.euler.euler2quat(euler[0],euler[1],euler[2])
            t.transform.rotation.x = q[0]
            t.transform.rotation.y = q[1]
            t.transform.rotation.z = q[2]
            t.transform.rotation.w = q[3]

            self.br.sendTransform(t)

def main():
    rclpy.init()
    node = PoseEstimator()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    rclpy.shutdown()
        

