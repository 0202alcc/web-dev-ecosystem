from app.utils.security import validate_ip_prefix, validate_timestamp


class TestSecurityUtils:
    """Tests for security utility functions."""

    def test_validate_ip_prefix_valid(self):
        """Test IP validation with matching prefix."""
        result = validate_ip_prefix("192.168.12.100", "192.168.12.")
        assert result is True

    def test_validate_ip_prefix_invalid(self):
        """Test IP validation with non-matching prefix."""
        result = validate_ip_prefix("192.168.13.100", "192.168.12.")
        assert result is False

    def test_validate_ip_prefix_empty_ip(self):
        """Test IP validation with empty IP."""
        result = validate_ip_prefix("", "192.168.12.")
        assert result is False

    def test_validate_ip_prefix_empty_prefix(self):
        """Test IP validation with empty prefix."""
        result = validate_ip_prefix("192.168.12.100", "")
        assert result is False

    def test_validate_timestamp_valid_recent(self):
        """Test timestamp validation with recent timestamp."""
        import time

        timestamp_ms = int(time.time() * 1000)
        result = validate_timestamp(timestamp_ms)
        assert result is True

    def test_validate_timestamp_invalid_old(self):
        """Test timestamp validation with old timestamp."""
        import time

        old_timestamp_ms = int((time.time() - 600) * 1000)  # 10 minutes ago
        result = validate_timestamp(old_timestamp_ms)
        assert result is False

    def test_validate_timestamp_invalid_future(self):
        """Test timestamp validation with future timestamp."""
        import time

        future_timestamp_ms = int((time.time() + 600) * 1000)  # 10 minutes ahead
        result = validate_timestamp(future_timestamp_ms)
        assert result is False

    def test_validate_timestamp_invalid_format(self):
        """Test timestamp validation with invalid format."""
        result = validate_timestamp(-1)
        assert result is False
