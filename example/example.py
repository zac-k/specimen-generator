from phaseimaging import *

# Set the width
domain = (150e-9, 150e-9, 150e-9)

# Import the specimens
film = Specimen(width=domain,
                mean_inner_potential=-9.09 + 0.5j,
                specimen_file='film.txt',
                name='Carbon Film')
particle = Specimen(width=domain,
                    mean_inner_potential=-17 + 1j,
                    specimen_file='particle.txt',
                    name='Particle')

# Get resolution from particle
res = particle.resolution

# Rotate so that the carbon film is perpendicular to the beam
film.rotate(angle=90, axis=1)
particle.rotate(angle=90, axis=1)


# Set the beam and project the phase through the film and particle
phase = Phase(res[0:2], domain[0:2], name='Exit Phase')
beam = Beam(wavelength=1.97e-12)
phase.project_electrostatic(film, beam)
phase.project_electrostatic(particle, beam)

# Transfer to an underfocus image plane and plot the image
image = Intensity(res[0:2], domain[0:2], defocus=-1e-6)
image.transfer(phase, beam)
image.add_noise(0.1)
image.plot(limits=(0, 2))