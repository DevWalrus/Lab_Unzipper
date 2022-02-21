import argparse
import glob
import os.path
import re
import shutil
import xml.dom.minidom as md

from CreateTests import set_test_global, create_stu_tests
from utils import verbose_print, vverbose_print, set_verbosity

DEFAULT_CONFIG_TEMPLATE, INPUT_CONFIG_TEMPLATE, PARAM_CONFIG_TEMPLATE = "", "", ""
TEMPLATE_DICT = {}

def _test_create_file(_dir):
    if not os.path.exists(_dir):
        os.mkdir(_dir)

def setup():
    default = argparse.ArgumentParser()

    default.add_argument('config',
                         help="A config file (XML) used to setup the config(s). The path used to grab this will be " +
                              "{working_dir}\\{config}")
    default.add_argument('-d', '--directory',
                         help="The directory of the student's folders [This changes the working directory " +
                              "(working_dir) to be os.getcwd()\\{directory}]")
    default.add_argument('-t', '--tests',
                         help="An optional folder holding some Junit tests to replace the students with. (This " +
                              "ensures they are not modifying the tests to pass)")
    default.add_argument('-i', '--iml',
                         help='An IML file used to setup the modules. The path used will be {working_dir}\\{iml}')
    default.add_argument("--defaults",
                         help="The directory of the defaults, and templates folders")
    default.add_argument("-v", "--verbose", action="count", default=0,
                         help="set the verbosity level (initially silent)")
    return default.parse_args()

def _setup_templates(defaults_path : str):
    global DEFAULT_CONFIG_TEMPLATE
    global INPUT_CONFIG_TEMPLATE
    global PARAM_CONFIG_TEMPLATE
    global TEMPLATE_DICT

    templates_path = os.path.join(defaults_path, "./templates/")
    for file in ["default", "input", "param"]:
        _dir = os.path.join(templates_path, f"./{file}_config_template.xml")
        with open(_dir, 'r') as f:
            TEMPLATE_DICT[file] = f.read()

    test_dir = os.path.join(templates_path, "./test_config_template.xml")
    with open(test_dir, 'r') as f:
        set_test_global(f.read())

def add_stu_to_module(xml: md.Document, module_element : md.Node.ELEMENT_NODE, stu_dir : str) -> int:
    new_module = xml.createElement("module")
    new_module.setAttribute("fileurl", f"file://$PROJECT_DIR$/{stu_dir}/{stu_dir}.iml")
    new_module.setAttribute("filepath", f"$PROJECT_DIR$/{stu_dir}/{stu_dir}.iml")
    module_element.appendChild(new_module)
    for ele in module_element.getElementsByTagName("module"):
        if re.split('[/]+', ele.getAttribute("fileurl"))[2] == stu_dir:
            return 1
    return 0

def create_stu_iml(iml_path, s_dir, working_dir=os.getcwd()):
    stu_path = os.path.join(working_dir, s_dir)
    stu_iml_path = os.path.join(stu_path, s_dir + ".iml")
    shutil.copy(iml_path, stu_iml_path)

def main(argv):
    calling_dir = os.getcwd()       # Grab the current directory
    working_dir = calling_dir       # Initialize the working dir to the current dir
    test_files = []
    test_dirs = []
    if argv.tests is not None:
        tests_path = os.path.join(calling_dir, argv.tests)
        os.chdir(tests_path)
        test_files = glob.glob("*.java")
        test_dirs = []
        for i in range(len(test_files)):
            test_dirs.append(os.path.join(tests_path, test_files[i]))
        os.chdir(working_dir)
    if argv.directory is not None:  # Move the working dir to the provided dir if present
        working_dir = os.path.join(calling_dir, argv.directory)
    config_path = os.path.join(working_dir, argv.config)
    defaults_path = os.path.join(calling_dir, "../LabUnzipper/")
    if argv.defaults is not None:
        defaults_path = os.path.join(calling_dir, argv.defaults)
    _setup_templates(defaults_path)
    iml_path = os.path.join(defaults_path, "./defaults/iml.iml")
    config_xml = md.parse(config_path)
    configs = config_xml.getElementsByTagName("config")
    class_name = config_xml.getElementsByTagName("MAIN_CLASS_NAME")[0].getAttribute("value")

    stu_dirs = []
    for s_dir in os.listdir(working_dir):
        if re.match("[a-zA-Z-']+, [a-zA-Z-']+", s_dir):
            stu_dirs.append(s_dir)

    folders_to_make = ["./out/", "./output/", "./input/", "./.idea/"]

    for folder in folders_to_make:
        temp_dir = os.path.join(working_dir, folder)
        _test_create_file(temp_dir)

    idea_dir = os.path.join(working_dir, "./.idea/")

    modules_dir = os.path.join(idea_dir, "./modules.xml")
    configurations_dir = os.path.join(idea_dir, "./runConfigurations/")
    _test_create_file(configurations_dir)

    files_to_make = ["misc.xml", "modules.xml"]
    for file in files_to_make:
        temp_path = os.path.join(idea_dir, file)
        if not os.path.exists(temp_path):
            file_to_steal = os.path.join(defaults_path, "./defaults/" + file)
            shutil.copy(file_to_steal, temp_path)

    modules_xml = md.parse(modules_dir)
    modules_element = modules_xml.getElementsByTagName("modules")[0]

    os.chdir(working_dir)

    for s_dir in stu_dirs:
        if argv.tests is not None:
            create_stu_tests(s_dir, test_dirs, configurations_dir)

        # Add to the modules.xml
        if add_stu_to_module(modules_xml, modules_element, s_dir) == 0:
            verbose_print(f"ERROR:\tCould not add {s_dir} to the XML file")
        else:
            vverbose_print(f"Added\t{s_dir} to the XML file")

        # Create an IML
        if create_stu_iml(iml_path, s_dir, working_dir) == 0:
            verbose_print(f"ERROR:\tCould not make {s_dir}'s IML file")
        else:
            vverbose_print(f"Created\t{s_dir}'s IML file")

        # Create the configs
        for config in configs:
            c_type = config.getAttribute("type")
            if c_type == "input":
                input_dir = config.getElementsByTagName("INPUT_FILE")[0].getAttribute("value")
            if c_type == "param" or "input":
                param = config.getElementsByTagName("PROGRAM_PARAMETERS")[0].getAttribute("value")

            name = s_dir.split(', ')
            config_name = s_dir + "_" + config.getAttribute("name")
            file_name = name[1][0] + name[0][0] + config.getAttribute("name") + '.xml'
            config = TEMPLATE_DICT[c_type].format(
                config_name=config_name,
                class_name=class_name,
                module_name=s_dir,
                folder_name=s_dir,
                param="" if (c_type != "input" or "param") else param,
                input_dir="" if c_type != "input" else input_dir,
            )
            with open(os.path.join(configurations_dir, file_name), 'w') as config_xml_path:
                config_xml_path.write(config)
            vverbose_print(f"Added {config_name} to the configurations file")
        vverbose_print(f"Completed {s_dir}'s setup")
    with open(modules_dir, "w") as fs:
        modules_xml.writexml(fs, newl='\n', addindent='  ')
        vverbose_print(f"Updated the modules directory")


if __name__ == '__main__':
    _ = setup()             # temp variable to hold the args
    set_verbosity(_.verbose)
    main(_)