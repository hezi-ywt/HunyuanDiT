# -*- coding: utf-8 -*-
import datetime
import gc
import os
import time
from multiprocessing import Pool
import subprocess
import pandas as pd
import pyarrow as pa
from tqdm import tqdm
import hashlib
from PIL import Image
import sys
import json

def parse_data(data):
    try:
        img_path = data[0]

        with open(img_path, "rb") as fp:
            image = fp.read()
            md5 = hashlib.md5(image).hexdigest()

        with Image.open(img_path) as f:
            width, height = f.size

        artist = ""
        character = ""
        character_zh = ""
        general = ""
        meta = ""
        copyright_tag = ""
        year = ""
        text_zh1 = ""
        text_zh2 = ""
        
        if len(data) == 3:
            kwargs = data[2]
            artist = kwargs.get('tag_artist', "")
            character = kwargs.get('tag_character', "")
            character_zh = kwargs.get('character_zh', "")
            general = kwargs.get('tag_general', "")
            meta = kwargs.get('tag_meta', "")
            copyright_tag = kwargs.get('tag_copyright', "")
            year = kwargs.get('year_tag', "")
            text_zh1 = kwargs.get('text_zh1', "")
            text_zh2 = kwargs.get('text_zh2', "")
            quality_tag = kwargs.get('quality_tag', "")
            rating_tag = kwargs.get('rating_tag', "")
            
        # print(f'artist:{artist} character:{character} character_zh:{character_zh} general:{general} meta:{meta} copyright:{copyright} year:{year}')
        return [data[1], md5, width, height, image, artist, character, character_zh, general, meta, copyright_tag, year, text_zh1, text_zh2, quality_tag, rating_tag]
    except Exception as e:
        print(f'Error: {e}')
        return


def make_arrow(csv_root, dataset_root, start_id=0, end_id=-1):
    print(csv_root)
    arrow_dir = dataset_root
    print(arrow_dir)

    if not os.path.exists(arrow_dir):
        os.makedirs(arrow_dir)

    data = pd.read_csv(csv_root)
    data = data[["image_path", "text_zh", "kwarg"]]
    columns_list = data.columns.tolist()
    columns_list.append("image")

    if end_id < 0:
        end_id = len(data)
    print(f'start_id:{start_id}  end_id:{end_id}')
    data = data[start_id:end_id]
    num_slice = 5000
    start_sub = int(start_id / num_slice)
    sub_len = int(len(data) // num_slice)  # if int(len(data) // num_slice) else 1
    subs = list(range(sub_len + 1))
    for sub in tqdm(subs):
        arrow_path = os.path.join(arrow_dir, '{}.arrow'.format(str(sub + start_sub).zfill(5)))
        if os.path.exists(arrow_path):
            continue
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} start {sub + start_sub}")

        sub_data = data[sub * num_slice: (sub + 1) * num_slice].values

        bs = pool.map(parse_data, sub_data)
        bs = [b for b in bs if b]
        print(f'length of this arrow:{len(bs)}')

        columns_list = ["text_zh", "md5", "width", "height", "image", "artist", "character", "character_zh", "general", "meta", "copyright", "year", "text_zh1", "text_zh2", "quality_tag", "rating_tag"]
        dataframe = pd.DataFrame(bs, columns=columns_list)
        table = pa.Table.from_pandas(dataframe)

        os.makedirs(dataset_root, exist_ok=True)
        with pa.OSFile(arrow_path, "wb") as sink:
            with pa.RecordBatchFileWriter(sink, table.schema) as writer:
                writer.write_table(table)
        del dataframe
        del table
        del bs
        gc.collect()

def make_arrow_from_json(json_root, dataset_root, start_id=0, end_id=-1):
    print(json_root)
    arrow_dir = dataset_root
    print(arrow_dir)

    if not os.path.exists(arrow_dir):
        os.makedirs(arrow_dir)

    with open(json_root, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 创建 DataFrame
    data = pd.DataFrame(data)
    data = data[["image_path", "text_zh", "kwarg"]]
    columns_list = data.columns.tolist()
    columns_list.append("image")

    if end_id < 0:
        end_id = len(data)
    print(f'start_id:{start_id} end_id:{end_id}')
    data = data[start_id:end_id]
    num_slice = 5000
    start_sub = int(start_id / num_slice)
    sub_len = int(len(data) // num_slice)
    subs = list(range(sub_len + 1))

    for sub in tqdm(subs):
        arrow_path = os.path.join(arrow_dir, '{}.arrow'.format(str(sub + start_sub).zfill(5)))
        if os.path.exists(arrow_path):
            continue
        print(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} start {sub + start_sub}")

        sub_data = data[sub * num_slice: (sub + 1) * num_slice].values

        with Pool(pool_num) as pool:
            bs = pool.map(parse_data, sub_data)
        bs = [b for b in bs if b]
        print(f'Length of this arrow: {len(bs)}')

        columns_list = ["text_zh", "md5", "width", "height", "image", "artist", "character", "character_zh", "general", "meta", "copyright", "year", "text_zh1", "text_zh2", "quality_tag", "rating_tag"]
        
        dataframe = pd.DataFrame(bs, columns=columns_list)
        table = pa.Table.from_pandas(dataframe)

        os.makedirs(dataset_root, exist_ok=True)
        with pa.OSFile(arrow_path, "wb") as sink:
            with pa.RecordBatchFileWriter(sink, table.schema) as writer:
                writer.write_table(table)
        del dataframe
        del table
        del bs
        gc.collect()



if __name__ == '__main__':

    if len(sys.argv) != 4:
        print("Usage: python hydit/data_loader/csv2arrow.py ${csv_root} ${output_arrow_data_path} ${pool_num}")
        print("csv_root: The path to your created CSV file. For more details, see https://github.com/Tencent/HunyuanDiT?tab=readme-ov-file#truck-training")
        print("output_arrow_data_path: The path for storing the created Arrow file")
        print("pool_num: The number of processes, used for multiprocessing. If you encounter memory issues, you can set pool_num to 1")
        sys.exit(1)
    csv_root = sys.argv[1]
    output_arrow_data_path = sys.argv[2]

    pool_num = int(sys.argv[3])
    pool = Pool(pool_num)
    
    if csv_root.endswith('.csv'):
        make_arrow(csv_root, output_arrow_data_path)
    
    elif csv_root.endswith('.json'):
        make_arrow_from_json(csv_root, output_arrow_data_path)
    
    else:   
        print("The input file format is not supported. Please input a CSV or JSON file.")
        sys.exit(1)
