"""Tests for load-tester CLI functionality."""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from src.load_tester.main import (
    cli,
    conversation_load_test,
    run_load_test,
    search_load_test,
    validate,
)


class TestCLICommands:
    """Test CLI command functionality."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_help(self) -> None:
        """Test CLI help command."""
        result = self.runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Load Tester" in result.output
        assert "End-to-End Load Testing" in result.output
        assert "run-load-test" in result.output
        assert "search-load-test" in result.output
        assert "conversation-load-test" in result.output
        assert "validate" in result.output

    def test_cli_version(self) -> None:
        """Test CLI version command."""
        result = self.runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestRunLoadTestCommand:
    """Test run-load-test CLI command."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_run_load_test_basic(self, mock_create_load_tester: Mock) -> None:
        """Test basic run-load-test command."""
        # Setup mock
        mock_load_tester = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_load_tester.run_load_test.return_value = mock_result
        mock_load_tester.generate_comprehensive_report.return_value = "Test Report"
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(
            run_load_test,
            ["--concurrent-users", "3", "--duration", "5", "--ramp-up", "1"],
        )

        assert result.exit_code == 0
        assert "🚀 Starting comprehensive load test..." in result.output
        assert "✅ Load test completed successfully!" in result.output
        mock_create_load_tester.assert_called_once_with(
            "test-project",
            "test-datastore",
        )
        mock_load_tester.run_load_test.assert_called_once()

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_run_load_test_with_custom_queries(
        self,
        mock_create_load_tester: Mock,
    ) -> None:
        """Test run-load-test with custom queries."""
        mock_load_tester = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_load_tester.run_load_test.return_value = mock_result
        mock_load_tester.generate_comprehensive_report.return_value = "Custom Report"
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(
            run_load_test,
            [
                "--search-queries",
                "AI basics",
                "--search-queries",
                "ML concepts",
                "--conversation-queries",
                "Explain AI",
                "--project-id",
                "custom-project",
                "--data-store-id",
                "custom-datastore",
            ],
        )

        assert result.exit_code == 0
        mock_create_load_tester.assert_called_once_with(
            "custom-project",
            "custom-datastore",
        )

        # Verify the config passed to run_load_test
        call_args = mock_load_tester.run_load_test.call_args[0][0]
        assert "AI basics" in call_args.search_queries
        assert "ML concepts" in call_args.search_queries
        assert "Explain AI" in call_args.conversation_queries

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_run_load_test_failure(self, mock_create_load_tester: Mock) -> None:
        """Test run-load-test with failure result."""
        mock_load_tester = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_load_tester.run_load_test.return_value = mock_result
        mock_load_tester.generate_comprehensive_report.return_value = "Failure Report"
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(run_load_test)

        assert result.exit_code == 1
        assert "❌ Load test failed - error rate too high" in result.output

    def test_run_load_test_default_queries(self) -> None:
        """Test run-load-test uses default queries when none provided."""
        with patch("src.load_tester.main.create_load_tester_with_mocks") as mock_create:
            mock_load_tester = Mock()
            mock_result = Mock()
            mock_result.success = True
            mock_load_tester.run_load_test.return_value = mock_result
            mock_load_tester.generate_comprehensive_report.return_value = (
                "Default Report"
            )
            mock_create.return_value = mock_load_tester

            result = self.runner.invoke(run_load_test)

            assert result.exit_code == 0

            # Verify default queries were used
            call_args = mock_load_tester.run_load_test.call_args[0][0]
            assert "What is machine learning?" in call_args.search_queries
            assert "Explain artificial intelligence" in call_args.conversation_queries


class TestSearchLoadTestCommand:
    """Test search-load-test CLI command."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_search_load_test_basic(self, mock_create_load_tester: Mock) -> None:
        """Test basic search-load-test command."""
        mock_load_tester = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_load_tester.run_search_load_test.return_value = mock_result
        mock_load_tester.generate_comprehensive_report.return_value = "Search Report"
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(
            search_load_test,
            ["--concurrent-users", "4", "--duration", "8"],
        )

        assert result.exit_code == 0
        assert "🔍 Starting search load test..." in result.output
        assert "✅ Search load test completed successfully!" in result.output
        mock_load_tester.run_search_load_test.assert_called_once()

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_search_load_test_with_queries(self, mock_create_load_tester: Mock) -> None:
        """Test search-load-test with custom queries."""
        mock_load_tester = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_load_tester.run_search_load_test.return_value = mock_result
        mock_load_tester.generate_comprehensive_report.return_value = (
            "Custom Search Report"
        )
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(
            search_load_test,
            ["--queries", "search1", "--queries", "search2", "--queries", "search3"],
        )

        assert result.exit_code == 0

        # Verify custom queries were passed
        call_args = mock_load_tester.run_search_load_test.call_args[0]
        query_list = call_args[0]
        assert "search1" in query_list
        assert "search2" in query_list
        assert "search3" in query_list

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_search_load_test_failure(self, mock_create_load_tester: Mock) -> None:
        """Test search-load-test with failure result."""
        mock_load_tester = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_load_tester.run_search_load_test.return_value = mock_result
        mock_load_tester.generate_comprehensive_report.return_value = (
            "Search Failure Report"
        )
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(search_load_test)

        assert result.exit_code == 1
        assert "❌ Search load test failed - error rate too high" in result.output


class TestConversationLoadTestCommand:
    """Test conversation-load-test CLI command."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_conversation_load_test_basic(self, mock_create_load_tester: Mock) -> None:
        """Test basic conversation-load-test command."""
        mock_load_tester = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_load_tester.run_conversation_load_test.return_value = mock_result
        mock_load_tester.generate_comprehensive_report.return_value = (
            "Conversation Report"
        )
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(
            conversation_load_test,
            ["--concurrent-users", "2", "--duration", "6"],
        )

        assert result.exit_code == 0
        assert "💬 Starting conversation load test..." in result.output
        assert "✅ Conversation load test completed successfully!" in result.output
        mock_load_tester.run_conversation_load_test.assert_called_once()

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_conversation_load_test_with_queries(
        self,
        mock_create_load_tester: Mock,
    ) -> None:
        """Test conversation-load-test with custom queries."""
        mock_load_tester = Mock()
        mock_result = Mock()
        mock_result.success = True
        mock_load_tester.run_conversation_load_test.return_value = mock_result
        mock_load_tester.generate_comprehensive_report.return_value = (
            "Custom Conversation Report"
        )
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(
            conversation_load_test,
            ["--queries", "conversation1", "--queries", "conversation2"],
        )

        assert result.exit_code == 0

        # Verify custom queries were passed
        call_args = mock_load_tester.run_conversation_load_test.call_args[0]
        query_list = call_args[0]
        assert "conversation1" in query_list
        assert "conversation2" in query_list

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_conversation_load_test_failure(
        self,
        mock_create_load_tester: Mock,
    ) -> None:
        """Test conversation-load-test with failure result."""
        mock_load_tester = Mock()
        mock_result = Mock()
        mock_result.success = False
        mock_load_tester.run_conversation_load_test.return_value = mock_result
        mock_load_tester.generate_comprehensive_report.return_value = (
            "Conversation Failure Report"
        )
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(conversation_load_test)

        assert result.exit_code == 1
        assert "❌ Conversation load test failed - error rate too high" in result.output


