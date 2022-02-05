import argparse
import os.path
import re
import shutil
import xml.dom.minidom as md
DEFAULT_CONFIG_TEMPLATE = open('../LabUnzipper/templates/default_config_template.xml', 'r').read()
INPUT_CONFIG_TEMPLATE = open('../LabUnzipper/templates/input_config_template.xml', 'r').read()
PARAM_CONFIG_TEMPLATE = open('../LabUnzipper/templates/param_config_template.xml', 'r').read()

def setup():
    default = argparse.ArgumentParser()

    default.add_argument('-d', '--directory',
                         help="A subdirectory to create the configs for")
    default.add_argument('-c', '--config',
                         help='A config file (XML) used to setup the config(s). If something is provided for [-d DIRECTORY] the path for the config will be {os.getcwd()}\\{directory}\\{config}, if nothing is provided, the path used will be {os.getcwd()}\\{config}')
    default.add_argument('-i', '--iml',
                         help='An IML file used to setup the modules. If something is provided for [-d DIRECTORY] the path for the config will be {os.getcwd()}\\{directory}\\{iml}, if nothing is provided, the path used will be {os.getcwd()}\\{iml}')
    return default.parse_args()

def main(argv):
    calling_dir = os.getcwd()
    working_dir = calling_dir
    if argv.directory is not None:
        working_dir = os.path.join(calling_dir, argv.directory)
    config_path = os.path.join(working_dir, 'config.xml')
    if argv.config is not None:
        config_path = os.path.join(working_dir, argv.config)
    iml_path = os.path.join(calling_dir, "../LabUnzipper/templates/iml.iml")
    misc_path = os.path.join(calling_dir, "../LabUnzipper/templates/misc.xml")
    config_xml = md.parse(config_path)
    configs = config_xml.getElementsByTagName("config")
    class_name = config_xml.getElementsByTagName("MAIN_CLASS_NAME")[0].getAttribute("value")

    stu_dirs = []
    for s_dir in os.listdir(working_dir):
        if re.match("[a-zA-Z'-]+, [a-zA-Z'-]+", s_dir):
            stu_dirs.append(s_dir)

    idea_dir = os.path.join(working_dir, ".idea/")
    configurations_dir = os.path.join(idea_dir, "runConfigurations/")
    if not os.path.exists(configurations_dir):
        os.makedirs(configurations_dir)
    modules_dir = os.path.join(idea_dir, "modules.xml")
    misc_dir = os.path.join(idea_dir, "misc.xml")
    shutil.copy(misc_path, misc_dir)
    if not os.path.exists(idea_dir):
        os.makedirs(idea_dir)
    if not os.path.exists(modules_dir):
        shutil.copy(os.path.join(calling_dir, "../LabUnzipper/templates/modules.xml"), modules_dir)
    modules_xml = md.parse(modules_dir)
    modules_element = modules_xml.getElementsByTagName("modules")[0]

    for s_dir in stu_dirs:
        # Add to the modules.xml
        new_module = modules_xml.createElement("module")
        new_module.setAttribute("fileurl", f"file://$PROJECT_DIR$/{s_dir}/{s_dir}.iml")
        new_module.setAttribute("filepath", f"$PROJECT_DIR$/{s_dir}/{s_dir}.iml")
        modules_element.appendChild(new_module)

        # Create an IML
        stu_path = os.path.join(working_dir, s_dir)
        stu_iml_path = os.path.join(stu_path, s_dir + ".iml")
        shutil.copy(iml_path, stu_iml_path)

        # Create the configs
        for config in configs:
            c_type = config.getAttribute("type")
            if c_type == "input":
                config_name = s_dir + " auto " + config.getAttribute("name")
                name = s_dir.split(', ')
                file_name = name[0] + '_' + name[1] + '_auto_' + config.getAttribute("name") + '.xml'
                param = config.getElementsByTagName("PROGRAM_PARAMETERS")[0].getAttribute("value")
                input_dir = config.getElementsByTagName("INPUT_FILE")[0].getAttribute("value")
                config = INPUT_CONFIG_TEMPLATE.format(
                    config_name=config_name,
                    class_name=class_name,
                    module_name=s_dir,
                    param=param,
                    input_dir=input_dir,
                )
                with open(os.path.join(configurations_dir, file_name), 'w') as config_xml_path:
                    config_xml_path.write(config)
            elif c_type == "param":
                config_name = s_dir + " manual " + config.getAttribute("name")
                param = config.getElementsByTagName("PROGRAM_PARAMETERS")[0].getAttribute("value")
                name = s_dir.split(', ')
                file_name = name[0] + '_' + name[1] + '_manual_' + config.getAttribute("name") + '.xml'
                config = PARAM_CONFIG_TEMPLATE.format(
                    config_name=config_name,
                    class_name=class_name,
                    module_name=s_dir,
                    param=param,
                )
                with open(os.path.join(configurations_dir, file_name), 'w') as config_xml_path:
                    config_xml_path.write(config)
            else:
                config_name = s_dir + " default " + config.getAttribute("name")
                name = s_dir.split(', ')
                file_name = name[0] + '_' + name[1] + '_default_' + config.getAttribute("name") + '.xml'
                config = DEFAULT_CONFIG_TEMPLATE.format(
                    config_name=config_name,
                    class_name=class_name,
                    module_name=s_dir,
                )
                with open(os.path.join(configurations_dir, file_name), 'w') as config_xml_path:
                    config_xml_path.write(config)
    with open(modules_dir, "w") as fs:
        modules_xml.writexml(fs, newl='\n', addindent='  ')

if __name__ == '__main__':
    argv = setup()
    main(argv)