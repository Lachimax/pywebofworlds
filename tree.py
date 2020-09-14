from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from typing import Union, List


def draw_tree_line(ax, origin_x: float, origin_y: float, destination_x: float, destination_y: float,
                   colour: str = 'black', edge_style: str = 'direct'):
    dx = destination_x - origin_x
    dy = destination_y - origin_y

    if edge_style == 'direct_no_arrow':
        ax.plot([origin_x, destination_x], [origin_y, destination_y], c=colour)
    elif edge_style == 'direct':
        ax.arrow(origin_x, origin_y, dx, dy, length_includes_head=False, width=0.01,
                 color=colour)
    elif edge_style == 'square':
        ax.plot([origin_x, origin_x, destination_x, destination_x],
                [origin_y, origin_y + dy / 2, origin_y + dy / 2, destination_y], c=colour)
        ax.plot([destination_x - 0.01, destination_x, destination_x + 0.01],
                [destination_y - 100, destination_y, destination_y - 100], c=colour)
    elif edge_style == 'square_no_arrow':
        ax.plot([origin_x, origin_x, destination_x, destination_x],
                [origin_y, origin_y + dy / 2, origin_y + dy / 2, destination_y], c=colour)


class Tree:
    def __init__(self, root=None):
        self.root = root

    def draw(self, edge_style='direct'):
        figure = plt.figure()
        ax = figure.add_subplot(111)
        if self.root is not None:
            self.root.draw(ax=ax, edge_style=edge_style)
        else:
            print("No root defined for Tree.")
        ax.invert_yaxis()
        plt.show()


class TreeNode:
    def __init__(self, parents: list = None, children: Union[List['TreeNode'], 'TreeNode'] = None, data=None,
                 x: float = 0, y: float = 0):
        # Allow relative & absolute definitions of position x/y
        self.parents = parents
        if type(children) is TreeNode:
            self.children = [children]
        elif type(children) is list:
            self.children = children
        elif children is not None:
            raise TypeError("children must be list or TreeNode.")
        else:
            self.children = None
        self.data = data
        self.x = x
        self.y = y

    def draw(self, ax, edge_style='direct'):
        ax.scatter(self.x, self.y, c='red')
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        ax.text(self.x + 0.5, self.y - 0.1, str(self.data), fontsize=14,
                verticalalignment='top', bbox=props)
        if self.children:
            for child in self.children:
                child.draw(ax=ax)
                dx = child.x - self.x
                dy = child.y - self.y
                if edge_style == 'direct':
                    ax.arrow(self.x, self.y, dx, dy, length_includes_head=True, width=0.05,
                             color='black')
                elif edge_style == 'square':
                    ax.add_patch(Rectangle((self.x - 0.05, self.y), 0.1, dy / 2, facecolor='black'))
                    ax.add_patch(Rectangle((self.x, self.y + dy / 2 - 0.05), dx, 0.05, facecolor='black'))
                    ax.arrow(child.x, self.y + dy / 2, 0, dy / 2, length_includes_head=True, width=0.05,
                             color='black')
