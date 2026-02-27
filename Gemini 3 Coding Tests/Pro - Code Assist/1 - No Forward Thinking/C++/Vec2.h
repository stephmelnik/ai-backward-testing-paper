#pragma once
#include <cmath>

struct Vec2 {
    double x, y;

    Vec2() : x(0), y(0) {}
    Vec2(double x, double y) : x(x), y(y) {}

    Vec2 operator+(const Vec2& other) const {
        return Vec2(x + other.x, y + other.y);
    }

    Vec2 operator*(double scalar) const {
        return Vec2(x * scalar, y * scalar);
    }

    // Rotate vector by angle (radians)
    Vec2 rotate(double angle) const {
        double s = std::sin(angle);
        double c = std::cos(angle);
        return Vec2(x * c - y * s, x * s + y * c);
    }

    double length() const {
        return std::sqrt(x * x + y * y);
    }
    
    double lengthSq() const {
        return x * x + y * y;
    }
};