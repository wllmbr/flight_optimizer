###########################################################
#
#   FILENAME:       engine.py
#
#   AUTHOR:         Will B.
# 
#   DESCRIPTION:    Basic engine model
#
###########################################################

class Rocket_Motor:
    def __init__(self, average_thrust_n, burn_time_s):
        self.thrust_n       = average_thrust_n
        self.burn_time_s    = burn_time_s

    def get_thrust(self, time_into_burn_s):
        return self.thrust_n

        # This can eventually support different thrust curves, but for now hardcode a J270
        J270_thrust_curve = [
            [0.007, 367.585],
            [0.020, 325.124],
            [0.074, 353.027],
            [0.136, 329.977],
            [0.176, 343.928],
            [0.273, 324.518],
            [0.330, 342.715],
            [0.357, 326.338],
            [0.399, 330.584],
            [0.473, 310.567],
            [0.553, 325.731],
            [0.734, 340.895],
            [0.744, 357.273],
            [0.761, 315.419],
            [0.788, 337.256],
            [0.897, 340.895],
            [1.009, 333.617],
            [1.053, 354.24],
            [1.105, 320.878],
            [1.180, 345.748],
            [1.214, 321.485],
            [1.249, 345.748],
            [1.274, 314.206],
            [1.500, 316.026],
            [1.601, 309.96],
            [1.916, 303.894],
            [1.956, 265.073],
            [2.000, 214.121],
            [2.052, 179.546],
            [2.102, 158.923],
            [2.201, 117.676],
            [2.268, 106.151],
            [2.303, 87.953],
            [2.369, 55.805],
            [2.407, 49.739],
            [2.486, 39.427],
            [2.558, 21.837],
            [2.563, 0.0]
        ]

        #Traverse the list to find where where we are in time
        # print "TIME %f" % time_into_burn_s
        for index in range(0,len(J270_thrust_curve)):
            # print "Comparing Time %f with Curve Time %f" % (time_into_burn_s, J270_thrust_curve[index][0])
            if(time_into_burn_s < J270_thrust_curve[index][0]):
                # The search has gone too far, so go back one index and return that thrust
                if(index == 0):
                    return J270_thrust_curve[index][1]
                else:
                    # print J270_thrust_curve[index-1][1]
                    return J270_thrust_curve[index -1][1]
        # We're past the last motor point so just return that
        return J270_thrust_curve[-1][1]

        # raise ValueError("Engine Model Failed")
