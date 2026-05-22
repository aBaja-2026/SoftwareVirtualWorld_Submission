
sim_params = cmapi.Parametrization()
sim_params.set_path(pathlib.Path("Data/Config/SimParameters"))
cmapi.Project.instance().load_parametrization(sim_params)
sim_params.set_parameter_value("DStore.BufSize_kB", 131072)
cmapi.Project.instance().write_parametrization(sim_params)