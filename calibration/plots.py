import numpy as np
import utils
def create_voltage_scatter(ax,independant_axis_data,dependant_axis_data):
    print("vscatter")
    print("len independant_axis_data", len(independant_axis_data))
    print("len dependant_axis_data 0", len(dependant_axis_data[0]))
    print("len dependant_axis_data 1", len(dependant_axis_data[1]))
    print("len dependant_axis_data 2", len(dependant_axis_data[2]))
    utils.mmap(lambda x: ax.scatter(independant_axis_data,dependant_axis_data[x[0]],zorder=1, color=x[1], s=1, label=x[2]),[[0, "red", "a-vn"],[1, "orange", "b-vn"],[2, "black","c-vn"]])
    ax.legend(loc="center right")
    ax.set_xlim(left=0, right=2*np.pi)
    ax.hlines(y=[0], xmin=[0], xmax=[2*np.pi], colors='purple', linestyles='--', lw=1, label='Multiple Lines')

def create_voltage_lines(ax,independant_axis_data,dependant_axis_data):
    utils.mmap(lambda x: ax.plot(independant_axis_data,dependant_axis_data[x[0]],zorder=1, color=x[1], label=x[2]),[[0, "red", "a-vn"],[1, "orange", "b-vn"],[2, "black","c-vn"]])
    ax.legend(loc="center right")
    ax.set_xlim(left=0, right=2*np.pi)
    ax.hlines(y=[0], xmin=[0], xmax=[2*np.pi], colors='purple', linestyles='--', lw=1, label='Multiple Lines')