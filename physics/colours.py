import numpy as np


def wavelengthToRGB(wavelength):
    l = wavelength

    factor = 0.

    r = 0.
    g = 0.
    b = 0.

    if (l >= 380 and l < 440):
        r = -(l - 440.) / (440. - 380.)
        g = 0.
        b = 1.0

    elif (l >= 440 and l < 490):
        r = 0.
        g = (l - 440.) / (490. - 440.)
        b = 1.

    elif (l >= 490 and l < 510):
        r = 0.0
        g = 1.0
        b = -(l - 510) / (510 - 490)

    elif (l >= 510 and l < 580):
        r = (l - 510) / (580 - 510)
        g = 1.0
        b = 0.0

    elif (l >= 580 and l < 645):
        r = 1.0
        g = -(l - 645) / (645 - 580)
        b = 0.0

    elif (l >= 645 and l < 781):
        r = 1.0
        g = 0.0
        b = 0.0

    else:
        r = 0.0
        g = 0.0
        b = 0.0

    # Let the intensity fall off near the vision limits


    if (l >= 380 and l < 420):

        factor = 0.3 + 0.7 * (l - 380) / (420 - 380)

    elif (l >= 420 and l < 701):

        factor = 1.0

    elif (l >= 701 and l < 781):
        factor = 0.3 + 0.7 * (780 - l) / (780 - 700)

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
