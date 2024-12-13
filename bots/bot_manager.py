import asyncio
from dotenv import load_dotenv
from api.utils import save_to_database

from service.extractions.bot_extractor import SalesOrderDataExtractor
from service.bot_service import BotService

load_dotenv()

BLOCKED_RESOURCE_TYPES = ['image', 'stylesheet', 'font', 'media']

async def route_interceptor(route, request):
    """
    Intercept and manage network requests based on resource type.

    Parameters:
    route (playwright.async_api.Route): The route to manage.
    request (playwright.async_api.Request): The request being made.
    """
    if request.resource_type in BLOCKED_RESOURCE_TYPES:
        await route.abort()
    else:
        await route.continue_()

async def main(bot_name):
    """
    Main function to execute bot tasks for sales order processing.

    Parameters:
    bot_name (str): The name of the bot to be executed.

    Returns:
    list: A list of processed tracking information.
    """
    # Initialize bot service
    bot_service = BotService(bot_name)
    page = await bot_service.run_bot()
    
    # Initialize web extractor
    sales_order_extractor = SalesOrderDataExtractor(page)

    # Login to the application
    login_url = "https://pathfinder.automationanywhere.com/challenges/salesorder-applogin.html#"
    await sales_order_extractor.login(login_url)

    # Navigate to the order tracking page
    query_page_url = "https://pathfinder.automationanywhere.com/challenges/salesorder-tracking.html"
    tracking_page = await sales_order_extractor.open_query_page(route_interceptor, query_page_url)

    # Process orders
    script_path = "service/extractions/getFilteredRows.js"
    trackings = await sales_order_extractor.process_orders(tracking_page, script_path)

    # Clean up resources
    await bot_service.close()

    # Save tracking information to database
    await save_to_database(bot_name, trackings)

    return trackings