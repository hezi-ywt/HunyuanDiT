# export CUDA_VISIBLE_DEVICES=1,2

# python -m pip install -r requirements.txt
# # 或者将所有权更改为当前用户
# sudo chown $(whoami) /path/to/directory

export CUDA_VISIBLE_DEVICES=0,1,2

export PATH=/usr/local/cuda-11.7/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11.7/lib64:$LD_LIBRARY_PATH

# # 3 Data conversion 
# python ./hydit/data_loader/csv2arrow.py /home1/qbs/my_program1/HunyuanDiT/data1/mmd/1_mmd.csv /home1/qbs/my_program1/HunyuanDiT/data1/arrows 1
 # Single Resolution Data Preparation
# idk base -c dataset/yamls/porcelain.yaml -t dataset/porcelain/jsons/porcelain.json

#  # Multi Resolution Data Preparation     
# idk multireso -c dataset/yamls/porcelain_mt.yaml -t dataset/porcelain/jsons/porcelain_mt.json

PYTHONPATH=./ sh hydit/train.sh --index-file dataset/porcelain/jsons/porcelain_mt.json --multireso --reso-step 64