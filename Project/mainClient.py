import logging
import multiprocessing
import client
import studentVideo
import time

def setupClientMain():
	logging.basicConfig(level=logging.DEBUG)
	pil_logger = logging.getLogger('PIL')
	pil_logger.setLevel(logging.INFO)
	logger = logging.getLogger("MAIN_CLIENT")

	name = input('Name: ')
	id_num = input('ID: ')

	logger.debug("initilaizing clients")
	logger.debug("Creating Q&A client")
	# spawn Q&A

	# spawn PORT SCAN
	logger.debug("Creating PORTSCAN client")
	process = multiprocessing.Process(target=client.run, args=(name, id_num))
	process.daemon = True
	process.start()
	
	# timer to give user time to enable permissions for port scan
	time.sleep(10)
	# run video in parent process
	logger.debug("Creating VIDEOSTREAM client")

	studentVideo.run(name, id_num)

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
	cv2.destroyAllWindows()
	out.release()
	logging.info("All done")

# make sure everything is closed when exited