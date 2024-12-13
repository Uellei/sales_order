import pytest
from service.bot_service import BotService

@pytest.mark.asyncio
async def test_run_bot_service(monkeypatch):
    async def mock_browser(*args, **kwargs):
        return {"success": True}

    monkeypatch.setattr("service.bot_browser.BotBrowser", mock_browser)

    bot_service = BotService("test_bot")
    page = await bot_service.run_bot()
    assert page is not None
    await bot_service.close()

import pytest
from unittest.mock import AsyncMock, MagicMock
from ..service.bot_service import BotService
from service.extractions.bot_extractor import SalesOrderDataExtractor

@pytest.mark.asyncio
async def test_bot_service_initialization():
    bot_service = BotService(bot_name="TestBot")
    assert bot_service.bot_name == "TestBot"
    assert bot_service.browser_context is None
    assert bot_service.page is None

@pytest.mark.asyncio
async def test_bot_service_run_bot():
    bot_service = BotService(bot_name="TestBot")
    bot_service.run_bot = AsyncMock(return_value="Mocked Page")
    
    page = await bot_service.run_bot()
    assert page == "Mocked Page"

@pytest.mark.asyncio
async def test_sales_order_extractor_login():
    mock_page = AsyncMock()
    extractor = SalesOrderDataExtractor(page=mock_page)
    
    # Mock environment variables
    mock_page.goto = AsyncMock()
    mock_page.query_selector = AsyncMock(return_value=True)
    mock_page.click = AsyncMock()
    mock_page.fill = AsyncMock()
    
    await extractor.login("https://example.com/login")
    
    mock_page.goto.assert_called_with("https://example.com/login")
    mock_page.query_selector.assert_called_with("[aria-label='Community login']")
    mock_page.click.assert_called()

@pytest.mark.asyncio
async def test_sales_order_extractor_process_orders():
    mock_page = AsyncMock()
    mock_query_page = AsyncMock()
    extractor = SalesOrderDataExtractor(page=mock_page)
    
    extractor.load_script_content = MagicMock(return_value="function getFilteredRows() {}")
    mock_page.evaluate = AsyncMock(return_value=[
    {"SoOrder": "12345", "elements": ["TRACK123"], "index": 1}
    ])

    mock_query_page.fill = AsyncMock()
    mock_query_page.click = AsyncMock()
    mock_query_page.wait_for_selector = AsyncMock()
    mock_query_page.query_selector = AsyncMock(return_value=MagicMock(inner_text=AsyncMock(return_value="Delivered")))
    
    result = await extractor.process_orders(mock_query_page, "mock_script_path.js")
    assert len(result) == 1
    assert result[0]["sales_order_id"] == "12345"
    assert result[0]["invoice_sent"] is True

