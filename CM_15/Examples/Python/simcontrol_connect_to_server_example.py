import cmapi
from cmapi import SimControlInteractive
from cmapi import ApoServer, Application

from parametrization_full_example import make_variations


async def start_application(host):

    application = Application.create(cmapi.AppType.CarMaker)
    application.set_host(host)
    await application.start()

    return application


async def stop_application(application):
    await application.stop()


async def main():

    variation, variation_trailer = await make_variations()
    variation.get_testrun().set_parameter_value("Vehicle", "Examples/Demo_IPG_CompanyCar")

    PID = None
    HOST = "localhost"

    # Start CarMaker application.
    # May be uncommented, if the application has already been started externally.
    application = await start_application(HOST)

    # Specify a pid to determine which server to connect to.
    # May be specified manually. We use the pid of the started CarMaker application.
    if not PID:
        PID = application.get_pid()

    # Create a handle to the apo server started with the CarMaker application.
    sinfo = cmapi.ApoServerInfo(pid=PID, description="Idle")

    master = ApoServer()
    master.set_sinfo(sinfo)
    master.set_host(HOST)

    # Use the fact, that 'master' can be either of type cmapi.CarMaker or cmapi.ApoServer.
    sim_control = await SimControlInteractive.create_with_master(master)
    sim_control.set_variation(variation)

    cmapi.logger.debug(f"Running servers on host: {cmapi.query_aposerverinfos(HOST)}")

    # Only connect, not start_and_connect.
    await sim_control.connect()
    await sim_control.start_sim()
    await sim_control.simstate.condition_finished.wait()
    await sim_control.disconnect()

    assert sim_control.sessionlog.get_entries_with_pattern("*SIM_END*BackAndForth*")

    # Stop the CarMaker application.
    await stop_application(application)


if __name__ == "__main__":
    cmapi.Task.run_main_task(main())