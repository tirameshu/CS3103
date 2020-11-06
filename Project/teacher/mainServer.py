import multiprocessing
import logging
import teacherVideo
import portScanServer

def setupServerMain():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("MAIN_SERVER")

    logger.debug("initilaizing servers")
    # spawn processes qna
    logger.debug("Creating Q&A server")

    # spawn processes port scan
    logger.debug("Creating PORTSCAN server")
    process = multiprocessing.Process(target=portScanServer.run)
    process.daemon = True
    process.start()

    # teacher video run in parent thread
    logger.debug("Creating VIDEOSTREAM server")
    teacherVideo.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    try:
        logging.info("Listening")
        setupServerMain()
    except:
        logging.exception("Unexpected exception")
    finally:
        logging.info("Shutting down")
        for process in multiprocessing.active_children():
            logging.info("Shutting down process %r", process)
            process.terminate()
            process.join()
    logging.info("All done")

# make sure everything is closed when exited
