import math as m
import numpy as np
import numbers

error_compare = 'Vectors can only be compared to scalars or other vectors.'

class vector:
    """
    This class is an object for manipulating vectors in three dimensions
    """
    def __init__(self, x=0., y=0., z=0.):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.magnitude = self.modulus()

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        elif item == 2:
            return self.z

        else:
            raise IndexError('Vectors have three entries only.')

    def modulus(self):
        return m.sqrt(self.x**2 + self.y**2 + self.z**2)

    def unit(self):
        return vector(x=self.x/self.magnitude, y=self.y/self.magnitude,  z=self.z/self.magnitude)

    def __lt__(self, other):
        if isinstance(other, numbers.Number):
            return self.magnitude < other
        elif isinstance(other, vector):
            return self.magnitude < other.magnitude
        else:
            raise TypeError(error_compare)

    def __le__(self, other):
        if isinstance(other, numbers.Number):
            return self.magnitude <= other
        elif isinstance(other, vector):
            return self.magnitude <= other.magnitude
        else:
            raise TypeError(error_compare)

    def __eq__(self, other):
        if isinstance(other, numbers.Number):
            return self.magnitude == other
        elif isinstance(other,vector):
            return self.x == other.x and self.y == other.y and self.z == other.z
        else:
            raise TypeError(error_compare)

    def __ge__(self, other):
        if isinstance(other, numbers.Number):
            return self.magnitude >= other
        elif isinstance(other, vector):
            return self.magnitude >= other.magnitude
        else:
            raise TypeError(error_compare)

    def __gt__(self, other):
        if isinstance(other, numbers.Number):
            return self.magnitude > other
        elif isinstance(other, vector):
            return self.magnitude > other.magnitude
        else:
            raise TypeError(error_compare)

    def __add__(self, other):
        return vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return vector(other*self.x, other*self.y, other*self.z)
        elif isinstance(other, vector):
            return ValueError('Multiplication of two vectors is undefined - try dot() or cross() instead.')

    def __truediv__(self, other):
        if isinstance(other, numbers.Number):
            return vector(x=self.x/other, y=self.y/other, z=self.z/other)
        else:
            raise ValueError('Division of two vectors is undefined.')

    def __abs__(self):
        return self.magnitude

    def __invert__(self):
        return vector(x=1./self.x, y=1./self.y, z=1./self.z)

    def __repr__(self):
        return 'physics.vector.vector(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'

    def __bytes__(self):
        return bytes('(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')')

    def __hash__(self):
        return hash(str(self))

    def __bool__(self):
        if self.magnitude != 0.:
            return True
        else:
            return False

    def __dir__(self):
        return [self.x, self.y, self.z]

    def __len__(self):
        # Note: Rewrite if you generalise to higher-order vectors
        return 3

