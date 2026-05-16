import moderngl_window as mglw

from physics import get_shader_scale


class BlackHoleShader(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Black Hole Shader"
    window_size = (1000, 700)
    aspect_ratio = None
    resizable = True

    vertex_shader = """
    #version 330

    in vec2 in_position;
    out vec2 uv;

    void main() {
        uv = in_position * 0.5 + 0.5;
        gl_Position = vec4(in_position, 0.0, 1.0);
    }
    """

    fragment_shader = """
    #version 330

    uniform float time;
    uniform vec2 resolution;

    uniform float shadow_radius;
    uniform float photon_ring_radius;
    uniform float inner_disk_radius;
    uniform float outer_disk_radius;

    in vec2 uv;
    out vec4 fragColor;

    float hash(vec2 p) {
        return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
    }

    float noise(vec2 p) {
        vec2 i = floor(p);
        vec2 f = fract(p);

        float a = hash(i);
        float b = hash(i + vec2(1.0, 0.0));
        float c = hash(i + vec2(0.0, 1.0));
        float d = hash(i + vec2(1.0, 1.0));

        vec2 u = f * f * (3.0 - 2.0 * f);

        return mix(a, b, u.x)
             + (c - a) * u.y * (1.0 - u.x)
             + (d - b) * u.x * u.y;
    }

    float fbm(vec2 p) {
        float value = 0.0;
        float amplitude = 0.5;

        for (int i = 0; i < 7; i++) {
            value += amplitude * noise(p);
            p *= 2.0;
            amplitude *= 0.5;
        }

        return value;
    }

    mat2 rotate2d(float angle) {
        float s = sin(angle);
        float c = cos(angle);
        return mat2(c, -s, s, c);
    }

    float starField(vec2 p) {
        float stars = 0.0;

        vec2 grid1 = floor(p * 260.0);
        float rnd1 = hash(grid1);

        if (rnd1 > 0.994) {
            vec2 local = fract(p * 260.0) - 0.5;
            float d = length(local);
            stars += smoothstep(0.075, 0.0, d);
        }

        vec2 grid2 = floor((p + vec2(0.37, 0.12)) * 520.0);
        float rnd2 = hash(grid2);

        if (rnd2 > 0.997) {
            vec2 local = fract((p + vec2(0.37, 0.12)) * 520.0) - 0.5;
            float d = length(local);
            stars += smoothstep(0.045, 0.0, d) * 0.8;
        }

        return stars;
    }

    vec3 temperatureColor(float heat) {
        vec3 cold = vec3(0.95, 0.14, 0.02);
        vec3 warm = vec3(1.0, 0.48, 0.06);
        vec3 hot = vec3(1.0, 0.86, 0.35);
        vec3 whiteHot = vec3(1.0, 0.98, 0.82);

        vec3 color = mix(cold, warm, smoothstep(0.0, 0.45, heat));
        color = mix(color, hot, smoothstep(0.45, 0.78, heat));
        color = mix(color, whiteHot, smoothstep(0.78, 1.0, heat));

        return color;
    }

    vec2 lens(vec2 p) {
        float r = length(p);

        if (r > shadow_radius && r < 1.35) {
            float strength = (1.35 - r) / 1.35;
            float bend = strength * strength * 0.30;
            p += normalize(p) * bend;
        }

        return p;
    }

    float diskMaskFunc(vec2 q, float innerDisk, float outerDisk, out float diskR, out float diskAngle, out float heat) {
        vec2 diskP = q;
        diskP.y /= 0.46;

        diskR = length(diskP);
        diskAngle = atan(diskP.y, diskP.x);

        vec2 flow = vec2(
            diskAngle * 2.9 + time * 0.55,
            diskR * 7.5 - time * 0.42
        );

        float plasmaA = fbm(flow * 3.0);
        float plasmaB = fbm(flow * 8.0 + vec2(2.7, 5.1));

        float turbulence = (plasmaA - 0.5) * 0.13 + (plasmaB - 0.5) * 0.055;

        float mask =
            smoothstep(innerDisk, innerDisk + 0.045, diskR + turbulence) *
            (1.0 - smoothstep(outerDisk - 0.20, outerDisk, diskR + turbulence));

        heat = 1.0 - smoothstep(innerDisk, outerDisk, diskR);

        float broadThickness = exp(-abs(q.y) * 5.1);
        float coreThickness = exp(-abs(q.y) * 16.0);

        return mask * (broadThickness * 0.55 + coreThickness * 0.75);
    }

    vec3 renderBlackHole(vec2 p, vec2 starUV) {
        vec3 color = vec3(0.0);
        float r = length(p);

        float stars = starField(starUV);
        color += vec3(stars) * 0.9;

        vec2 q = rotate2d(-0.45) * p;

        float innerDisk = inner_disk_radius * 0.88;
        float outerDisk = outer_disk_radius * 1.28;

        float diskR;
        float diskAngle;
        float heat;

        float diskMask = diskMaskFunc(q, innerDisk, outerDisk, diskR, diskAngle, heat);

        vec2 flow = vec2(
            diskAngle * 3.4 + time * 0.70,
            diskR * 8.0 - time * 0.35
        );

        float plasmaA = fbm(flow * 4.0);
        float plasmaB = fbm(flow * 10.0 + vec2(4.2, 1.3));

        float filament = smoothstep(0.36, 1.0, plasmaA);
        float fineFilament = smoothstep(0.55, 1.0, plasmaB);

        float doppler = 1.0 + 1.05 * sin(diskAngle - 0.55);
        doppler = max(0.18, doppler);

        vec3 diskColor = temperatureColor(heat);

        vec3 disk =
            diskColor *
            diskMask *
            doppler *
            (3.6 + filament * 3.4 + fineFilament * 2.6);

        color += disk;

        float hotCore =
            diskMask *
            smoothstep(0.95, 0.25, abs(diskR - innerDisk)) *
            exp(-abs(q.y) * 18.0);

        color += vec3(1.0, 0.98, 0.82) * hotCore * doppler * 5.4;

        float tail =
            smoothstep(0.0, 1.0, q.x) *
            exp(-abs(q.y - 0.08 * q.x) * 4.0) *
            (1.0 - smoothstep(1.15, 2.35, q.x));

        float tailNoise = fbm(vec2(q.x * 3.8 - time * 0.55, q.y * 8.0 + time * 0.2));
        tail *= smoothstep(0.25, 1.0, tailNoise);

        color += vec3(1.0, 0.25, 0.03) * tail * 2.8;

        float foregroundBand =
            smoothstep(-0.12, 0.20, q.y) *
            (1.0 - smoothstep(0.42, 0.92, q.y)) *
            smoothstep(-1.25, -0.15, q.x + 0.25) *
            (1.0 - smoothstep(1.85, 2.45, q.x));

        float foregroundNoise =
            fbm(vec2(q.x * 5.0 - time * 0.60, q.y * 12.0 + time * 0.25));

        foregroundBand *= smoothstep(0.25, 1.0, foregroundNoise);

        vec3 foregroundColor =
            temperatureColor(0.65 + foregroundNoise * 0.35) *
            foregroundBand *
            5.2;

        vec2 arcP = rotate2d(-0.45) * p;
        float arcR = length(vec2(arcP.x, (arcP.y - 0.04) / 0.82));

        float upperArc =
            smoothstep(0.050, 0.0, abs(arcR - photon_ring_radius * 1.48)) *
            smoothstep(-0.22, 0.40, arcP.y) *
            (1.0 - smoothstep(0.32, 1.25, abs(arcP.x)));

        float upperArc2 =
            smoothstep(0.035, 0.0, abs(arcR - photon_ring_radius * 1.68)) *
            smoothstep(-0.12, 0.48, arcP.y) *
            (1.0 - smoothstep(0.35, 1.18, abs(arcP.x)));

        color += vec3(1.0, 0.80, 0.36) * upperArc * 4.4;
        color += vec3(1.0, 0.55, 0.16) * upperArc2 * 1.9;

        float photonRing = smoothstep(0.018, 0.0, abs(r - photon_ring_radius));
        color += vec3(1.0, 0.96, 0.78) * photonRing * 5.8;

        float halo = exp(-abs(r - photon_ring_radius * 1.06) * 14.0) * 0.85;
        color += vec3(1.0, 0.48, 0.12) * halo;

        float shadow = smoothstep(
            shadow_radius + 0.025,
            shadow_radius - 0.045,
            r
        );

        color = mix(color, vec3(0.0), shadow);

        color += foregroundColor;

        return color;
    }

    void main() {
        vec2 p = uv * 2.0 - 1.0;
        p.x *= resolution.x / resolution.y;

        float r = length(p);

        vec2 lensedP = lens(p);

        vec2 starUV = uv;

        if (r > shadow_radius && r < 1.35) {
            vec2 dir = normalize(p);
            float strength = (1.35 - r) / 1.35;
            starUV += dir * strength * strength * 0.13;
        }

        float chroma = smoothstep(1.05, shadow_radius, r) * 0.007;
        vec2 dir = r > 0.0 ? normalize(p) : vec2(0.0);

        float red = renderBlackHole(lensedP + dir * chroma, starUV).r;
        float green = renderBlackHole(lensedP, starUV).g;
        float blue = renderBlackHole(lensedP - dir * chroma, starUV).b;

        vec3 color = vec3(red, green, blue);

        float brightness = max(max(color.r, color.g), color.b);

        color += vec3(1.0, 0.43, 0.08) * brightness * brightness * 0.55;
        color += vec3(1.0, 0.78, 0.32) * pow(brightness, 4.0) * 0.35;

        float vignette = smoothstep(1.65, 0.18, length(p));
        color *= vignette;

        color = color / (color + vec3(1.0));
        color = pow(color, vec3(0.76));

        fragColor = vec4(color, 1.0);
    }
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.program = self.ctx.program(
            vertex_shader=self.vertex_shader,
            fragment_shader=self.fragment_shader,
        )

        self.quad = mglw.geometry.quad_fs()
        self.physics_scale = get_shader_scale()

    def on_render(self, time, frame_time):
        self.ctx.clear(0.0, 0.0, 0.0)

        self.program["time"].value = time
        self.program["resolution"].value = self.window_size

        self.program["shadow_radius"].value = self.physics_scale["shadow_radius"]
        self.program["photon_ring_radius"].value = self.physics_scale["photon_ring_radius"]
        self.program["inner_disk_radius"].value = self.physics_scale["inner_disk_radius"]
        self.program["outer_disk_radius"].value = self.physics_scale["outer_disk_radius"]

        self.quad.render(self.program)


if __name__ == "__main__":
    mglw.run_window_config(BlackHoleShader)