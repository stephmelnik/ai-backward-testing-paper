class Renderer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        this.resize();
        window.addEventListener('resize', () => this.resize());
    }

    resize() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    clear() {
        // Clear with the cream paper color
        this.ctx.fillStyle = "#FFF9F4"; 
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    /**
     * Maps the layer index (0 to 1) to a color.
     * Reference image: Inner loops are Blue/Purple, Outer loops are Pink/Salmon.
     */
    getColor(t) {
        // HSL Interpolation
        // Inner (0.0): Blue-ish Purple (240deg)
        // Outer (1.0): Salmon Pink (340deg)
        
        const h = 230 + (t * 110); 
        const s = 60; 
        const l = 60 + (t * 15); // Get slightly lighter at edges
        const a = 0.3; // Low opacity for "sketchy" overlap effect

        return `hsla(${h}, ${s}%, ${l}%, ${a})`;
    }

    draw(layers) {
        this.clear();
        
        if (!layers.length) return;

        // 1. Calculate Bounds for Auto-Fit
        let minX = Infinity, maxX = -Infinity;
        let minY = Infinity, maxY = -Infinity;

        // Sample points to find bounding box
        for (const layer of layers) {
            for (const p of layer) {
                if (p.x < minX) minX = p.x;
                if (p.x > maxX) maxX = p.x;
                if (p.y < minY) minY = p.y;
                if (p.y > maxY) maxY = p.y;
            }
        }

        const dataW = maxX - minX;
        const dataH = maxY - minY;
        const cx = (minX + maxX) / 2;
        const cy = (minY + maxY) / 2;

        // 2. Setup Transformation
        const padding = 100;
        const scale = Math.min(
            (this.canvas.width - padding) / dataW,
            (this.canvas.height - padding) / dataH
        );

        this.ctx.save();
        
        // Center on screen
        this.ctx.translate(this.canvas.width / 2, this.canvas.height / 2);
        this.ctx.scale(scale, scale);
        this.ctx.translate(-cx, -cy);

        // Drawing Style
        this.ctx.lineWidth = 0.8 / scale; // Keep hairline thin regardless of zoom
        this.ctx.globalCompositeOperation = 'multiply'; // Ink blending

        // 3. Render Loop
        layers.forEach((layer, i) => {
            const t = i / layers.length; // Normalized position (0=core, 1=edge)
            
            this.ctx.strokeStyle = this.getColor(t);
            this.ctx.beginPath();

            // Draw the computed orbit
            if (layer.length > 0) {
                this.ctx.moveTo(layer[0].x, layer[0].y);
                for (let k = 1; k < layer.length; k++) {
                    this.ctx.lineTo(layer[k].x, layer[k].y);
                }
            }
            this.ctx.stroke();

            // Draw Mirror Image (Bilateral Symmetry)
            // The reference is perfectly symmetric. We force this visually.
            this.ctx.beginPath();
            if (layer.length > 0) {
                this.ctx.moveTo(-layer[0].x, layer[0].y);
                for (let k = 1; k < layer.length; k++) {
                    this.ctx.lineTo(-layer[k].x, layer[k].y);
                }
            }
            this.ctx.stroke();
        });

        this.ctx.restore();
    }
}