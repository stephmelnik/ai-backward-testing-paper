"""
Helper functions for 2D vector arithmetic and Bezier curves.
"""
import math

def add(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def sub(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def mul(v, s):
    return (v[0] * s, v[1] * s)

def length(v):
    return math.sqrt(v[0]**2 + v[1]**2)

def normalize(v):
    l = length(v)
    if l == 0: return (0, 0)
    return (v[0] / l, v[1] / l)

def rotate_90(v):
    """Rotates vector 90 degrees counter-clockwise."""
    return (-v[1], v[0])

def distance(p1, p2):
    return length(sub(p1, p2))

def quadratic_bezier(p0, p1, p2, t):
    """Calculates point on a quadratic bezier curve at t [0,1]."""
    mt = 1 - t
    # B(t) = (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
    x = (mt**2 * p0[0]) + (2 * mt * t * p1[0]) + (t**2 * p2[0])
    y = (mt**2 * p0[1]) + (2 * mt * t * p1[1]) + (t**2 * p2[1])
    return (x, y)

def quadratic_bezier_derivative(p0, p1, p2, t):
    """Calculates the tangent vector (derivative) of the curve at t."""
    mt = 1 - t
    # B'(t) = 2(1-t)(P1-P0) + 2t(P2-P1)
    d1 = sub(p1, p0)
    d2 = sub(p2, p1)
    
    # Tangent = 2(1-t)d1 + 2t*d2
    tan_x = 2 * mt * d1[0] + 2 * t * d2[0]
    tan_y = 2 * mt * d1[1] + 2 * t * d2[1]
    return (tan_x, tan_y)