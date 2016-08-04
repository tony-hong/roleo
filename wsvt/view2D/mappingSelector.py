''' 
    mappingSelector.py
'''

import math

ZOOM_WEIGHT = 0.9


def mapping(parameters, quadrant = 4):
    if quadrant == 1:
        return mapping_1q(parameters[0], parameters[1], parameters[2])
    elif quadrant == 4 or quadrant == 32:
        return mapping_nq(parameters[0], parameters[1], parameters[2], quadrant)
    # elif quadrant == 0:
    #     return mapping_sc(parameters[0], parameters[1], parameters[2])
    elif quadrant == -2:
        x = parameters[0]
        y = parameters[1]
        cos = parameters[2]
        minCos = parameters[3]
        return mapping_svd_cosine(x, y, cos, minCos)
    elif quadrant == -1:
        x = parameters[0]
        y = parameters[1]
        maxVal = parameters[4]
        return mapping_svd(x, y, maxVal)
    else:
        return -1, -1


def mapping_1q(fraction, cosine, sumFraction):
    '''
    Mapping from fraction, and cosine to the x, y coordinate.
    This is a simple function which maps the high dimension vector to 2D.
    It is suitable for a web tool which need a short response time.

    @parameters:
        fraction = support / sumSupport
        cosine   = cosine_sim(centroid, wordVector)
    @return: 
        (x, y) is a tuple
    '''
    # Scale fraciton and cosine, let them become more sparse over [0, 1]
    x = 1 - sumFraction
    y = 1 - cosine

    # print x, y

    # Compute radial coordinates
    r = math.sqrt((math.pow(x, 2) + math.pow(y, 2))) * 1.5
    if x - 0 < 1e-3:
        rad_b = math.pi / 2
    else:
        # Scale rad from [0, pi/2] to [0, 2 * pi]
        rad_b = math.atan(y / x)
    rad = rad_b

    # Transform back to Cartesian coordinates
    x = r * math.cos(rad) - 0.75
    y = r * math.sin(rad) - 0.75

    return x, y


def mapping_nq(fraction, cosine, sumFraction, quadrant = 4):
    '''
    Mapping from fraction, and cosine to the x, y coordinate.
    This is a simple function which maps the high dimension vector to 2D.
    It is suitable for a web tool which needs a short response time.

    @parameters:
        fraction = support / sumSupport
        cosine   = cosine_sim(centroid, wordVector)
    @return: 
        (x, y) is a tuple
    '''
    # Scale fraciton and cosine, let them become more sparse over [0, 1]
    x = 1 - sumFraction
    y = 1 - cosine
    weight = 0.5

    # Compute radial coordinates
    r = math.sqrt(((1 - weight) * math.pow(x, 2) + weight * math.pow(y, 2)))
    
    rad_b = math.atan2( weight * y, ((1 - weight) * x))

    rad = rad_b * quadrant

    # Transform back to Cartesian coordinates
    y = r * math.cos(rad)
    x = r * math.sin(rad)

    return x, y


def mapping_svd_cosine(x, y, cos, minCos):
    maxR = 1 - minCos

    rad = math.atan2(y, x)
    r = (1 - cos) / maxR

    r = r * ZOOM_WEIGHT

    # Transform back to Cartesian coordinates
    x = r * math.cos(rad)
    y = r * math.sin(rad)

    return x, y


def mapping_svd(x, y, maxVal):
    rad = math.atan2(y, x)
    r = math.sqrt(math.pow(x, 2) + math.pow(y, 2)) / maxVal

    r = r * ZOOM_WEIGHT

    # Transform back to Cartesian coordinates
    x = r * math.cos(rad)
    y = r * math.sin(rad)

    return x, y
