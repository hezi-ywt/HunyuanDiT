import os
import subprocess

import yaml
import re
import argparse

from tqdm import tqdm



def convert_csv_to_arrow(csv_file, output_dir):
    try:
        #两个版本
        subprocess.run(['python', './hydit/data_loader/csv2arrow.py', csv_file, output_dir, '8'], check=True)
        #subprocess.run(['python', './hydit/data_loader/csv2arrow.py', csv_file, output_dir], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting {csv_file}: {e}")
        return False

# def batch_convert_csv_to_arrow(csv_dir, output_dir, max_workers=8):
#     csv_files = [os.path.join(csv_dir, file) for file in os.listdir(csv_dir) if file.endswith('.csv')]
    
#     with ThreadPoolExecutor(max_workers=max_workers) as executor:

#         futures = {executor.submit(convert_csv_to_arrow, csv_file, os.path.join(output_dir,os.path.splitext(os.path.basename(csv_file))[0])): csv_file for csv_file in csv_files}
        
#         for future in tqdm(as_completed(futures), total=len(futures), desc="Converting CSV files"):
#             csv_file = futures[future]
#             try:
#                 future.result()
#             except Exception as e:
#                 print(f"Error processing {csv_file}: {e}")


def extract_repeat_info(base_dir):
    repeat_dirs = []
    pattern = re.compile(r'^\d+(?=_)')
    
    for root, dirs, files in os.walk(base_dir):
        for dir_name in dirs:
            match = pattern.match(dir_name)
            if match:
                repeat_num = int(match.group(0))
                path = os.path.join(root, dir_name, '*.arrow')


                repeat_dirs.append({'path': path, 'repeat': repeat_num})
            
            else:
                repeat_num = 1
                path = os.path.join(root, dir_name, '*.arrow')
                repeat_dirs.append({'path': path, 'repeat': repeat_num})
    
    return repeat_dirs

def generate_yaml(repeat_dirs, output_file):
    data = {'source': []}

    for item in repeat_dirs:
        path = item['path']
        repeat = item['repeat']
        data['source'].append({path: {'repeat': repeat}})

    with open(output_file, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)

    print(f"YAML file '{output_file}' has been created.")

def main():
    parser = argparse.ArgumentParser(description="Generate YAML from repeat directories.")
    parser.add_argument('base_dir', type=str, help="Base directory containing repeat directories")
    parser.add_argument('output_file', type=str, help="Output YAML file path")
    
    args = parser.parse_args()
    
    repeat_dirs = extract_repeat_info(args.base_dir)
    generate_yaml(repeat_dirs, args.output_file)
    
    

if __name__ == "__main__":
    csv_dir = "/home1/qbs/my_program1/datahun2/base_out"
    output_dir = "/home1/qbs/my_program1/datahun2/base_out_arrow"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    csv_files = [os.path.join(csv_dir, file) for file in os.listdir(csv_dir) if file.endswith('.csv') or file.endswith('.json')]    
    
    for csv_file in tqdm(csv_files, desc="Converting CSV files"):
        convert_csv_to_arrow(csv_file, os.path.join(output_dir,os.path.splitext(os.path.basename(csv_file))[0]))

    repeat_dirs = extract_repeat_info(output_dir)
    generate_yaml(repeat_dirs, '/home1/qbs/my_program1/datahun2/base_out/base.yaml')