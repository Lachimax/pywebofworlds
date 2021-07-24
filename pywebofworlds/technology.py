import matplotlib.pyplot as plt
import numpy as np

import pywebofworlds.utils as u


class Technology:
    """
    A class that models technological "advancement" as linear when indexed against actual Earth technology.
    """

    def __init__(self, slope=1., intercept=0.):
        """
        :param slope: The slope of the tech development line.
        :param intercept: The y-intercept of the development line.
        """
        self.slope = slope
        self.intercept = intercept

    @classmethod
    def from_two_points(cls, time_1, tech_1, time_2, tech_2):
        """
        Instantiate a Technology instance using two points lying on the line.
        :param time_1: Time of the first point.
        :param tech_1: Technology level of the first point.
        :param time_2: Time of the second point.
        :param tech_2: Technology level of the second point.
        :return:
        """
        slope, intercept = u.line_func(x1=time_1, y1=tech_1,
                                       x2=time_2, y2=tech_2)
        return cls(slope=slope, intercept=intercept)

    @classmethod
    def from_point_slope(cls, time, tech, slope):
        intercept = tech - slope * time
        return cls(slope=slope, intercept=intercept)

    def technology_at_time(self, time):
        """
        Use the straight-line model to calculate the technological level at the given time.
        :param time: float
        :return:
        """
        return self.slope * time + self.intercept

    def time_at_technology(self, tech):
        """
        Use the straight-line model to calculate the time at which a technological level is attained.
        :param tech: numerical
        :return:
        """
        return (tech - self.intercept) / self.slope

    def plot_tech_level(self, t_start: float, t_end: float, **kwargs):
        time = np.linspace(t_start, t_end)
        plt.plot(time, self.technology_at_time(time), **kwargs)
