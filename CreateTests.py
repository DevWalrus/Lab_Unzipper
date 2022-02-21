import argparse
import glob
import os.path
import re
import shutil
from typing import List
from utils import *

TEST_CONFIG_TEMPLATE = open('../LabUnzipper/templates/test_config_template.xml', 'r').read()

def setup():
    default = argparse.ArgumentParser()
    default.add_argument('tests',
                         help='A folder holding some Junit tests to replace the students with. This ensures they are not modifying the tests to pass')
    default.add_argument('-d', '--directory',
                         help="A directory holding the student folders")
    return default.parse_args()

def set_test_global(contents : str):
    global TEST_CONFIG_TEMPLATE
    TEST_CONFIG_TEMPLATE = contents

def create_stu_tests(s_dir : str,
                     test_dirs : List[str],
                     configurations_dir : str) -> None:
    """
    Copies a bunch of tests from the test_dirs to the s_dir.

    :param s_dir: the directory of the students folder
    :param test_dirs: A list of test directories
    :param configurations_dir: A place to store the configurations once created
    :param verbose: if true, we will print out the creation of every student's tests
    """

    assert os.path.exists(configurations_dir) == True, "configurations_dir must be created"

    if not os.path.exists(os.path.join(s_dir, "./src/")):
        verbose_print(f"{s_dir}'s folder is not setup properly for test creation, must be done manually")
        return

    s_test_dir = os.path.join(s_dir, "src/test")
    if os.path.exists(s_test_dir):
        shutil.rmtree(s_test_dir)
    os.mkdir(s_test_dir)

    name = s_dir.split(', ')

    for i in range(len(test_dirs)):
        curr_test = test_dirs[i].split("\\")[-1]
        test_to_dir = os.path.join(s_test_dir, curr_test)
        shutil.copy(test_dirs[i], test_to_dir)
        test_name = curr_test[:-5]
        file_name = name[1][0] + name[0][0] + test_name + '.xml'

        config = TEST_CONFIG_TEMPLATE.format(
            test_name=file_name[:-4],
            module_name=s_dir,
            folder_name=s_dir,
            class_name=test_name
        )

        with open(os.path.join(configurations_dir, file_name), 'w') as config_xml_path:
            config_xml_path.write(config)
        vverbose_print(f"{s_dir}'s test ({test_name}) has been copied")

def main(argv):
    calling_dir = os.getcwd()

    working_dir = calling_dir
    if argv.directory is not None:
        working_dir = os.path.join(calling_dir, argv.directory)

    idea_dir = os.path.join(working_dir, ".idea/")
    configurations_dir = os.path.join(idea_dir, "runConfigurations/")

    tests_path = os.path.join(calling_dir, argv.tests)

    os.chdir(tests_path)

    test_files = glob.glob("*.java")

    test_dirs = []

    for i in range(len(test_files)):
        test_dirs.append(os.path.join(tests_path, test_files[i]))

    os.chdir(working_dir)

    stu_dirs = []
    for s_dir in os.listdir(working_dir):
        if re.match("[a-zA-Z-']+, [a-zA-Z-']+", s_dir):
            stu_dirs.append(s_dir)

    for s_dir in stu_dirs:
        create_stu_tests(s_dir, test_dirs, configurations_dir)

if __name__ == '__main__':
    argv = setup()
    main(argv)