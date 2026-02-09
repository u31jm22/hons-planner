import glob
import os
from tests.test_pddl_constants import TMP_FOLDER


def erase_tmp_files():
    for f in glob.glob(TMP_FOLDER+"/*.txt"):
        os.remove(f)
    for f in glob.glob(TMP_FOLDER+"/*.pddl"):
        os.remove(f)