from fmpy import read_model_description, extract
from typing import Dict
import shutil
from fmpy.fmi2 import FMU2Slave
from fmpy.model_description import ScalarVariable
from cosimlibrary.autoinit import AutoInit


class LoadedFMU(AutoInit):
    fmu: FMU2Slave = None
    dir: str = None
    vars: Dict[str, ScalarVariable] = None


class FMULoader:

    @staticmethod
    def get_vars(model_description):
        vrs = {}
        for variable in model_description.modelVariables:
            vrs[variable.name] = variable
        return vrs

    @staticmethod
    def load(fmu_path, instance_name, logger):
        unzipdir = extract(fmu_path)
        desc = read_model_description(fmu_path)
        vars = FMULoader.get_vars(desc)
        fmu = FMU2Slave(guid=desc.guid,
                        unzipDirectory=unzipdir,
                        modelIdentifier=desc.coSimulation.modelIdentifier,
                        instanceName=instance_name,
                        fmiCallLogger=logger)
        return LoadedFMU(fmu=fmu, dir=unzipdir, vars=vars)

    @staticmethod
    def unload(loaded_fmu: LoadedFMU):
        loaded_fmu.fmu.freeInstance()
        try:
            shutil.rmtree(loaded_fmu.dir)
        except PermissionError:
            print("Warning: failed to clear directory ", loaded_fmu.dir)






