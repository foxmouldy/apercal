def module_template(settings=None):
	# Template for APERCAL Modules
	# 1: Report the name of the module, and check that settings and other variables have
	# been provided.
	logging.info("<Name of Module>: <1-Line Description of Module>")
	if settings is None:
	    logging.error("Settings Not Provided!")
	    sys.exit(0)
	# 2: Get the settings, check that the working directory is present and, if so, move to
	# it. 

	params = settings.get('<SECTION>')
	try:
	    os.chdir(settings.get('data', 'working'))
	    logging.info("Moved to path "+settings.get('data', 'working'))
	except:
	    logging.error("Error: path does not exist!")
	    sys.exit(0)

	# 3: Define local variables to match those in params for use in the module.  
	
	# 4: Write the body of the code. 
