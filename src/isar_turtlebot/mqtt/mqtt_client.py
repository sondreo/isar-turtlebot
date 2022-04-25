import logging
import os
import re
from logging import Logger
from time import sleep
from typing import Dict

from isar_turtlebot.config import config
from isar_turtlebot.ros_bridge.ros_bridge import RosBridge
from isar_turtlebot.utilities.inspection_pose import get_distance
from isar_turtlebot.utilities.pose_message import decode_pose_message
from paho.mqtt.client import Client
from robot_interface.models.geometry.frame import Frame
from robot_interface.models.geometry.pose import Pose
from robot_interface.models.geometry.position import Position


class MqttClient:
    def __init__(
        self,
        bridge: RosBridge,
        host: str = "localhost",  # config.get("service_connections", "mqtt_host"),
        port: int = 1883,  # config.getint("service_connections", "mqtt_port"),
    ) -> None:

        self.logger: Logger = logging.getLogger("robot")

        username: str = (
            "mosquitto"  # config.get("service_connections", "mqtt_username")
        )
        password: str = "default"  # ""

        try:
            password = os.environ["MQTT_PASSWORD"]
        except KeyError:
            pass

        self.bridge = bridge
        self.client = Client()

        self.client.username_pw_set(username=username, password=password)
        self.client.connect(host=host, port=port, keepalive=60)

    def publish_battery_state(self) -> None:
        pass

    def publish_distance_to_goal(self) -> None:
        published_task: Dict = self.bridge.execute_task.get_value()

        try:
            goal_pose_message: dict = published_task["goal"]["target_pose"]["pose"]

            goal_position: Position = Position(
                x=goal_pose_message["position"]["x"],
                y=goal_pose_message["position"]["y"],
                z=goal_pose_message["position"]["z"],
                frame=Frame.Robot,
            )
        except (IndexError, TypeError):
            return None

        pose_message: dict = self.bridge.pose.get_value()
        pose: Pose = decode_pose_message(pose_message=pose_message)

        distance = get_distance(current_position=pose.position, target=goal_position)

        return distance

    def publish(self) -> None:
        sleep(15)
        for i in range(500):
            distance = self.publish_distance_to_goal()
            self.logger.info(
                f"Published from MQTT client! -- DISTANCE_TO_GOAL:\n{distance}"
            )
            self.client.publish(topic="test", payload=f"data: Hello!\n{distance}")
            print(f"Have published message #: {i}")
            sleep(2.5)
            self.client.loop()
