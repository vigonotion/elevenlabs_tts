from unittest.mock import Mock, patch

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
import requests

from custom_components.elevenlabs_tts.tts import (
    CONF_SIMILARITY,
    CONF_STABILITY,
    CONF_VOICE,
    ElevenLabsProvider,
    async_setup_entry,
    get_engine,
)


@pytest.fixture
def config_entry() -> ConfigEntry:
    return MockConfigEntry(
        domain="elevenlabs_tts",
        data={
            CONF_API_KEY: "fake_api_key",
            CONF_VOICE: "John",
            CONF_STABILITY: 0.9,
            CONF_SIMILARITY: 0.5,
        },
    )


@pytest.mark.asyncio
async def test_async_setup_entry(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Test async_setup_entry function."""
    with patch("custom_components.elevenlabs_tts.tts.ElevenLabsClient") as mock_client:
        mock_client.return_value.get_voices.return_value = None

        # Call the async_setup_entry function
        result = await async_setup_entry(hass, config_entry)

        # Verify that the function returns the expected value
        assert result == True


@pytest.mark.asyncio
async def test_async_setup_entry_with_bad_api_key(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Test async_setup_entry function with bad API key."""
    # patch a 401
    with patch(
        "custom_components.elevenlabs_tts.tts.ElevenLabsClient.get_voices",
        side_effect=requests.exceptions.HTTPError(response=Mock(status_code=401)),
    ) as mock_client:
        mock_client.return_value.get_voices.return_value = None

        # Call the async_setup_entry function
        result = await async_setup_entry(hass, config_entry)

        # Verify that the function returns the expected value
        assert result == False


@pytest.mark.asyncio
async def test_async_setup_entry_with_bad_voice(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Test async_setup_entry function with bad voice."""
    with patch("custom_components.elevenlabs_tts.tts.ElevenLabsClient") as mock_client:
        mock_client.return_value.get_voices.return_value = None
        mock_client.return_value.get_voice_by_name.return_value = None

        # Call the async_setup_entry function
        result = await async_setup_entry(hass, config_entry)

        # Verify that the function returns the expected value
        assert result == False


@pytest.mark.asyncio
async def test_async_setup_entry_with_exception(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Test async_setup_entry function with exception."""
    with patch(
        "custom_components.elevenlabs_tts.tts.ElevenLabsClient.get_voices",
        side_effect=Exception,
    ) as mock_client:
        mock_client.return_value.get_voices.return_value = None

        # ConfigEntryNotReady should be raised
        with pytest.raises(ConfigEntryNotReady):
            await async_setup_entry(hass, config_entry)


def test_elevenlabs_provider_init(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Test ElevenLabsProvider init function."""
    with patch("custom_components.elevenlabs_tts.tts.ElevenLabsClient") as mock_client:
        mock_client.return_value.get_voices.return_value = None

        provider = get_engine(hass, config_entry)

        assert isinstance(provider, ElevenLabsProvider)
        assert provider.name == "ElevenLabsTTS"
        assert provider.default_language == "en"
        assert provider.supported_languages == ["en"]
        assert provider._client == mock_client.return_value


def test_elevenlabs_provider_get_tts_audio(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> None:
    """Test ElevenLabsProvider get_tts_audio function."""
    with patch("custom_components.elevenlabs_tts.tts.ElevenLabsClient") as mock_client:
        mock_client.return_value.get_voices.return_value = None
        mock_client.return_value.get_tts_audio.return_value = "mp3", b"fake_audio"

        provider = get_engine(hass, config_entry)

        audio = provider.get_tts_audio("Hello", "en")

        assert audio == ("mp3", b"fake_audio")
