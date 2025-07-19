#!/usr/bin/env python

import os
import shutil
mode = 182

WORK_DIR=os.getcwd()

for i in range(mode):
        os.mkdir(str(i+1))
        if i+1 < 10:
                original = WORK_DIR+'/POSCAR-00'+str(i+1)
        elif i+1 >= 10 and i+1 < 100:
                original = WORK_DIR+'/POSCAR-0'+str(i+1)
        else:
                original = WORK_DIR+'/POSCAR-'+str(i+1)

        target_pos = WORK_DIR+'/'+str(i+1)+'/POSCAR'
        target_input = WORK_DIR+'/'+str(i+1)

        shutil.move(original, target_pos)
        shutil.copy(WORK_DIR+'/INCAR', target_input)
        shutil.copy(WORK_DIR+'/KPOINTS', target_input)
        shutil.copy(WORK_DIR+'/POTCAR', target_input)	
