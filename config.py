"""Configuration management for PR Inspector MCP Server."""

import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration YAML file
        
    Returns:
        Dictionary containing the configuration values
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}. "
            "Please create config.yaml with server settings."
        )
    
    with open(config_file, "r") as f:
        config = yaml.safe_load(f)
    
    return config


def get_server_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Get server-specific configuration.
    
    Args:
        config_path: Path to the configuration YAML file
        
    Returns:
        Dictionary with server configuration (host, port, transport)
    """
    config = load_config(config_path)
    
    # Get server config, with defaults if not present
    server_config = config.get("server", {})
    
    return {
        "host": server_config.get("host", "127.0.0.1"),
        "port": server_config.get("port", 8000),
        "transport": server_config.get("transport", "http"),
    }

