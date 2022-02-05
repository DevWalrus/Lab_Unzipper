from zipfile import ZipFile as zp
import glob
import os
import shutil
import argparse

FORMAT = '[0-9][0-9][0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9][0-9][0-9][0-9] - *, * - *.zip'

def setup():
	"""
	Does the inital setup of the arguments and parsing of them.
	"""
	verbose = argparse.ArgumentParser(add_help=False)

	verbose.add_argument("-v", "--verbose", 
		help="send messages about every extraction", action="store_true")

	default = argparse.ArgumentParser(prog="Lab Unzipper",
		description="Easily unzip student submissions.", parents=[verbose])

	default.add_argument("--version", action='version', version='%(prog)s 1.0')

	sub = default.add_subparsers(dest="mode")

	zip_s  = sub.add_parser("zip", parents=[verbose],
		help="extract using a zipped file holding the directory (usually the file downloaded from MyCourses)")
	zip_s.add_argument("file", 
		help="The file to be unzipped and used as the working directory")
	zip_s.add_argument("-r", "--remove", 
		help="remove the zip file holding the student zips (passing with no file passed in will do nothing)",
		action="store_true")
	zip_s.add_argument("-l", "--lab",
		help="Provide a name for overarching directory of student submissions (Some common examples are \"Lab\\ 01\" or \"In-Lab\\ 09\"")

	dir_s  = sub.add_parser("directory", aliases=['dir'], parents=[verbose],
		help="extract using a subdirectory of the student's zips")
	dir_s.add_argument("directory", 
		help="The subdirectory to holding the student's zipped files")

	argv = default.parse_args()
	return argv

def main(argv, ver):
	"""
	Finds all of the zip files and sends them to be processed. Once processed
	they will be removed. The user could provide a directory [-d DIRECTORY] in 
	order to call this routine on an already unzipped directory. They could 
	providea zip file [-z ZIP] which will tell the program to extract that and
	use that new directory as the collection of student zips. This has an 
	optional [-r] flag to remove the zip on completion of the initial 
	extraction. In the event that no arguments are passed, the program will 
	just assume the directory it was called in holds the student's files and 
	will attempt to extract them. 

	:param argv:	The possible options
	:param ver:		If true, will alert all commands to output print messages
					for every extraction
	"""
	calling_path = os.getcwd()
	if argv.mode == 'zip':
		if os.path.exists(os.path.join(calling_path, argv.file)):
			if argv.lab is not None:
				lab_dir = argv.lab
			else:
				lab_dir = argv.file[2:-4]
			with zp(argv.file, 'r') as uzip:
				if uzip.testzip() is not None:
					print(argv.file + 'is corrupted, please try downloading it again')
					print('Exiting...')
					exit(0)
				if ver:
					print('Extracting ' + argv.file + ' to ' + lab_dir + ' now...')
				uzip.extractall(lab_dir)
			if argv.remove:
				if ver:
					print("Removing the original Zip")
				os.remove(argv.file)
			os.chdir(os.path.join(calling_path, lab_dir))
		else:
			print(argv.file + ' was not found.')
			print('Exiting...')
			exit(0)


	if argv.mode == 'dir' or argv.mode == 'directory':
		path = os.path.join(calling_path, argv.directory)
		if os.path.isdir(path):
			if ver:
				print('Using ' + path + ' as the working directory')
			os.chdir(path)
		else:
			print(argv.directory + ' was not found.')
			print('Exiting...')
			exit(0)

	found = glob.glob(FORMAT)

	if len(found) == 0:
		print('No files matched the MyCourses format')

	for i in range(len(found)):
		name = found[i].split(' - ')[1]
		path = os.getcwd()
		path = os.path.join(path, name)
		extract_student(found[i], path, ver)
		rm_macosx(path)
		os.remove(found[i])

def extract_student(zip_dir, path, ver):
	"""
	Takes a zipped file (with the name in the format described above) and
	unzips it to a foder with a relative path of "/LastName, FirstName"

	This also removes old submissions, but relies on MyCourses to output
	the old versions with a number appended to them.

	:param zip_dir: The directory of the zipped file
    :param path: The absolute path of the unzipped file
	"""
	if os.path.isdir(path):
		if ver:
			print("Removing " + os.path.relpath(path) + "'s old version...")
		shutil.rmtree(path)

	with zp(zip_dir, 'r') as zip:
		if ver:
			print('Extracting ' + zip_dir + ' now...')
		zip.extractall(os.path.relpath(path))

def rm_macosx(path):
	"""
	Takes an absolute path of the student's submission and removes unnecessary
	MACOSX files.

    :param path: The absolute path of the unzipped file
	"""
	path = os.path.join(path, "__MACOSX")
	if os.path.isdir(path):
		shutil.rmtree(path)
		if os.path.isdir(path):
			print(path + " directory removal failed")

if __name__ == '__main__':
	argv = setup()
	if argv.mode == 'dir' or argv.mode == 'directory':
		argv.directory = argv.directory[:-1]	# For some reason an extra " is
												# appended to the end of the
												# directory name, so I just have
												# to remove it
	print(argv)
	main(argv, argv.verbose)
