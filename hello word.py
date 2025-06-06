import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

def compute_next_generation(grid):
    # 计算下一代的逻辑（康威生命游戏规则）
    new_grid = grid.copy()
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            # 计算周围活细胞数
            total = int((
                grid[i, (j-1)%grid.shape[1]] + grid[i, (j+1)%grid.shape[1]] +
                grid[(i-1)%grid.shape[0], j] + grid[(i+1)%grid.shape[0], j] +
                grid[(i-1)%grid.shape[0], (j-1)%grid.shape[1]] + grid[(i-1)%grid.shape[0], (j+1)%grid.shape[1]] +
                grid[(i+1)%grid.shape[0], (j-1)%grid.shape[1]] + grid[(i+1)%grid.shape[0], (j+1)%grid.shape[1]]
            ))
            # 应用生命游戏规则
            if grid[i, j] == 1:
                if (total < 2) or (total > 3):
                    new_grid[i, j] = 0
            else:
                if total == 3:
                    new_grid[i, j] = 1
    return new_grid

def update(frame, img, grid, size):
    # 更新网格的逻辑
    new_grid = compute_next_generation(grid)
    img.set_array(new_grid)
    return [img]  # 关键修改：返回包含img的列表

# 初始化
grid_size = 50
grid = np.random.choice([0, 1], (grid_size, grid_size))
fig, ax = plt.subplots()
img = ax.imshow(grid, interpolation='nearest')

# 创建动画
ani = FuncAnimation(fig, update, fargs=(img, grid, grid_size),
                  frames=100, interval=200)

plt.show()
