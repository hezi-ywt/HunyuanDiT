import re
import matplotlib.pyplot as plt
import numpy as np  # 导入 NumPy 库
import os

# 读取日志文件路径
log_file_path = '/home1/qbs/my_program1/HunyuanDiT/log_EXP/020-dit_g2_full_1024p/log.txt'

# 读取日志文件
with open(log_file_path, 'r', encoding='utf-8') as file:
    log_lines = file.readlines()

# 正则表达式匹配训练损失和步数
loss_pattern = re.compile(r'Train Loss: ([0-9.]+)')
step_pattern = re.compile(r'step=([0-9]+)')

steps = []
losses = []

# 解析日志文件
for line in log_lines:
    loss_match = loss_pattern.search(line)
    step_match = step_pattern.search(line)
    if loss_match and step_match:
        loss = float(loss_match.group(1))
        step = int(step_match.group(1))
        losses.append(loss)
        steps.append(step)

# 计算平均损失
avg_losses = []
avg_steps = []
window_size = 24  # 设置窗口大小为32步

for i in range(0, len(losses), window_size):
    window_end = min(i + window_size, len(losses))
    avg_loss = sum(losses[i:window_end]) / (window_end - i)
    # 取窗口中间的步数
    avg_step = steps[i + (window_end - i) // 2]
    avg_losses.append(avg_loss)
    avg_steps.append(avg_step)

# 拟合平均损失的直线
coeffs = np.polyfit(avg_steps, avg_losses, 1)  # 一次多项式拟合
linear_fit = np.polyval(coeffs, avg_steps)     # 计算拟合值

# 绘制训练损失图
plt.figure(figsize=(12, 6))
plt.plot(steps, losses, label='Train Loss', alpha=0.5)
plt.plot(avg_steps, avg_losses, label='Average Train Loss', color='red')
plt.plot(avg_steps, linear_fit, label='Fitted Line', linestyle='--', color='blue')  # 添加拟合直线
plt.xlabel('Steps')
plt.ylabel('Loss')
plt.title('Training Loss and Average Training Loss Over Time')
plt.legend()
plt.grid(True)
plt.show()

# 保存绘制的图像
output_path = os.path.join(os.path.dirname(log_file_path), 'plot_loss_train.png')
plt.savefig(output_path)
print(f'Plot saved to {output_path}')
