import os
import glob
import pandas as pd 
import numpy as np
from scipy import stats

class csv_analysis:
    
    def search_for_folder(self,folder):
        if os.path.exists(folder):
            self.name = folder[folder.rfind(os.path.sep)+1:folder.rfind('_')]
            print(f'Found directory {folder},\nGenenerating output file {self.name}.csv')
            self.input_dir = os.path.join(os.getcwd(),folder)
            return True

        else:
            print('This directory does not exist)')
            return False

    def prepare_container(self, keys):
        stats = dict()
        stats['folder name'] = []
        for key in keys:
            stats[key] = []
            stats[key + " error"] = []
            stats[key + " var"] = []
            stats[key + " std"] = []


        return stats

    def generate_folder_name(self,csv_file):
        name = csv_file.lower()
        
        if name.find('pos0') != -1:
            name = name[0:name.find('pos0')-1]
            return name[name.rfind(os.path.sep)+1:].upper()
        
        name = name[0:name.rfind(os.path.sep)-1]
        return name[name.rfind(os.path.sep)+1:].upper()

    def search_csv(self):
        files_to_process = glob.glob(self.input_dir + os.path.sep +'**'+ os.path.sep + '*.csv', recursive=True)
        if len(files_to_process):
            # read the first found csv to gather the keys used 
            data = pd.read_csv(files_to_process[0])
            output_container = self.prepare_container(data.keys())
            
            for csv_file in files_to_process:
                data = pd.read_csv(csv_file)
                if 'folder name' in data.keys():
                    continue

                for key in data.keys():
                    output_container[key].append(np.mean(data[key]))
                    output_container[key + " error"].append(stats.sem(data[key]))
                    output_container[key + " var"].append(np.var(data[key]))
                    output_container[key + " std"].append(np.std(data[key]))
                output_container['folder name'].append(self.generate_folder_name(csv_file))
                data = None

            self.output_to_file( output_container)
            
    def output_to_file(self,stats):
        data = pd.DataFrame.from_dict(stats)
        data.to_csv(os.path.join(self.input_dir, self.name + '.csv'),index=False)

def main():
    extract = csv_analysis()
    found_folder = False

    while not found_folder:
        folder_name = input('Folder to be analyzed: ')
        found_folder = extract.search_for_folder(folder_name)
    extract.search_csv()

if __name__ == "__main__":
    main()