#!/usr/bin/env python

import os

mode = 582
path = os.getcwd()
for i in range(mode):
	os.chdir(path+'/'+str(i+1))
        os.system('rm OUT* CHG* EI* WA* POTC* DOS*')
