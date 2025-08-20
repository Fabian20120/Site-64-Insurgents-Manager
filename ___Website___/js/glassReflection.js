window.addEventListener('DOMContentLoaded', function() {
    // Track mouse movement for interactive reflections
    let mouseX = 0.5;
    let mouseY = 0.5;
    let lastUpdateTime = 0;
    const updateInterval = 16; // ~60fps
    
    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX / window.innerWidth;
        mouseY = e.clientY / window.innerHeight;
        
        // Throttled redraw for performance
        const now = performance.now();
        if (now - lastUpdateTime > updateInterval) {
            lastUpdateTime = now;
            updateReflections();
        }
    });
    
    function updateReflections() {
        setupGlassReflection('header-reflection', document.querySelector('header').getBoundingClientRect());
        setupGlassReflection('hero-reflection', document.querySelector('.hero_glass').getBoundingClientRect());
    }
    
    // Initial setup
    updateReflections();
    
    function setupGlassReflection(canvasId, rect) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        // Set canvas dimensions
        canvas.width = rect.width;
        canvas.height = rect.height;
        
        const gl = canvas.getContext('webgl');
        if (!gl) {
            console.warn('WebGL nicht unterstützt');
            return;
        }
        
        // Clear with a transparent color
        gl.clearColor(0.0, 0.0, 0.0, 0.0);
        gl.clear(gl.COLOR_BUFFER_BIT);
        
        // Enable alpha blending - crucial for glass effect
        gl.enable(gl.BLEND);
        gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
        
        // iOS 26 style shader with proper edge highlights
        const vertexShaderSource = `
            attribute vec2 position;
            varying vec2 vPosition;
            void main() {
                vPosition = position;
                gl_Position = vec4(position, 0.0, 1.0);
            }
        `;
        
        const fragmentShaderSource = `
            precision highp float;
            varying vec2 vPosition;
            uniform vec2 resolution;
            uniform vec2 mouse;
            uniform float time;
            
            // Improved noise function for better texture
            float noise(vec2 p) {
                vec2 ip = floor(p);
                vec2 u = fract(p);
                u = u*u*u*(u*(u*6.0-15.0)+10.0); // Improved smoothstep
                
                float res = mix(
                    mix(sin(dot(ip, vec2(12.9898,78.233))),
                        sin(dot(ip + vec2(1.0, 0.0), vec2(12.9898,78.233))), u.x),
                    mix(sin(dot(ip + vec2(0.0, 1.0), vec2(12.9898,78.233))),
                        sin(dot(ip + vec2(1.0, 1.0), vec2(12.9898,78.233))), u.x), u.y);
                return 0.5 + 0.5*res;
            }
            
            void main() {
                vec2 uv = vPosition * 0.5 + 0.5;
                
                // Mouse influence - more prominent for real iOS 26 feel
                vec2 mouseOffset = (mouse - 0.5) * 0.3;
                
                // Simulate light source from top-left (iOS style)
                vec2 lightPos = vec2(0.2, 0.2) + mouseOffset * 0.8;
                float distToLight = length(uv - lightPos);
                
                // Main glass highlight (stronger at edges - key for iOS 26 look)
                float edgeHighlight = smoothstep(0.7, 0.0, length(uv - lightPos));
                
                // Edge detection for iOS 26-style rim highlights
                float edgeTop = smoothstep(0.05, 0.0, uv.y);
                float edgeLeft = smoothstep(0.05, 0.0, uv.x);
                float edgeBottom = smoothstep(0.05, 0.0, 1.0 - uv.y);
                float edgeRight = smoothstep(0.05, 0.0, 1.0 - uv.x);
                
                // Combine edge highlights with mouse-responsive intensity
                float edgeFactor = (edgeTop + edgeLeft) * 0.5 + (edgeBottom + edgeRight) * 0.2;
                edgeFactor *= 0.5 + mouse.y * 0.5; // More highlight when mouse is lower
                
                // Detailed noise for texture (iOS glass has subtle texture)
                float noisePattern = noise(uv * 15.0 + time * 0.05) * 0.03;
                noisePattern += noise(uv * 30.0 - time * 0.02) * 0.015;
                
                // Combine all lighting effects with proper weighting
                float alpha = edgeHighlight * 0.15 + edgeFactor * 0.12 + noisePattern;
                
                // Add subtle color - iOS 26 glass isn't pure white
                // Slight blue tint for cooler areas, warm for highlights
                vec3 coolColor = vec3(0.92, 0.95, 1.0);
                vec3 warmColor = vec3(1.0, 0.98, 0.95);
                vec3 finalColor = mix(coolColor, warmColor, edgeHighlight);
                
                gl_FragColor = vec4(finalColor, alpha * 0.6); // Higher alpha for more visible effect
            }
        `;
        
        // Create and compile shaders
        const vertexShader = gl.createShader(gl.VERTEX_SHADER);
        gl.shaderSource(vertexShader, vertexShaderSource);
        gl.compileShader(vertexShader);
        
        const fragmentShader = gl.createShader(gl.FRAGMENT_SHADER);
        gl.shaderSource(fragmentShader, fragmentShaderSource);
        gl.compileShader(fragmentShader);
        
        // Check for compilation errors
        if (!gl.getShaderParameter(fragmentShader, gl.COMPILE_STATUS)) {
            console.error('Shader compilation error:', gl.getShaderInfoLog(fragmentShader));
            return;
        }
        
        // Link shaders into a program
        const program = gl.createProgram();
        gl.attachShader(program, vertexShader);
        gl.attachShader(program, fragmentShader);
        gl.linkProgram(program);
        gl.useProgram(program);
        
        // Create a rectangle to cover the canvas
        const positions = [
            -1, -1,
            1, -1,
            -1, 1,
            1, 1
        ];
        
        const positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);
        
        const positionLocation = gl.getAttribLocation(program, 'position');
        gl.enableVertexAttribArray(positionLocation);
        gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);
        
        // Set uniform values
        const resolutionLocation = gl.getUniformLocation(program, 'resolution');
        gl.uniform2f(resolutionLocation, canvas.width, canvas.height);
        
        const mouseLocation = gl.getUniformLocation(program, 'mouse');
        gl.uniform2f(mouseLocation, mouseX, mouseY);
        
        const timeLocation = gl.getUniformLocation(program, 'time');
        gl.uniform1f(timeLocation, performance.now() / 1000.0);
        
        // Draw
        gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    }
    
    // Add subtle animation even without mouse movement
    setInterval(function() {
        updateReflections();
    }, 100);
});