from numpy import rate
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
from pipeline import gstreamer_pipeline

class CsiPublisher(Node):

    def __init__(self):
        camcfg, rate = gstreamer_pipeline()
        super.__init__('csi_raw_publisher')
        self.publisher = self.create_publisher(Image, 'csi_raw', 10)
        self.timer_period = 1.0/rate
        self.timer = self.create_timer(self.timer_period, self.timer_callback)
        # Add error checking here for if the camera cannot open the stream!
        self.cap = cv2.VideoCapture((camcfg), cv2.CAP_GSTREAMER)
        self.br = CvBridge()

    def timer_callback(self):
        ret, frame = self.cap.read()

        if ret == True:
            self.publisher.publish(self.br.cv2_to_imgmsg(frame))
        self.get_logger().info('Publish CSI raw frame')

def main(args=None):
    rclpy.init(arg=args)

    csi_raw_pub = CsiPublisher()
    rclpy.spin(csi_raw_pub)

    csi_raw_pub.destroy_node()
    rclpy.shutdown

if __name__ == '__main__':
    main()


