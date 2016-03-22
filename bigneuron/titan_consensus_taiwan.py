__author__ = 'xiaoxiaol'
__author__ = 'xiaoxiaol'
__author__ = 'xiaoxiaoliu'



import pandas as pd
import os
import sys
import platform

if (platform.system() == "Linux"):
    WORK_PATH = "/local1/xiaoxiaol/work"
else:
    WORK_PATH = "/Users/xiaoxiaoliu/work"


p =  WORK_PATH + '/src/morphology_analysis'
sys.path.append(p)
import pandas as pd
import numpy as np
import os
import blast_neuron.blast_neuron_comp as bn


#random 500

def gen_txt_job_script(cmd, job_fn):
    output_dir = os.path.dirname(job_fn)
    if not os.path.exists(output_dir):
        os.system("mkdir -p  " + output_dir)
        print "create output dir: ", output_dir

    FILE = open(job_fn, 'w')

    FILE.write("%s\n" % cmd)

    FILE.close()


#data_DIR = "/lustre/atlas2/nro101/proj-shared/BigNeuron/data/taiwan16k/reconstructions_for_img_anisosmooth"
#output_dir =  "/lustre/atlas2/nro101/proj-shared/BigNeuron/data/taiwan16k/consensus_0306_anisosmooth"
data_DIR = "/lustre/atlas2/nro101/proj-shared/BigNeuron/data/taiwan16k/reconstructions_for_img_nopreproprcessing"
output_dir =  "/lustre/atlas2/nro101/proj-shared/BigNeuron/data/taiwan16k/consensus_0308_random500"
#fn_list = '~/work/data/image_file_name_list.csv'
image_DIR="/lustre/atlas2/nro101/proj-shared/BigNeuron/data/taiwan16k/img_nopreproprcessing"


fn_list = '~/work/data/taiwan_image_file_name_list.csv'

df_nd = pd.read_csv(fn_list)
images = np.unique(df_nd['image_file_name'])


dfg = df_nd.groupby('image_file_name')
os.system('rm -r ./txt_jobs')
os.system('mkdir ./txt_jobs')

count = 0
random_ids = np.random.randint(1,15921,500)
for im in images[random_ids]:


     out_dir = output_dir
     input_dir =data_DIR+'/'+im

     im_id = im.split('.')[0] # just the id to avoid long names

     output_eswc_path = out_dir+'/'+im_id+'_consensus.eswc'
     logfile = output_eswc_path+".log"
     line1 = "./start_vaa3d.sh -x consensus_swc -f consensus_swc -i " +  input_dir +"/*.swc   -o " + output_eswc_path + " -p 2 10 > "+logfile

     #image_file = image_DIR+ '/'+ im[:-7]+'/'+im
     image_file = image_DIR+'/'+im+'/'+im
     output_eswc_path2 =  out_dir+'/'+im_id+'_consensus_pruned.eswc'
     logfile2 = output_eswc_path2+".log"
     line2 = "./start_vaa3d.sh -x consensus_swc -f dark_pruning -i " + output_eswc_path + " "+ image_file + " -o " + output_eswc_path2 + " -p  40 > "+logfile2

     line3 = "./start_vaa3d.sh -x consensus_swc -f median_swc -i "+ input_dir +"/*.swc  "+ output_eswc_path2 +" -o "+  out_dir+"/"+im_id+"_median_distances.csv"
     line4 = "./start_vaa3d.sh -x consensus_swc -f median_swc -i "+ input_dir +"/*.swc  "+ output_eswc_path +" -o "+  out_dir+"/"+im_id+"_nonprune_median_distances.csv"

     job_fn = './txt_jobs/'+str(count)+'.txt'
     FILE = open(job_fn, 'w')
     FILE.write("%s;" % line1)
     FILE.write("%s;" % line2)
     FILE.write("%s;" % line3)
     FILE.write("%s\n" % line4)
     FILE.close()

     count = count +1


os.system('tar -zcvf ./txt_jobs.tar.gz ./txt_jobs/')
