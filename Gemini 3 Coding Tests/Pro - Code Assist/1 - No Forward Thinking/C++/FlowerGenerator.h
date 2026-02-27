#pragma once
#include <vector>
#include <cmath>
#include <random>
#include "Vec2.h"
#include "Color.h"
#include "SVGWriter.h"

class FlowerGenerator {
private:
    int width, height;
    std::mt19937 rng;

    // Colors extracted from the reference image concept
    Color centerColor = Color(80, 80, 220, 0.4);  // Blue/Purple
    Color edgeColor = Color(255, 180, 180, 0.3);  // Pink/Peach

    double random(double min, double max) {
        std::uniform_real_distribution<double> dist(min, max);
        return dist(rng);
    }

public:
    FlowerGenerator(int w, int h, unsigned int seed = 12345) 
        : width(w), height(h), rng(seed) {}

    void generate(SVGWriter& svg) {
        Vec2 center(width / 2.0, height / 2.0);
        double scale = std::min(width, height) * 0.45;

        // We generate several "layers" of curves to create the volume
        // Layer 1: The central vertical core (tall, narrow)
        generateLayer(svg, center, scale, 300, 
            2.0, 6.0,   // X frequencies
            1.0, 3.0,   // Y frequencies
            0.001, 0.005 // Damping
        );

        // Layer 2: The side wings (wider, diagonal)
        generateLayer(svg, center, scale, 400, 
            3.0, 7.0, 
            2.0, 5.0, 
            0.002, 0.008
        );

        // Layer 3: The bottom petals (downward flow)
        generateLayer(svg, center, scale, 300, 
            4.0, 8.0, 
            3.0, 4.0, 
            0.001, 0.006
        );
    }

private:
    void generateLayer(SVGWriter& svg, Vec2 center, double scale, int count, 
                       double fx_base, double fx_mod, 
                       double fy_base, double fy_mod,
                       double damp_min, double damp_max) {
        
        for (int i = 0; i < count; ++i) {
            std::vector<Vec2> points;
            
            // Harmonograph parameters
            // x = A*sin(f1*t + p1)*exp(-d1*t) + B*sin(f2*t + p2)*exp(-d2*t)
            // y = ...
            
            // Randomize frequencies slightly around the base to create the "bundle" effect
            double f1 = fx_base + random(-0.1, 0.1);
            double f2 = fx_mod + random(-0.5, 0.5);
            double f3 = fy_base + random(-0.1, 0.1);
            double f4 = fy_mod + random(-0.5, 0.5);

            // Phases
            double p1 = random(0, 3.14 * 2);
            double p2 = random(0, 3.14 * 2);
            double p3 = random(0, 3.14 * 2);
            double p4 = random(0, 3.14 * 2);

            // Damping (decay)
            double d1 = random(damp_min, damp_max);
            double d2 = random(damp_min, damp_max);
            double d3 = random(damp_min, damp_max);
            double d4 = random(damp_min, damp_max);

            // Simulation loop
            double t = 0;
            double dt = 0.05;
            double max_t = 150.0; // Length of the line

            while (t < max_t) {
                // Compute raw position [-1, 1]
                double x = std::sin(t * f1 + p1) * std::exp(-d1 * t) + std::sin(t * f2 + p2) * std::exp(-d2 * t);
                double y = std::sin(t * f3 + p3) * std::exp(-d3 * t) + std::sin(t * f4 + p4) * std::exp(-d4 * t);

                // Normalize roughly to keep within scale
                x *= 0.5; 
                y *= 0.5;

                // Apply to screen coordinates
                Vec2 pos(center.x + x * scale, center.y + y * scale);
                points.push_back(pos);

                t += dt;
            }

            // Determine color based on the "average" extension of the curve
            // Curves that go further out are pinker
            double avgDist = points.size() > 10 ? (points[10].length() / scale) : 0.5; 
            Color curveColor = Color::lerp(centerColor, edgeColor, avgDist * 0.8);

            svg.addPath(points, curveColor, 0.5);
        }
    }
};