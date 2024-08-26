import os
import time
import re
import schedule
from retrying import retry
import matplotlib.pyplot as plt
from huggingface_hub import HfApi
import numpy as np  # 导入 NumPy 库

# 设置 Hugging Face 终端点
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 函数：读取日志文件并绘图
def plot(dirname):
    log_file_path = os.path.join(dirname, 'log.txt')
    

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


# 函数：上传单个文件到 Hugging Face
@retry(stop_max_attempt_number=60, wait_fixed=60000)  # 最大重试5次，每次重试间隔60秒
def upload_single_file(local_file: str, repo_id="", file_dir=""):
    try:
        api = HfApi(token='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')
        print(f"HfApi准备完成,准备上传 {local_file}")
        res = api.upload_file(
            path_or_fileobj=local_file,
            path_in_repo=file_dir + "/" + os.path.basename(local_file),
            repo_id=repo_id,
            repo_type="model",
        )
        print(res)
    except Exception as e:
        print(str(e))
        raise e  # 继续抛出异常以便 retrying 库处理

# 函数：搜索本地目录中的文件列表
def search_file_list(dirname):
    file_list = []
    dir_name = os.path.join(dirname, "checkpoints")
    for dir in os.listdir(dir_name):
        if os.path.isdir(os.path.join(dir_name, dir)):
            file_name = os.path.join(dir_name, dir, "mp_rank_00_model_states.pt")
            if os.path.exists(file_name):
                file_list.append(file_name)

    # 绘制并保存损失图
    plot(dirname)
    plot_file = os.path.join(dirname, "plot_loss_train.png")
    if os.path.exists(plot_file):
        file_list.append(plot_file)
        
    return file_list

# 函数：上传文件列表
def upload_file_list(dirname, repo_id):
    file_list = search_file_list(dirname)
    if not file_list:
        print("No files found to upload.")
        return
    for file in file_list:
        upload_single_file(file, repo_id, file)

# 函数：定时任务
def scheduled_upload():
    try:
        upload_file_list("/home1/qbs/my_program1/HunyuanDiT/log_EXP/020-dit_g2_full_1024p", "heziiiii/laxbab_hydit")
    except Exception as e:
        print(f"Error during scheduled upload: {str(e)}")

if __name__ == "__main__":
    # 立即执行一次任务
    scheduled_upload()
    
    # 每五分钟执行一次上传任务
    schedule.every(2).hours.do(scheduled_upload)

    while True:
        schedule.run_pending()
        time.sleep(1)
