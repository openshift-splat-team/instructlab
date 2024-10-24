# SPDX-License-Identifier: Apache-2.0

# Standard
import logging
import pathlib

# Third Party
from click.testing import CliRunner
import yaml

# First Party
from instructlab import configuration, lab


def test_ilab_config_show(cli_runner: CliRunner) -> None:
    result = cli_runner.invoke(lab.ilab, ["--config", "DEFAULT", "config", "show"])
    assert result.exit_code == 0, result.stdout

    parsed = yaml.safe_load(result.stdout_bytes)
    assert parsed

    assert configuration.Config(**parsed)


def test_ilab_config_init_with_env_var_config(
    cli_runner: CliRunner, tmp_path: pathlib.Path
) -> None:
    # Common setup code
    cfg = configuration.get_default_config()
    assert cfg.general.log_level == logging.getLevelName(logging.INFO)
    cfg.general.log_level = logging.getLevelName(logging.DEBUG)
    cfg_file = tmp_path / "config-gold.yaml"
    with cfg_file.open("w") as f:
        yaml.dump(cfg.model_dump(), f)

    # Invoke the CLI command
    command = ["config", "init", "--non-interactive"]
    result = cli_runner.invoke(
        lab.ilab, command, env={"ILAB_GLOBAL_CONFIG": cfg_file.as_posix()}
    )
    assert result.exit_code == 0, result.stdout

    # Load and check the generated config file
    config_path = pathlib.Path(configuration.DEFAULTS.CONFIG_FILE)
    assert config_path.exists()
    with config_path.open(encoding="utf-8") as f:
        parsed = yaml.safe_load(f)
    assert parsed
    assert configuration.Config(**parsed).general.log_level == logging.getLevelName(
        logging.DEBUG
    )


def test_ilab_config_init_with_model_path(cli_runner: CliRunner) -> None:
    # Common setup code
    model_path = "path/to/model"
    command = ["config", "init", "--model-path", model_path]

    # Invoke the CLI command
    result = cli_runner.invoke(lab.ilab, command)
    assert result.exit_code == 0, result.stdout

    # Load and check the generated config file
    config_path = pathlib.Path(configuration.DEFAULTS.CONFIG_FILE)
    assert config_path.exists()
    with config_path.open(encoding="utf-8") as f:
        parsed = yaml.safe_load(f)
    assert parsed
    # the generate config should NOT use the same model as the chat/serve model
    assert configuration.Config(**parsed).generate.model != "path/to/model"
    assert configuration.Config(**parsed).generate.teacher.model_path != "path/to/model"
    assert configuration.Config(**parsed).serve.model_path == "path/to/model"
