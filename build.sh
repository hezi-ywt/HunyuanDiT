# python ./hydit/data_loader/csv2arrow.py  /home1/qbs/my_program1/datahun2/reg1.json  /home1/qbs/my_program1/datahun2/reg1_arrow 1
# python ./hydit/data_loader/csv2arrow.py  /home1/qbs/my_program1/datahun2/image-webp.json  /home1/qbs/my_program1/datahun2/image-webp_arrow 1
# python ./hydit/data_loader/csv2arrow.py  /home1/qbs/my_program1/datahun2/realistic_out1.json  /home1/qbs/my_program1/datahun2/realistic_out_arrow 1
# python ./hydit/data_loader/csv2arrow.py  /home1/qbs/my_program1/datahun2/cli_out_o.json  /home1/qbs/my_program1/datahun2/cli_out_o_arrow 1
# python ./hydit/data_loader/csv2arrow.py  /home1/qbs/my_program1/datahun2/nai_normal_s.json  /home1/qbs/my_program1/datahun2/nai_normal_s_arrow 1

 
 # Single Resolution Data Preparation
 idk base -c /home1/qbs/my_program1/datahun2/artist_out/artist.yaml -t dataset/porcelain/jsons/porcelain.json

 # Multi Resolution Data Preparation     
 idk multireso -c dataset/yamls/porcelain_mt.yaml -t dataset/porcelain/jsons/porcelain_mt.json