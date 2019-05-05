# Wait until a state is reached.

def WaitForVolumeConversion(self, timeout=1200, retrialPeriod=60):
    """
    Wait for Volume conversion task status to complete of fail.
    :param timeout: wait time.
    :param retrialPeriod: probe time.
    :return: in case of success, raise on error.
    """
    startTime = time.time()
    remainingTime = timeout

    while remainingTime > 0:
        currentTime = time.time()
        remainingTime = timeout - (currentTime - startTime)

        # Wait for volume conversion task to complete.
        taskState = self.GetVolumeTaskStatus()

        # Example return values.
        # 'State': 'active'|'cancelling'|'cancelled'|'completed',

        if taskState == 'completed':
            self.logger.info("Volume Conversion {} complete in {}s". \
                             format(self.volumeTaskID, remainingTime))
            return

        # Raise in case exception occurred in pending operation.
        if taskState == 'cancelling' or taskState == 'cancelled':
            self.logger.error("Volume Conversion task abandoned with state{}". \
                              format(taskState))
            raise Exception("Volume Conversion task abandoned with state{}" \
                            .format(taskState))

        time.sleep(retrialPeriod)

    self.logger.debug("Timed out {}s waiting for Volume conversion Operation {}". \
                      format(timeout, self.volumeTaskID))
    raise Exception("Timed out waiting for Volume conversion Operation {}" \
                    .format(self.volumeTaskID))
