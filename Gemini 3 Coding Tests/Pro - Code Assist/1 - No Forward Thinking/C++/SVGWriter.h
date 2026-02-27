#pragma once
#include <string>
#include <vector>
#include <fstream>
#include <iostream>
#include "Vec2.h"
#include "Color.h"

class SVGWriter {
private:
    int width, height;
    std::vector<std::string> elements;

public:
    SVGWriter(int w, int h) : width(w), height(h) {}

    void addPath(const std::vector<Vec2>& points, const Color& stroke, double strokeWidth) {
        if (points.empty()) return;

        std::stringstream ss;
        ss << "<path d=\"M " << points[0].x << " " << points[0].y;
        
        for (size_t i = 1; i < points.size(); ++i) {
            ss << " L " << points[i].x << " " << points[i].y;
        }

        ss << "\" stroke=\"" << stroke.toSVGString() << "\" "
           << "stroke-width=\"" << strokeWidth << "\" "
           << "fill=\"none\" "
           << "stroke-opacity=\"" << stroke.a << "\" />";
        
        elements.push_back(ss.str());
    }

    void save(const std::string& filename) {
        std::ofstream file(filename);
        if (!file.is_open()) {
            std::cerr << "Error opening file: " << filename << std::endl;
            return;
        }

        file << "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n";
        file << "<svg width=\"" << width << "\" height=\"" << height << "\" "
             << "xmlns=\"http://www.w3.org/2000/svg\" style=\"background-color:#FFFBF5\">\n";

        for (const auto& el : elements) {
            file << "  " << el << "\n";
        }

        file << "</svg>";
        file.close();
        std::cout << "SVG saved to " << filename << std::endl;
    }
};