from parametrization_full_example import *


async def main():
    variation, variation_trailer = await make_variations()

    cmapi.logger.info(f"Executing with Runtime sequential...")

    # Make a custom execution policy using a DVA read
    class DVAExecutionPolicy(cmapi.VariationExecutionPolicyInteractive):
        @classmethod
        async def run_variation(cls, variation):

            simcontrol = variation.get_simcontrol()
            await simcontrol.start_sim()

            condition = simcontrol.create_quantity_condition(lambda car_v: car_v > 10.0, "Car.v")
            await condition.wait()

            time_10, = await simcontrol.simio.dva_read_async("Time")
            cmapi.logger.info(f"{variation.get_name()}: Reached speed 10 m/s after {time_10} seconds")

            await simcontrol.await_condition(simcontrol.simstate.condition_finished)


    variation.set_execution_policy(DVAExecutionPolicy)
    variation_trailer.set_execution_policy(DVAExecutionPolicy)

    runtime = cmapi.Runtime.create_default_runtime()

    await runtime.queue_variation(variation)
    await runtime.queue_variation(variation_trailer)

    await runtime.start()
    await runtime.wait_until_completed()
    await runtime.stop()

    cmapi.logger.info(f"Execution with Runtime sequential finished.")

    cmapi.logger.info(f"Execution with Runtime in parallel...")

    pool = cmapi.StaticConfigResourcePoolCarMaker()
    pool.set_app_nodes([cmapi.AppNode.create(cmapi.get_hostname(), 0, 10)])

    runtime.set_resourcepool(cmapi.ResourceType.CarMaker, pool)

    variation.reset()
    variation_trailer.reset()

    await runtime.queue_variation(variation)
    await runtime.queue_variation(variation_trailer)

    await runtime.start()
    await runtime.wait_until_completed()
    await runtime.stop()

    cmapi.logger.info(f"Execution with Runtime parallel finished.")


if __name__ == "__main__":
    cmapi.Task.run_main_task(main())
