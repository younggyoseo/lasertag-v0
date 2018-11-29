from gym.envs.registration import register

register(
    id='LaserTag-v0',
    entry_point='laser_tag.envs:LaserTag'
)

register(
    id='LaserTag-small2-v0',
    entry_point='laser_tag.envs:LaserTag_small2'
)

register(
    id='LaserTag-small3-v0',
    entry_point='laser_tag.envs:LaserTag_small3'
)

register(
    id='LaserTag-small4-v0',
    entry_point='laser_tag.envs:LaserTag_small4'
)