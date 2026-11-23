import yaml


def load_config(filename: str, logger: object) -> dict[str, object]:
    """
    Carica la configurazione YAML.
    """
    logger.info( "Loading configuration: %s", filename, )
    try:
        with open( filename, "r", encoding="utf-8", ) as f:
            config = yaml.safe_load(f)

    except FileNotFoundError:
        logger.error( "Configuration file not found: %s", filename, )
        raise

    except yaml.YAMLError as exc:
        logger.error( "Invalid YAML configuration: %s", exc, )
        raise

    if not isinstance(config, dict):
        raise TypeError( "Invalid configuration: root must be a dictionary" )

    return config
