import os
import pyarrow as pa
import pyarrow.parquet as pq
import pandas as pd

def read_arrow_file(arrow_path):
    """
    读取一个 .arrow 文件，并返回一个 Pandas DataFrame。
    
    参数:
    - arrow_path (str): .arrow 文件的路径。
    
    返回:
    - pandas.DataFrame: 包含 .arrow 文件数据的 DataFrame。
    """
    # 打开 .arrow 文件
    with pa.memory_map(arrow_path, 'r') as source:
        # 创建一个 Table 读取器
        table = pa.ipc.RecordBatchFileReader(source)
        # 将 Arrow Table 转换为 Pandas DataFrame
        dataframe = table.read_all().to_pandas()
    return dataframe

def read_multiple_arrow_files(directory):
    """
    读取一个文件夹中的所有 .arrow 文件，并合并为一个 Pandas DataFrame。
    
    参数:
    - directory (str): 包含 .arrow 文件的文件夹路径。
    
    返回:
    - pandas.DataFrame: 包含所有 .arrow 文件数据的合并 DataFrame。
    """
    dataframes = []
    for filename in os.listdir(directory):
        if filename.endswith('.arrow'):
            arrow_path = os.path.join(directory, filename)
            df = read_arrow_file(arrow_path)
            dataframes.append(df)
    # 合并所有 DataFrame
    final_dataframe = pd.concat(dataframes, ignore_index=True)
    return final_dataframe

# 示例用法
arrow_dir = '/home1/qbs/my_program1/HunyuanDiT/dataset/porcelain/arrows/'
combined_df = read_multiple_arrow_files(arrow_dir)
print(combined_df.head())
