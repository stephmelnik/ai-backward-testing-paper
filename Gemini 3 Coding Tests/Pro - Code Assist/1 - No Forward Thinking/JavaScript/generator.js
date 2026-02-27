/**
 * FlowerGenerator
 * 
 * Generates a procedural flower pattern using a modified Temple H. Fay Butterfly Curve.
 * The "texture" is achieved by iterating the curve with a non-integer period, causing
 * the path to precess and fill the volume over many iterations.
 */
class FlowerGenerator {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        
        // Configuration for the generative art
        this.config = {
            // Resolution and Iteration
            stepSize: 0.01,          // Step size for t (smaller = smoother)
            totalCycles: 80,         // How many "loops" to draw. Higher = denser.
            
            // Curve Parameters (Based on Butterfly Curve)
            // r = exp(cos(t)) - 2*cos(4t) + sin((2t - PI)/24)^5
            periodOffset: 0.1,       // Adds irregularity to the period to prevent perfect overlapping
            scale: 120,              // Base size of the flower
            rotation: -Math.PI / 2,  // Rotate -90deg to make the big lobe point up
            
            // Positioning
            centerX: 0.5,            // 0.5 = center of canvas
            centerY: 0.55,           // Slightly lower than center to fit the top lobe
            
            // Visuals
            lineWidth: 0.5,
            opacity: 0.6,
            
            // Colors (HSL)
            centerColor: { h: 240, s: 60, l: 60 }, // Blue/Purple for inner veins
            outerColor:  { h: 340, s: 80, l: 80 }, // Pink/Salmon for outer petals
        };

        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        // Handle High DPI displays
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = window.innerWidth * dpr;
        this.canvas.height = window.innerHeight * dpr;
        this.ctx.scale(dpr, dpr);
        
        // Re-render on resize
        this.draw();
    }

    /**
     * The parametric equation for the flower.
     * Returns polar radius 'r' for a given angle 'theta'.
     */
    calculateRadius(theta) {
        // The "Butterfly Curve" equation
        // r = e^(cos(theta)) - 2*cos(4*theta) + sin(theta/12)^5
        
        // We modify the divisor (12) slightly by adding the cycle count to it
        // in the main loop, or here, to create the "precession" effect.
        // For this specific image, the texture comes from the sin^5 term changing phase.
        
        const part1 = Math.exp(Math.cos(theta));
        const part2 = 2 * Math.cos(4 * theta);
        const part3 = Math.pow(Math.sin((theta / 12) + this.config.periodOffset), 5);
        
        return part1 - part2 + part3;
    }

    /**
     * Interpolates between two colors based on a factor (0 to 1).
     */
    getStrokeColor(factor) {
        const c1 = this.config.centerColor;
        const c2 = this.config.outerColor;
        
        // Clamp factor
        const t = Math.max(0, Math.min(1, factor));
        
        const h = c1.h + (c2.h - c1.h) * t;
        const s = c1.s + (c2.s - c1.s) * t;
        const l = c1.l + (c2.l - c1.l) * t;
        
        return `hsla(${h}, ${s}%, ${l}%, ${this.config.opacity})`;
    }

    draw() {
        const { width, height } = this.canvas;
        // Clear with transparent (background is in CSS)
        this.ctx.clearRect(0, 0, width, height);
        
        // Center point
        const cx = width / window.devicePixelRatio * this.config.centerX;
        const cy = height / window.devicePixelRatio * this.config.centerY;

        this.ctx.lineWidth = this.config.lineWidth;
        this.ctx.lineCap = 'round';

        // We draw the curve in segments to allow color changes along the path.
        const batchSize = 50; 
        const maxTheta = this.config.totalCycles * Math.PI;
        const totalSteps = Math.ceil(maxTheta / this.config.stepSize);
        
        this.ctx.beginPath();
        
        // Pre-calculate first point
        let r = this.calculateRadius(0);
        let x = cx + r * this.config.scale * Math.cos(this.config.rotation);
        let y = cy + r * this.config.scale * Math.sin(this.config.rotation);
        this.ctx.moveTo(x, y);

        for (let i = 1; i <= totalSteps; i++) {
            const theta = i * this.config.stepSize;
            
            r = this.calculateRadius(theta);
            
            // Convert polar to cartesian with rotation
            const drawAngle = theta + this.config.rotation;
            x = cx + r * this.config.scale * Math.cos(drawAngle);
            y = cy + r * this.config.scale * Math.sin(drawAngle);
            
            this.ctx.lineTo(x, y);

            if (i % batchSize === 0) {
                // Normalize r for coloring (approx max r is 4.5)
                const colorFactor = (Math.abs(r) / 4.5); 
                this.ctx.strokeStyle = this.getStrokeColor(colorFactor);
                this.ctx.stroke();
                this.ctx.beginPath();
                this.ctx.moveTo(x, y);
            }
        }
        this.ctx.stroke(); // Final stroke
    }
}