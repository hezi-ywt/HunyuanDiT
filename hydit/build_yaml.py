import os
import yaml
import re
import argparse

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
    # main()


    base_dir = '/data/images_200char_out_arrow'  # 您的基目录
    output_file = '/data/images_200char_out_arrow/source_config.yaml'
    
    repeat_dirs = extract_repeat_info(base_dir)
    generate_yaml(repeat_dirs, output_file)
