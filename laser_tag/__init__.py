from gym.envs.registration import register

register(
    id='LaserTag-v0',
    entry_point='laser_tag.envs:LaserTag'
)