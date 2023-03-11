import os
import sys

PROJECT_PATH = os.path.dirname(__file__)
SRC_PATH = os.path.join(PROJECT_PATH,'src')
sys.path.append(SRC_PATH)

import kindergarten.classroom.kfcv_img_classifier.train

if __name__=="__main__":
    kindergarten.classroom.kfcv_img_classifier.train.main()
