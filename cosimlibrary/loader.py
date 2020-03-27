from cosimlibrary.autoinit import AutoInit
from fmpy import read_model_description, extract
from fmpy.fmi2 import FMU2Slave
from fmpy.model_description import ScalarVariable
from pathlib import Path
from typing import Dict
import shutil


class LoadedFMU(AutoInit):
    fmu: FMU2Slave = None
    dir: str = None
    vars: Dict[str, ScalarVariable] = None
    cleanup: bool = None


class FMULoader:

    @staticmethod
    def get_vars(model_description):
        vrs = {}
        for variable in model_description.modelVariables:
            vrs[variable.name] = variable
        return vrs

    @staticmethod
    def load(fmu_path, instance_name, logger):

        fmu_path = Path(fmu_path)

        is_compressed = fmu_path.is_file() and fmu_path.name.endswith('.fmu')

        if(is_compressed):
            unzipdir = extract(fmu_path)
        else:
            unzipdir = str(fmu_path)

        desc = read_model_description(unzipdir)
        vars = FMULoader.get_vars(desc)
        fmu = FMU2Slave(guid=desc.guid,
                        unzipDirectory=unzipdir,
                        modelIdentifier=desc.coSimulation.modelIdentifier,
                        instanceName=instance_name,
                        fmiCallLogger=logger)
        return LoadedFMU(fmu=fmu, dir=unzipdir, vars=vars,cleanup = is_compressed)

    @staticmethod
    def unload(loaded_fmu: LoadedFMU):

        loaded_fmu.fmu.freeInstance()

        if(loaded_fmu.cleanup):
            try:
                shutil.rmtree(loaded_fmu.dir)
            except PermissionError:
                print("Warning: failed to clear directory ", loaded_fmu.dir)
