import cmapi
import pathlib


async def make_variations():
    project_path = pathlib.Path("path/to/CM/project")
    cmapi.Project.load(project_path)

    testrun_path = pathlib.Path("Examples/BasicFunctions/Driver/BackAndForth")
    testrun = cmapi.Project.instance().load_testrun_parametrization(testrun_path)

    vehicle_path = pathlib.Path("Examples/DemoCar_SensorRadarRSI")
    vehicle = cmapi.Project.instance().load_vehicle_parametrization(vehicle_path)

    trailer_path = pathlib.Path("Examples/HorseTrailer")
    trailer = cmapi.Project.instance().load_trailer_parametrization(trailer_path)

    # Select vehicle by modifying the Parameter 'Vehicle' of the TestRunParametrization object.
    # This Parameter corresponds with the InfoFile key 'Vehicle' in the Test Run InfoFile.
    testrun.set_parameter_value("Vehicle", vehicle)

    # Make a variation containing a copy of the Test Run
    variation = cmapi.Variation.create_from_testrun(testrun.clone())
    variation.set_name("Variation")

    # Make a variation containing a trailer
    variation_trailer = variation.clone()
    variation_trailer.set_name("Variation with Trailer")

    # Append trailer by key value for this variation
    kvalues = []
    kvalues.append(cmapi.KeyValue(cmapi.Category.TestRun, "Trailer", trailer))
    variation_trailer.set_kvalues(kvalues)

    return [variation, variation_trailer]


async def main():
    variations = await make_variations()
    for variation in variations:

        cmapi.logger.info(f"Test Run parametrization of variation {variation.get_name()}:")
        param_string = []
        for parameter in variation.get_testrun().params_by_key.values():
            param_string.append(f"{parameter.key} : {parameter.value}")

        cmapi.logger.info("\n".join(param_string))



if __name__ == "__main__":
    cmapi.Task.run_main_task(main())

