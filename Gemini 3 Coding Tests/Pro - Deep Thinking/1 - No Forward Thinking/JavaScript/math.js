/**
 * Gumowski-Mira Attractor Math
 * 
 * The system is defined by:
 * G(x) = mu * x + (2 * (1 - mu) * x^2) / (1 + x^2)
 * x_n+1 = y_n + a * y_n * (1 - b * y_n^2) + G(x_n)
 * y_n+1 = -x_n + G(x_n+1)
 */

class AttractorEngine {
    constructor() {
        // Standard "Fleur-de-lis" parameters
        this.params = {
            a: 0.008,
            b: 0.05,
            mu: -0.496
        };
    }

    setMu(val) {
        this.params.mu = val;
    }

    /**
     * The G function: non-linear component of the map
     */
    G(x) {
        const mu = this.params.mu;
        return mu * x + (2 * (1 - mu) * x * x) / (1 + x * x);
    }

    /**
     * Generates a single trajectory (orbit).
     * Unlike chaotic attractors which are one long line, this specific regime 
     * forms closed loops (islands of stability).
     */
    generateOrbit(x0, y0, steps) {
        const path = [];
        let x = x0;
        let y = y0;

        for (let i = 0; i < steps; i++) {
            // Gumowski-Mira Iteration
            const g_x = this.G(x);
            
            // Calculate next X
            let x_next = y + this.params.a * y * (1 - this.params.b * y * y) + g_x;
            
            // Calculate next Y
            let y_next = -x + this.G(x_next);

            // Bounds check to prevent infinite numbers in unstable regions
            if (x_next * x_next + y_next * y_next > 10000) break;

            path.push({ x: x_next, y: y_next });

            x = x_next;
            y = y_next;
        }

        return path;
    }

    /**
     * Generates the full set of nested curves by scanning initial conditions.
     * The flower shape is revealed by varying the starting Y coordinate.
     */
    generateLayers(numLayers, pointsPerLayer) {
        const layers = [];
        
        // Scan range determined experimentally to cover the flower structure
        // Range: y = 0.5 to y = 10.0 covers the core out to the tips.
        const minScan = 0.5;
        const maxScan = 12.0;
        const step = (maxScan - minScan) / numLayers;

        for (let i = 0; i < numLayers; i++) {
            const startY = minScan + (i * step);
            // Starting X slightly off-center helps avoid singularities
            const startX = 0.1;

            const orbit = this.generateOrbit(startX, startY, pointsPerLayer);
            
            // Filter out dots or broken lines
            if (orbit.length > 50) {
                layers.push(orbit);
            }
        }

        return layers;
    }
}