from gym.envs.registration import register

register(
    id='LaserTag-v0',
    entry_point='lasertag.envs:LaserTag'
)

register(
    id='LaserTag-small2-v0',
    entry_point='lasertag.envs:LaserTag_small2'
)

register(
    id='LaserTag-small3-v0',
    entry_point='lasertag.envs:LaserTag_small3'
)

register(
    id='LaserTag-small4-v0',
    entry_point='lasertag.envs:LaserTag_small4'
)
LEVEL =\
   ['********************************************',
    '*F                                F        *',
    '*            F                             *',
    '*                       F                  *',
    '*                         P                *',
    '*     P         F                          *',
    '*F                                    F    *',
    '*                                          *',
    '*       F                    F             *',
    '*                 F                        *',
    '*                                          *',
    '*F            P                 P          *',
    '*      P                                   *',
    '*                                          *',
    '*               P        P                F*',
    '*             F                            *',
    '*                              F           *',
    '*  F                 F                     *',
    '*       P                               P  *',
    '*                       F                  *',
    '*           F                        F     *',
    '********************************************']