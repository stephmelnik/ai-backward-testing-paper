#include <iostream>
#include "SVGWriter.h"
#include "FlowerGenerator.h"

int main() {
    // Image dimensions
    const int WIDTH = 1000;
    const int HEIGHT = 1000;

    std::cout << "Initializing Procedural Flower Generator..." << std::endl;

    SVGWriter svg(WIDTH, HEIGHT);
    FlowerGenerator generator(WIDTH, HEIGHT, 42); // Seed 42

    std::cout << "Generating curves..." << std::endl;
    generator.generate(svg);

    svg.save("flower_output.svg");

    return 0;
}