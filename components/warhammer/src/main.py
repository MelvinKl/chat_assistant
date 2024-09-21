import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)

from base_component_api.main import app as component_app
from base_component_api.main import dependency_override

from warhammer_dependency_container import WarhammerDependencyContainer

warhammer_container = WarhammerDependencyContainer()
dependency_override(warhammer_container)