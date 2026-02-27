/**
 * FlowerGenerator
 * 
 * Recreates a stylized procedural flower using HTML5 Canvas.
 * The flower is composed of multiple "Lobes", where each lobe is a collection
 * of oscillating Bezier curves.
 */

class FlowerGenerator {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // Configuration for the visual style
        this.config = {
            width: 1000,
            height: 1000,
            bgColor: '#FFFBF5',
            // Colors: Inner (Blue/Purple) -> Outer (Pink/Salmon)
            colorInner: { h: 245, s: 50, l: 55 }, 
            colorOuter: { h: 340, s: 90, l: 75 },
            lineOpacity: 0.35,
            lineWidth: 0.8,
            globalScale: 0.9
        };

        this.resize();
        window.addEventListener('resize', () => this.resize());
        
        // Initial draw
        this.draw();
    }

    resize() {
        // Set high resolution for crisp lines
        const dpr = window.devicePixelRatio || 1;
        this.canvas.width = this.config.width * dpr;
        this.canvas.height = this.config.height * dpr;
        this.canvas.style.width = `${this.config.width}px`;
        this.canvas.style.height = `${this.config.height}px`;
        this.ctx.scale(dpr, dpr);
        this.draw();
    }

    /**
     * Main drawing routine
     */
    draw() {
        const { width, height, bgColor, globalScale } = this.config;
        const ctx = this.ctx;

        // Clear background
        ctx.fillStyle = bgColor;
        ctx.fillRect(0, 0, width, height);

        // Center the coordinate system
        ctx.save();
        ctx.translate(width / 2, height / 2 + 50); // Shift down slightly to center the flower visually
        ctx.scale(globalScale, globalScale);

        // Define the layers of the flower (The anatomy of the image)
        // We define the right side, and the loop will mirror it to the left.
        const layers = [
            // Center Top (The main upright petal)
            { angle: 0, scale: 1.0, width: 120, length: 380, curve: 0, strands: 60, freq: 0.15, amp: 5 },
            
            // Top Sides (The large wings)
            { angle: Math.PI / 6, scale: 0.95, width: 140, length: 350, curve: 50, strands: 50, freq: 0.15, amp: 6 },
            
            // Middle Sides (Curling outwards)
            { angle: Math.PI / 2.5, scale: 0.85, width: 130, length: 320, curve: 100, strands: 45, freq: 0.18, amp: 6 },
            
            // Lower Sides (Drooping down)
            { angle: Math.PI / 1.4, scale: 0.75, width: 120, length: 280, curve: 120, strands: 40, freq: 0.2, amp: 5 },
            
            // Bottom Center (The small heart shape at the bottom)
            { angle: Math.PI, scale: 0.5, width: 100, length: 200, curve: 20, strands: 30, freq: 0.25, amp: 4 },
            
            // Inner Details (Extra density in the center)
            { angle: Math.PI / 4, scale: 0.5, width: 60, length: 150, curve: 30, strands: 20, freq: 0.2, amp: 3 },
            { angle: Math.PI / 1.5, scale: 0.4, width: 60, length: 140, curve: 40, strands: 20, freq: 0.2, amp: 3 }
        ];

        // Draw layers
        // We draw back-to-front implicitly, but since we use multiply/transparency, order matters less than coverage.
        
        // Draw Right Side
        layers.forEach(layer => {
            this.drawLobe(ctx, layer, 1);
        });

        // Draw Left Side (Mirrored)
        layers.forEach(layer => {
            // Skip center layers if they are perfectly vertical (angle 0 or PI) to avoid double drawing,
            // but in this artistic style, overlapping the center slightly looks good.
            // However, for angle 0 and PI, we might want to be careful.
            if (layer.angle !== 0 && layer.angle !== Math.PI) {
                this.drawLobe(ctx, layer, -1);
            } else {
                // For vertical layers, we might want to draw a mirrored version if it has width, 
                // or just rely on the fan spread. 
                // The image shows bilateral symmetry where the center petals are actually two halves meeting.
                // So we WILL mirror 0 and PI, but maybe offset the angle slightly or just flip X.
                this.drawLobe(ctx, layer, -1);
            }
        });

        ctx.restore();
    }

    /**
     * Draws a single "Lobe" or petal.
     * A lobe is a collection of lines emanating from (0,0) and following a guide curve.
     * 
     * @param {CanvasRenderingContext2D} ctx 
     * @param {Object} config - Configuration for this lobe
     * @param {number} side - 1 for right, -1 for left (mirroring)
     */
    drawLobe(ctx, config, side) {
        const { angle, scale, width, length, curve, strands, freq, amp } = config;
        
        // Base rotation for the lobe axis
        const baseAngle = angle * side;
        
        // Control points for the quadratic bezier guide curve
        // Start at (0,0)
        // Control point determines the "bend"
        // End point determines length and direction
        const p0 = { x: 0, y: 0 };
        
        // We rotate the coordinate space to make math easier (local space)
        ctx.save();
        ctx.rotate(baseAngle);

        // Generate strands
        for (let i = 0; i <= strands; i++) {
            // Normalized index from -1 (left edge of lobe) to 1 (right edge of lobe)
            // We map 0 to strands to -1..1
            const t_strand = (i / strands) * 2 - 1; 
            
            // Calculate color based on how far from center the strand is.
            // Center (0) is Blue, Edges (1) are Pink.
            const color = this.getGradientColor(Math.abs(t_strand));
            ctx.strokeStyle = color;
            ctx.lineWidth = this.config.lineWidth;
            
            ctx.beginPath();

            // Draw the line as a series of segments
            const segments = 60;
            for (let j = 0; j <= segments; j++) {
                const t_len = j / segments; // 0 to 1 along the length of the strand

                // 1. Base Curve Calculation
                // The guide curve goes straight up (y axis negative) in local space
                // We bend x based on the 'curve' parameter and the side
                // We spread x based on the 'width' parameter and the strand index (t_strand)
                
                // Fan spread: starts at 0, gets wider towards the end
                const spread = t_strand * width * scale * Math.sin(t_len * Math.PI * 0.8);
                
                // Main structural curve (bending outwards)
                // If side is 1 (right), we bend right (positive x). 
                // Actually, 'curve' param defines how much the lobe hooks.
                const mainBend = curve * scale * (t_len * t_len); 

                // Calculate base position
                let x = spread + (mainBend * side); 
                let y = -length * scale * t_len;

                // 2. Oscillation / Wavy Texture
                // We add a sine wave to the X coordinate.
                // Frequency increases slightly along the length? Or constant.
                // Amplitude increases along length (0 at base, high at tip).
                // Phase shift depends on strand index to create the "interference" pattern.
                
                const wavePhase = t_strand * Math.PI * 10; // Phase shift across strands
                const waveVal = Math.sin((t_len * Math.PI * 2 * freq * 20) + wavePhase);
                
                // Envelope for wave amplitude (taper at start and end)
                const waveEnv = Math.sin(t_len * Math.PI); 
                
                const oscillation = waveVal * amp * waveEnv;

                // Apply oscillation perpendicular to the flow? 
                // For simplicity in local space, adding to X works well enough for vertical-ish lobes.
                x += oscillation;

                if (j === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            }
            ctx.stroke();
        }

        ctx.restore();
    }

    /**
     * Interpolates between the inner (blue) and outer (pink) colors.
     * @param {number} t - 0 (center) to 1 (edge)
     */
    getGradientColor(t) {
        const { colorInner, colorOuter, lineOpacity } = this.config;
        
        // Non-linear interpolation for better visual weight
        // Push the blue further out or keep it tight? 
        // t^2 keeps blue in the center, linear spreads it.
        const factor = t; 

        const h = this.lerp(colorInner.h, colorOuter.h, factor);
        const s = this.lerp(colorInner.s, colorOuter.s, factor);
        const l = this.lerp(colorInner.l, colorOuter.l, factor);

        return `hsla(${h}, ${s}%, ${l}%, ${lineOpacity})`;
    }

    /**
     * Linear interpolation helper
     */
    lerp(start, end, t) {
        return start + (end - start) * t;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new FlowerGenerator('flowerCanvas');
});