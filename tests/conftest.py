from stockalyzer.core.Logger import Logger
from stockalyzer.core.Config import YamlLoader
from pytest import fixture

@fixture(scope="session")
def cfg_setup():
    configPath = "config/tests/stockalyzer_test.yaml"
    config = YamlLoader.load(configPath)
    Logger(config.expand("Logger")).info("Test Genesis")
    yield config
    Logger().info("Test Completion")