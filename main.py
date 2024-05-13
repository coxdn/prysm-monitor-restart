import asyncio
import signal
import subprocess
import datetime
from src.logger_init import logger
from src.settings import working_directory

global last_processing_time


async def run_process():
    global last_processing_time
    while True:
        cmd = [
            "prysm.bat", "beacon-chain",
            "--execution-endpoint=\\\\.\\pipe\\geth.ipc",
            "--mainnet",
            "--checkpoint-sync-url=https://beaconstate.info",
            "--genesis-beacon-api-url=https://beaconstate.info"
        ]

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        logger.info("Starting the process")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=working_directory,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
        )

        stdout_filename = f"logs/stdout_log_{timestamp}.txt"
        stderr_filename = f"logs/stderr_log_{timestamp}.txt"

        stdout_file = open(stdout_filename, "w", encoding='utf-8')
        stderr_file = open(stderr_filename, "w", encoding='utf-8')

        last_processing_time = datetime.datetime.now()

        async def log_stream(stream, file):
            global last_processing_time
            while True:
                line = await stream.readline()
                if line:
                    decoded_line = line.decode('utf-8', errors='replace')
                    file.write(decoded_line)
                    file.flush()
                    if ' msg="Processing blocks" batchSize=' in decoded_line\
                            or 'msg="Synced new block"' in decoded_line:
                        last_processing_time = datetime.datetime.now()
                else:
                    break

        async def monitor_activity():
            global last_processing_time
            while True:
                await asyncio.sleep(10)
                if (datetime.datetime.now() - last_processing_time).total_seconds() > 150:
                    logger.info("Process without activity for more than 150 seconds. Interruption...")
                    if process.returncode is None:
                        process.send_signal(signal.CTRL_BREAK_EVENT)
                        process.stdin.write('Y\n'.encode('utf-8'))
                        await asyncio.sleep(5)
                        # await process.stdin.drain()
                        # process.stdin.close()
                        logger.info("A stop signal has been sent. Waiting for process completion...")
                    else:
                        logger.info("The process has already been completed.")
                    return

        await asyncio.gather(
            log_stream(process.stdout, stdout_file),
            log_stream(process.stderr, stderr_file),
            monitor_activity()
        )

        await process.wait()
        logger.info("The process is over.")

        stdout_file.close()
        stderr_file.close()

        logger.info("Process restart...")
        await asyncio.sleep(2)

asyncio.run(run_process())
