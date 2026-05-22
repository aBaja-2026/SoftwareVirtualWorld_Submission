from pathlib import Path

import cmapi
from cmapi import Runtime, Project, Variation


async def main():

    runtime = Runtime.create_default_runtime()                                  # Create the runtime

    project_path = Path("path/to/CM/project")
    Project.load(project_path)                                                  # Set Project directory

    testrun_path = Path("Examples/BasicFunctions/Driver/BackAndForth")
    testrun = Project.instance().load_testrun_parametrization(testrun_path)     # Load Testrun example

    variation = Variation.create_from_testrun(testrun)                          # Create a variation from testrun

    await runtime.queue_variation(variation)                                    # Pass variation to runtime queue

    await runtime.start()                                                       # Start runtime

    await runtime.wait_until_completed()                                        # Wait until the variation is completed
    cmapi.logger.info("All simulations finished")

    await runtime.stop()                                                        # Stop runtime


cmapi.Task.run_main_task(main())                                                # Create asynchronous scope
