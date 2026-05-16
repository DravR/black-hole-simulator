from astropy import units as u
from astropy.constants import G, c
import math


BLACK_HOLE_MASS = 10 * u.solMass

SCHWARZSCHILD_RADIUS = (2 * G * BLACK_HOLE_MASS / c**2).to(u.km)

PHOTON_SPHERE_RADIUS = 1.5 * SCHWARZSCHILD_RADIUS
APPARENT_SHADOW_RADIUS = (math.sqrt(27) / 2) * SCHWARZSCHILD_RADIUS

INNER_ACCRETION_DISK_RADIUS = 3.0 * SCHWARZSCHILD_RADIUS
OUTER_ACCRETION_DISK_RADIUS = 12.0 * SCHWARZSCHILD_RADIUS


def get_shader_scale():
    visual_outer_disk = 1.70

    shadow_radius = (
        APPARENT_SHADOW_RADIUS / OUTER_ACCRETION_DISK_RADIUS
    ).value * visual_outer_disk

    photon_ring_radius = (
        PHOTON_SPHERE_RADIUS / OUTER_ACCRETION_DISK_RADIUS
    ).value * visual_outer_disk

    inner_disk_radius = (
        INNER_ACCRETION_DISK_RADIUS / OUTER_ACCRETION_DISK_RADIUS
    ).value * visual_outer_disk

    outer_disk_radius = visual_outer_disk

    return {
        "shadow_radius": shadow_radius,
        "photon_ring_radius": photon_ring_radius,
        "inner_disk_radius": inner_disk_radius,
        "outer_disk_radius": outer_disk_radius,
    }


def print_physics_info():
    print("Black hole mass:", BLACK_HOLE_MASS)
    print("Schwarzschild radius:", SCHWARZSCHILD_RADIUS)
    print("Photon sphere:", PHOTON_SPHERE_RADIUS)
    print("Apparent shadow radius:", APPARENT_SHADOW_RADIUS)
    print("Inner accretion disk:", INNER_ACCRETION_DISK_RADIUS)
    print("Outer accretion disk:", OUTER_ACCRETION_DISK_RADIUS)
    print("Shader scale:", get_shader_scale())


if __name__ == "__main__":
    print_physics_info()