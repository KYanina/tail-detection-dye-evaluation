# Tail Detection Code
import os
import glob
import imageio
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

class mice_experiment:


    def __init__(self):
        self.processing_option = 1
        self.input_dir = os.getcwd()
        self.output_dir = os.getcwd()


    def prepare_stats_container(self):
        stats = dict()
        stats['tail_area'] = []
        stats['bright_area'] = []
        stats['max_value'] = []
        stats['min_value'] = []
        stats['mean_value'] = []
        stats['median_value'] = []    
        return stats

    ##############################################
    # Checking the folder and based on that      #
    # generates output folder                    #
    ##############################################
    def init_output_structure(self,folder):
        if os.path.exists(folder):
            print(f'Generating output directory {folder}_output')
            self.input_dir = os.path.join(os.getcwd(),folder)
            self.output_dir = os.path.join(os.getcwd(),folder + '_output')

            if not os.path.exists(self.output_dir):
                os.mkdir(self.output_dir)
            return True

        else:
            print('This folder does not exist, try another one ;)')
            return False    

    #########################################
    #########################################
    def perform_analysis(self):

        # Initial check of the files in the main folder
        stats = self.prepare_stats_container()
        stats = self.go_through_files(self.input_dir, self.output_dir, stats)
        self.output_stats(self.output_dir, stats)
        
        # retrieving all the files from the folder and all its subfolders
        for root, dirs, files in os.walk(self.input_dir):
            for folder in dirs:
                input_dir = os.path.join(root,folder)

                # created to output folder
    output_dir = os.path.join(self.output_dir,root[len(self.input_dir)+1:],folder)
                stats = self.prepare_stats_container()
                if not os.path.exists(output_dir):
                    os.mkdir(output_dir)

                # performs analysis for the folder    
                stats = self.go_through_files(input_dir,output_dir, stats)   

                # generates the files with the results
                self.output_stats(output_dir, stats)

    def go_through_files(self, input_dir, output_dir, stats):              
        files_to_process = glob.glob(input_dir + '\*.tif', recursive=True)
        print(f'Processing: {input_dir}')
        count = 0
        for path in files_to_process:
            try:
                data = imageio.imread(path).astype('uint16')
            except (ValueError,PermissionError):
                print(f'non accessible file. Skipping {path}')
                continue

            stats, whole_tail, local_image  = self.process_image(data,stats)
            count = count + 1
            if count % 500 == 0:
                count = 0
    imageio.imwrite(os.path.join(output_dir,path[path.rfind('\\')+1:-4]+'.png'),whole_tail)
    imageio.imwrite(os.path.join(output_dir,path[path.rfind('\\')+1:-4]+'_bright.png'),local_image)
            
        return stats    

    def normalize_data(self, data):
        return ((data - np.min(data)) / (np.max(data) - np.min(data)))*255

    ##################################################
    # Image processing                               #
    ##################################################
    def process_image(self, image, stats):
        # normalizeing the image
        local_image = np.copy(image/256)
        local_image = self.normalize_data(local_image)
        local_image = (local_image).astype(np.uint8) 

        threshold = np.quantile(local_image,0.72)
        whole_tail = np.copy(local_image)
        whole_tail[whole_tail < threshold] = 0

        stats['tail_area'].append(np.count_nonzero(whole_tail > 0))
        stats['max_value'].append(np.max(image[whole_tail > 0]))
        stats['min_value'].append(np.min(image[whole_tail > 0]))
        stats['median_value'].append(np.median(image[whole_tail > 0]))
        stats['mean_value'].append(np.mean(image[whole_tail > 0]))


        # extracting the brightest spots
        if self.processing_option == 1:
            threshold = np.quantile(local_image,0.90)
            local_image[local_image < threshold] = 0

            for i in range(0,512):
                column = local_image[:,i]
                threshold = np.quantile(column,0.93)
                column[column < threshold] = 0
                local_image[:,i]=column

        else:
            mean_value = np.mean(whole_tail[whole_tail > 0])
            percentage = 0.8
            threshold = np.max(local_image[whole_tail > 0]) -
             (np.max(local_image[whole_tail > 0]) 
              - mean_value) * percentage
            #print(mean_value,threshold,np.max(local_image[whole_tail > 0]))
            local_image[local_image < threshold] = 0
        stats['bright_area'].append(np.count_nonzero(local_image > 0))    
        return stats, whole_tail, local_image

    def output_stats(self, output_dir, stats):
        if len(stats['tail_area']) > 0:

        plt.figure()
        plt.plot(stats['tail_area'], marker='o', drawstyle="steps-post")
        ax = plt.gca()
        ax.ticklabel_format(useOffset=False)
        plt.savefig(os.path.join(output_dir,'tail_area.png'))
        plt.close()

        plt.figure()
        plt.plot(stats['mean_value'], marker='o', drawstyle="steps-post")
        ax = plt.gca()
        ax.ticklabel_format(useOffset=False)
        plt.savefig(os.path.join(output_dir,'mean_value.png'))
        plt.close()

        plt.figure()
        plt.plot(np.array(stats['tail_area'])/(512*512), marker='o', drawstyle="steps-post")
        ax = plt.gca()
        ax.ticklabel_format(useOffset=False)
        plt.savefig(os.path.join(output_dir,'tail_area_percentage.png'))
        plt.close()
            
        plt.figure()
        plt.plot(stats['bright_area'], marker='o', drawstyle="steps-post")
        ax = plt.gca()
        ax.ticklabel_format(useOffset=False)
        plt.savefig(os.path.join(output_dir,'m_bright_area.png'))
        plt.close()

        plt.figure()
        plt.plot(stats['max_value'], marker='o', drawstyle="steps-post")
        ax = plt.gca()
        ax.ticklabel_format(useOffset=False)
        plt.savefig(os.path.join(output_dir,'max_value.png'))
        plt.close()

        plt.figure()
        plt.plot(stats['min_value'], marker='o', drawstyle="steps-post")
        ax = plt.gca()
        ax.ticklabel_format(useOffset=False)
        plt.savefig(os.path.join(output_dir,'min_value.png'))
        plt.close()

        plt.figure()
        plt.plot(stats['median_value'], marker='o', drawstyle="steps-post")
        ax = plt.gca()
        ax.ticklabel_format(useOffset=False)
        plt.savefig(os.path.join(output_dir,'median_value.png'))
        plt.close() 

        plt.figure()
        plt.plot(np.array(stats['bright_area'])/np.array(stats['tail_area']), 
        marker='o', drawstyle="steps-post")
        ax = plt.gca()
        ax.ticklabel_format(useOffset=False)
            plt.savefig(os.path.join(output_dir,'percentage.png'))
        plt.close() 


        with open(os.path.join(output_dir,'data.csv'),'w') as f:
            f.write('tail area,bright area,max value,min value,median value,mean value\n')
            for i in range(0,len(stats['bright_area'])):
                f.write("%.1f,%.1f,%.1f,%.1f,%.1f,%.1f\n" % 
                (stats['tail_area'][i],stats['bright_area'][i],stats['max_value'][i]\
                ,stats['min_value'][i],stats['median_value'][i],stats['mean_value'][i]))


def main():

    extract = mice_experiment()
    found_folder = False

    while not found_folder:
        folder_name = input('Folder to be analyzed: ')
        found_folder = extract.init_output_structure(folder_name)

    which_filter = input('Do you want to use mean filtering? [y/n]')

    if which_filter == 'y' or which_filter == 'Y':
        extract.processing_option = 2

    # start going through files     
    extract.perform_analysis()

if __name__ == "__main__":
    main()