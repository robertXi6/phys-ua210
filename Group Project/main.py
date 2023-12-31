import matplotlib.pyplot as plt
import numpy as np
from cells import Cell


def plot_grid(grid_to_plot, nt_cur, nx_cur): # this function plot given variable of every cell element in the matrix
    global jj
    rho_map_cur = np.zeros((nt_cur, nx_cur))
    for jj in range(nt_cur):
        for ii in range(0, nx_cur):
            rho_map_cur[jj][ii] = grid_to_plot[jj][ii].P  # change which variable you want to see, U[0] is rho
        if jj % 10 == 0:
            plt.plot(rho_map_cur[jj])
    print(rho_map_cur)
    plt.show()
    return rho_map_cur


def plot_3d(data):
    position = np.arange(data.shape[1])
    time = np.arange(data.shape[0])

    X, Y = np.meshgrid(position, time)

    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the surface
    ax.plot_surface(X, Y, data, cmap='viridis')

    # Label axes
    ax.set_xlabel('Position')
    ax.set_ylabel('Time')
    ax.set_zlabel('Density')

    # Show the plot
    plt.show()

nt = 200 # total time steps
nx = 100 # total space steps
v0 = 0.01 # initial velocity
delta_x = 1
delta_t = 0.3
rows = nt
cols = nx
grid_cur = []


# initialization, matrix nt*nx, all element are Cell
for j in range(nt):
    grid_cur.append([])
    for i in range(nx):
        if i < nx / 2:
            rho_L = 1
            P_L = 0.8
            grid_cur[j].append(Cell(rho_L, v0*rho_L, P_L))
        else:
            rho_R = 0.1
            P_R = 0.1
            grid_cur[j].append(Cell(rho_R, v0*rho_R, P_R))
# plot_grid(grid_cur, nt, nx)


def find_p(cur_cell): # find pressure given U
    cur_cell.P = (cur_cell.gamma-1)*cur_cell.U[0]*(cur_cell.U[2]/cur_cell.U[0]-0.5*(cur_cell.U[1]/cur_cell.U[0])**2)
    # print(cur_cell.P)
    return cur_cell.P


def find_lambda(cur_cell): # find lambda given U
    p = find_p(cur_cell)
    v = cur_cell.U[1] / cur_cell.U[0]
    cur_cell.lambda_plus = v + (cur_cell.gamma*p/cur_cell.U[0])**0.5
    cur_cell.lambda_minus = v - (cur_cell.gamma*p/cur_cell.U[0])**0.5
    # print(cur_cell.U)
    # print(cur_cell.lambda_plus, cur_cell.lambda_minus)
    return cur_cell.lambda_plus, cur_cell.lambda_minus


def find_f_half(cur_cell, r_cell): # find F_HLL given current and right cell
    lambda_plus, lambda_minus = find_lambda(cur_cell)
    # print(lambda_plus,lambda_minus)
    for ii in range(3):
        lambda_plus_cur = lambda_plus*cur_cell.U[ii]
        lambda_plus_r = lambda_plus*r_cell.U[ii]
        lambda_minus_cur = -lambda_minus*cur_cell.U[ii]
        lambda_minus_r = -lambda_minus*r_cell.U[ii]
        cur_cell.alpha_plus[ii] = max([0, lambda_plus_cur, lambda_plus_r])
        cur_cell.alpha_minus[ii] = max([0, lambda_minus_cur, lambda_minus_r])
        # print(cur_cell.alpha_minus)

    for ii in range(3):
        cur_cell.F_half[ii] = (cur_cell.alpha_plus[ii]*cur_cell.F[ii] + cur_cell.alpha_minus[ii]*r_cell.F[ii]
        - cur_cell.alpha_plus[ii]*cur_cell.alpha_minus[ii]*(r_cell.U[ii]-cur_cell.U[ii])) \
        / (cur_cell.alpha_plus[ii] + cur_cell.alpha_minus[ii])

    return cur_cell.F_half


# find U value at next time step given left, right, current cell at current time
def find_u_later(cur_cell, l_cell, r_cell, dx, dt):
    u_temp = [0, 0, 0]
    for ii in range(3):
        du = -(find_f_half(cur_cell, r_cell)[ii] - find_f_half(l_cell, cur_cell)[ii]) / dx
        u_temp[ii] = cur_cell.U[ii] + dt * du
    return u_temp


# find F value at next time step given U of current cell at next time step
def find_f_later(cur_cell_later):
    f_temp = [0, 0, 0]
    p = find_p(cur_cell_later)
    f_temp[0] = cur_cell_later.U[1]
    f_temp[1] = cur_cell_later.U[1] ** 2 / cur_cell_later.U[0] + p
    f_temp[2] = (cur_cell_later.U[2] + p) * cur_cell_later.U[1] / cur_cell_later.U[0]
    # print(P)
    return f_temp


# loop all things together
for t in range(nt-1):
    for i, cell in enumerate(grid_cur[t][1:nx-1]):
        i += 1
        left_cell = grid_cur[t][i-1]
        right_cell = grid_cur[t][i+1]
        current_cell = grid_cur[t][i]
        current_cell_later = grid_cur[t+1][i]


        current_cell_later.U = find_u_later(current_cell, left_cell, right_cell, delta_x, delta_t)
        current_cell_later.F = find_f_later(current_cell)


rho_map_cur = plot_grid(grid_cur, nt, nx)
# plot_3d(rho_map_cur)
# plt.show(rho_map_cur)