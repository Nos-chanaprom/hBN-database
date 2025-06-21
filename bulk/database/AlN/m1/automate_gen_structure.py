import os

def find_folders_with_contcar(directory='.'):
    folders = []
    for root, dirs, files in os.walk(directory):
        if 'CONTCAR' in files:
            folders.append(root)
    return folders

def execute_cif2cell_command(folders):
    initial_dir = os.getcwd()
    for folder in folders:
        try:
            os.chdir(folder)
            os.system('vasp2cif CONTCAR')
            os.system('cif2cell -f CONTCAR.cif --cartesian -p VASP POSCAR')
            os.system('mv CONTCAR CONTCAR_fractional')
            os.system('mv POSCAR CONTCAR_cartesian')
            os.system('mv CONTCAR.cif structure.cif')
            add_atom = '''awk 'NR==1 {sub(/^.*order:/, "", $0); line=$0} FNR==6 {$0=line"\\n"$0} 1' CONTCAR_cartesian CONTCAR_cartesian > temp && mv temp CONTCAR_cartesian'''
            os.system(add_atom)
        except Exception as e:
            print(f"Error occurred in directory: {folder}. Error: {e}. Skipping to the next directory.")
        finally:
            os.chdir(initial_dir)

if __name__ == "__main__":
    folders_with_contcar = find_folders_with_contcar()
    num_folders = len(folders_with_contcar)
    print(f"Number of folders containing CONTCAR: {num_folders}")

    execute_cif2cell_command(folders_with_contcar)

