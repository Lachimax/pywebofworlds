import numpy as np


def wavelength_to_rgb(wavelength):
    factor = 0.

    r = 0.
    g = 0.
    b = 0.

    if 440 > wavelength >= 380:
        r = -(wavelength - 440.) / (440. - 380.)
        g = 0.
        b = 1.0

    elif 490 > wavelength >= 440:
        r = 0.
        g = (wavelength - 440.) / (490. - 440.)
        b = 1.

    elif 510 > wavelength >= 490:
        r = 0.0
        g = 1.0
        b = -(wavelength - 510) / (510 - 490)

    elif 580 > wavelength >= 510:
        r = (wavelength - 510) / (580 - 510)
        g = 1.0
        b = 0.0

    elif 640 > wavelength >= 580:
        r = 1.0
        g = -(wavelength - 645) / (645 - 580)
        b = 0.0

    elif 781 > wavelength >= 645:
        r = 1.0
        g = 0.0
        b = 0.0

    else:
        r = 0.0
        g = 0.0
        b = 0.0

    # Let the intensity fall off near the vision limits

    if 420 > wavelength >= 380:

        factor = 0.3 + 0.7 * (wavelength - 380) / (420 - 380)

    elif 701 > wavelength >= 420:

        factor = 1.0

    elif 781 > wavelength >= 701:
        factor = 0.3 + 0.7 * (780 - wavelength) / (780 - 700)

    else:
        factor = 0.0

    rgb = np.array([r, g, b])

    # Don't want 0^x = 1 for x <> 0

    # rgb[0] = r == 0.0 ? 0: (int)
    # Math.round(IntensityMax * Math.pow(r * factor, Gamma))
    # rgb[1] = g == 0.0 ? 0: (int)
    # Math.round(IntensityMax * Math.pow(g * factor, Gamma))
    # rgb[2] = b == 0.0 ? 0: (int)
    # Math.round(IntensityMax * Math.pow(b * factor, Gamma))

    return rgb
