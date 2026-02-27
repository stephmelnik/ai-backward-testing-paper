#pragma once
#include <algorithm>
#include <string>
#include <sstream>

struct Color {
    int r, g, b;
    double a; // Alpha 0.0 - 1.0

    Color(int r, int g, int b, double a = 1.0) : r(r), g(g), b(b), a(a) {}

    // Linear interpolation between two colors
    static Color lerp(const Color& c1, const Color& c2, double t) {
        t = std::max(0.0, std::min(1.0, t));
        return Color(
            static_cast<int>(c1.r + (c2.r - c1.r) * t),
            static_cast<int>(c1.g + (c2.g - c1.g) * t),
            static_cast<int>(c1.b + (c2.b - c1.b) * t),
            c1.a + (c2.a - c1.a) * t
        );
    }

    std::string toSVGString() const {
        std::stringstream ss;
        ss << "rgb(" << r << "," << g << "," << b << ")";
        return ss.str();
    }
};