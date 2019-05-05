# Wait until a state is reached.

import time

def WaitForVolumeConversion(func, desiredState, unexpectedState, timeout=1200, retrialPeriod=60, \
                            retrialCount=20, raiseOnError=False, description=""):
    """
    Wait for Volume conversion task status to complete of fail.
    :param func: function to be called for getting required state.
    :param desiredState: Desired state to be reached within time.
    :param unexpectedState: Unexpected state.
    :param timeout: wait time.
    :param retrialPeriod: probe time.
    :param retrialCount: number of times retrial is wanted.
    :param raiseOnError: Raise in case function raises error.
    :return: in case of success, raise on error.
    """
    startTime = time.time()
    remainingTime = timeout
    
    retrialRemain = retrialCount

    while remainingTime > 0 and retrialRemain > 0:
        currentTime = time.time()
        remainingTime = timeout - (currentTime - startTime)

        # Wait for expected state to be reached.
        try:
            taskState = func(*args, **kwargs)
        expect:
            if raiseOnError:
                raise Exception("Internal error while calling function")
        
        retrialRemain -= 1

        if taskState == desiredState:
            logger.info("Expected state reached {} complete in {}s". \
                             format(desiredState, remainingTime))
            return

        # Raise in case exception occurred in pending operation.
        if taskState == unexpectedState:
            logger.error("Waiting task abandoned with state{}". \
                              format(taskState))
            raise Exception("Waiting task abandoned with state{}" \
                            .format(taskState))

        time.sleep(retrialPeriod)

    if remainingTime > 0:
        logger.debug("Timed out {}s waiting for Operation {}". \
                          format(timeout, desiredState))
        raise Exception("Timed out waiting for  Operation {}" \
                        .format(desiredState))
        
    if retrialRemain > 0
        logger.debug("Retrial count hit while waiting for operation {}". \
                          format(desiredState))
        raise Exception ("Retrial count hit while waiting for operation {}". \
                          format(desiredState))