class TestValidateCommand:
    """Test validate CLI command."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_validate_success(self, mock_create_load_tester: Mock) -> None:
        """Test successful service validation."""
        mock_load_tester = Mock()
        mock_load_tester.search_engine.validate_connection.return_value = True
        mock_load_tester.answer_service.validate_connection.return_value = True
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(validate)

        assert result.exit_code == 0
        assert "🔧 Validating service connections..." in result.output
        assert "Search Engine: ✅ Connected" in result.output
        assert "Answer Service: ✅ Connected" in result.output
        assert "✅ All services validated successfully!" in result.output

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_validate_search_failure(self, mock_create_load_tester: Mock) -> None:
        """Test validation with search engine failure."""
        mock_load_tester = Mock()
        mock_load_tester.search_engine.validate_connection.return_value = False
        mock_load_tester.answer_service.validate_connection.return_value = True
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(validate)

        assert result.exit_code == 1
        assert "Search Engine: ❌ Failed" in result.output
        assert "Answer Service: ✅ Connected" in result.output
        assert "❌ Service validation failed" in result.output

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_validate_answer_failure(self, mock_create_load_tester: Mock) -> None:
        """Test validation with answer service failure."""
        mock_load_tester = Mock()
        mock_load_tester.search_engine.validate_connection.return_value = True
        mock_load_tester.answer_service.validate_connection.return_value = False
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(validate)

        assert result.exit_code == 1
        assert "Search Engine: ✅ Connected" in result.output
        assert "Answer Service: ❌ Failed" in result.output
        assert "❌ Service validation failed" in result.output

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_validate_both_failure(self, mock_create_load_tester: Mock) -> None:
        """Test validation with both services failing."""
        mock_load_tester = Mock()
        mock_load_tester.search_engine.validate_connection.return_value = False
        mock_load_tester.answer_service.validate_connection.return_value = False
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(validate)

        assert result.exit_code == 1
        assert "Search Engine: ❌ Failed" in result.output
        assert "Answer Service: ❌ Failed" in result.output
        assert "❌ Service validation failed" in result.output

    @patch("src.load_tester.main.create_load_tester_with_mocks")
    def test_validate_with_custom_ids(self, mock_create_load_tester: Mock) -> None:
        """Test validation with custom project and datastore IDs."""
        mock_load_tester = Mock()
        mock_load_tester.search_engine.validate_connection.return_value = True
        mock_load_tester.answer_service.validate_connection.return_value = True
        mock_create_load_tester.return_value = mock_load_tester

        result = self.runner.invoke(
            validate,
            ["--project-id", "custom-project", "--data-store-id", "custom-datastore"],
        )

        assert result.exit_code == 0
        mock_create_load_tester.assert_called_once_with(
            "custom-project",
            "custom-datastore",
        )


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    def setup_method(self) -> None:
        """Set up test environment."""
        self.runner = CliRunner()

    def test_cli_subcommand_help(self) -> None:
        """Test help for individual subcommands."""
        commands = [
            "run-load-test",
            "search-load-test",
            "conversation-load-test",
            "validate",
        ]

        for cmd in commands:
            result = self.runner.invoke(cli, [cmd, "--help"])
            assert result.exit_code == 0
            assert "--help" in result.output or "Usage:" in result.output

    def test_cli_parameter_validation(self) -> None:
        """Test CLI parameter validation."""
        # Test invalid concurrent users
        with patch("src.load_tester.main.create_load_tester_with_mocks"):
            self.runner.invoke(run_load_test, ["--concurrent-users", "-1"])
            # Click should handle invalid values gracefully

        # Test invalid duration
        with patch("src.load_tester.main.create_load_tester_with_mocks"):
            self.runner.invoke(search_load_test, ["--duration", "-5"])
            # Click should handle invalid values gracefully
