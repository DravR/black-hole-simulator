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

        for (int i = 0; i < 6; i++) {
            value += amplitude * noise(p);
            p *= 2.0;
            amplitude *= 0.5;
        }

        return value;
    }

    float stars(vec2 p, float scale, float threshold) {
        vec2 grid = floor(p * scale);
        float rnd = hash(grid);

        if (rnd > threshold) {
            vec2 local = fract(p * scale) - 0.5;
            float d = length(local);
            float star = smoothstep(0.09, 0.0, d);
            float twinkle = 0.65 + 0.35 * sin(time * 2.0 + rnd * 60.0);
            return star * twinkle;
        }

        return 0.0;
    }

    vec3 temperatureColor(float heat) {
        vec3 cold = vec3(1.0, 0.30, 0.06);
        vec3 warm = vec3(1.0, 0.68, 0.22);
        vec3 hot = vec3(1.0, 0.96, 0.78);

        vec3 color = mix(cold, warm, smoothstep(0.0, 0.65, heat));
        color = mix(color, hot, smoothstep(0.65, 1.0, heat));

        return color;
    }

    vec2 lens(vec2 p) {
        float r = length(p);

        if (r < 0.95 && r > shadow_radius) {
            float strength = (0.95 - r) / 0.95;
            float bend = strength * strength * 0.18;
            p += normalize(p) * bend;
        }

        return p;
    }

    vec3 renderScene(vec2 p, vec2 starUV) {
        float r = length(p);

        vec3 color = vec3(0.0);

        float starLayer =
            stars(starUV, 180.0, 0.994) +
            stars(starUV + vec2(0.13, 0.31), 320.0, 0.997);

        color += vec3(starLayer);

        vec2 diskP = p;
        diskP.y /= 0.16;

        float diskR = length(diskP);
        float diskAngle = atan(diskP.y, diskP.x);

        float innerDisk = inner_disk_radius;
        float outerDisk = outer_disk_radius;

        vec2 plasmaCoords = vec2(
            diskAngle * 2.4 + time * 0.40,
            diskR * 6.0 - time * 0.28
        );

        float plasma = fbm(plasmaCoords * 3.5);
        float turbulence = (plasma - 0.5) * 0.10;

        float diskShape =
            smoothstep(innerDisk, innerDisk + 0.05, diskR + turbulence) *
            (1.0 - smoothstep(outerDisk - 0.18, outerDisk, diskR + turbulence));

        float verticalSoftness = exp(-abs(p.y) * 23.0);
        diskShape *= verticalSoftness;

        float heat = 1.0 - smoothstep(innerDisk, outerDisk, diskR);

        float doppler = 1.0 + 0.75 * sin(diskAngle);

        vec3 disk = temperatureColor(heat) * diskShape * doppler * 3.8;

        float diskGlow =
            exp(-abs(p.y) * 8.0)
            * smoothstep(outerDisk, innerDisk, diskR)
            * 0.75;

        color += vec3(1.0, 0.48, 0.14) * diskGlow;
        color += disk;

        float topArc = smoothstep(0.070, 0.0, abs(r - photon_ring_radius * 1.4));
        topArc *= smoothstep(-0.10, 0.35, p.y);
        topArc *= 1.0 - smoothstep(0.50, 1.05, abs(p.x));

        color += vec3(1.0, 0.82, 0.48) * topArc * 2.4;

        float photonRing = smoothstep(0.022, 0.0, abs(r - photon_ring_radius));
        color += vec3(1.0, 0.96, 0.78) * photonRing * 5.2;

        float halo = exp(-abs(r - photon_ring_radius * 1.08) * 15.0) * 0.85;
        color += vec3(1.0, 0.58, 0.20) * halo;

        float shadow = smoothstep(
            shadow_radius + 0.03,
            shadow_radius - 0.04,
            r
        );

        color = mix(color, vec3(0.0), shadow);

        return color;
    }

    void main() {
        vec2 p = uv * 2.0 - 1.0;
        p.x *= resolution.x / resolution.y;

        vec2 lensedP = lens(p);

        vec2 starUV = uv;

        float r = length(p);

        if (r < 0.95 && r > shadow_radius) {
            vec2 dir = normalize(p);
            float strength = (0.95 - r) / 0.95;
            starUV += dir * strength * strength * 0.08;
        }

        float chroma = smoothstep(0.90, shadow_radius, r) * 0.006;
        vec2 dir = r > 0.0 ? normalize(p) : vec2(0.0);

        float red = renderScene(lensedP + dir * chroma, starUV).r;
        float green = renderScene(lensedP, starUV).g;
        float blue = renderScene(lensedP - dir * chroma, starUV).b;

        vec3 color = vec3(red, green, blue);

        float bloom = max(max(color.r, color.g), color.b);
        color += vec3(1.0, 0.62, 0.25) * bloom * bloom * 0.35;

        float vignette = smoothstep(1.55, 0.25, length(p));
        color *= vignette;

        color = color / (color + vec3(1.0));
        color = pow(color, vec3(0.82));

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