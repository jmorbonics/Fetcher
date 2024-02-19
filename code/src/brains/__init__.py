from . import base, human_driver, autonomous
import types


Types: dict[str, types.ModuleType] = {
    "autonomous": autonomous,
    "base": base,
    "human_driver": human_driver
}
