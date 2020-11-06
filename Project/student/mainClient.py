import logging
import multiprocessing
import portScanClient
import studentVideo
import qnaClient
import time

def setupClientMain():
	logging.basicConfig(level=logging.DEBUG)
	logger = logging.getLogger("MAIN_CLIENT")

	name = input('Name: ')
	id_num = input('ID: ')

	logger.debug("initilaizing clients")
	logger.debug("Creating Q&A client")
	
	# spawn PORT SCAN
	logger.debug("Creating PORTSCAN client")
	process = multiprocessing.Process(target=portScanClient.run, args=(name, id_num))
	process.daemon = True
	process.start()

	logger.debug("You have 10 seconds before exam begins")
	# timer to give user time to enable permissions for port scan
	time.sleep(10)

	# soawn video
	logger.debug("Creating VIDEOSTREAM client")
	process = multiprocessing.Process(target=studentVideo.run, args=(name, id_num))
	process.daemon = True
	process.start()

	# spawn Q&A in parent process
	qnaClient.run(name, id_num)

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG)
	try:
		logging.info("Listening")
		setupClientMain()
	except:
		logging.exception("Unexpected exception")
	finally:
		logging.info("Shutting down")
		for process in multiprocessing.active_children():
			logging.info("Shutting down process %r", process)
			process.terminate()
			process.join()
	out.release()
	logging.info("All done")

# make sure everything is closed when exited