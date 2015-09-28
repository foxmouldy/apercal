def cal2srcs(settings=None):
	# Template for APERCAL Modules
	# 1: Report the name of the module, and check that settings and other variables have
	# been provided.
	logging.info("CAL2SRCS: Module to copy the gain table from a calibrator to the source visibilities")
	if settings is None:
	    logging.error("Settings Not Provided!")
	    sys.exit(0)
	# 2: Get the settings, check that the working directory is present and, if so, move to
	# it. 

	try:
	    os.chdir(settings.get('data', 'working'))
	    logging.info("Moved to path "+settings.get('data', 'working'))
	except:
	    logging.error("Error: path does not exist!")
	    sys.exit(0)

	# 3: Define local variables to match those in params for use in the module.  

	params = settings.get('data')
	cal2copy = params.cal2copy
	srcs = params.srcs
	# 4: Write the body of the code. 
	for s in srcs.split(';'):

		logging.debug("PUTHD: Adding /restfreq=1.420405752 to "+s)
		o = lib.basher(task='puthd', in_=s+'/restfreq', value='1.420405752')
		
		logging.debug('PUTHD: Adding /interval=1.0 to '+s)
		o = lib.basher(task='puthd', in_=s+'/interval', value='1.0', type='double')

		logging.info('GPCOPY: Copying gain tables from '+cal2copy+' to '+s)
		o = lib.basher(task='gpcopy', vis=cal2copy, out=s)
	logging.info("CAL2SRCS: Appears to have ended successfully.")


def cal2srcs(cal, settings):
    '''
    Cals = 'cal1,cal2'
    Srcs = 'src1,src2'
    '''
    srcs = params.srcs
        logging.info("CALCALS: MFCALS on all Calibrator Visibilities")
    if settings is None:
        logging.error("Settings Not Provided!")
        sys.exit(0)

    params = settings.get('mfcal')
    try:
        os.chdir(settings.get('data', 'working'))
        logging.info("Moved to path "+settings.get('data', 'working'))
    except:
        logging.error("Error: path does not exist!")
        sys.exit(0)

	params = settings.get('data')
	cal2copy = params.cal2copy

    for s in srcs.split(';'):
        #puthd = mirexec.TaskPutHead()
        #puthd.in_ = s+'/restfreq'
        #puthd.value = 1.420405752
        #o = puthd.snarf()

	o = lib.basher(task='puthd', in_=s+'/restfreq', value='1.420405752')

        puthd.in_ = s+'/interval'
        puthd.value = 1.0
        puthd.type = 'double'
        o = puthd.snarf()

        gpcopy  = mirexec.TaskGPCopy()
        gpcopy.vis = cal
        gpcopy.out = s
        o = gpcopy.snarf()
