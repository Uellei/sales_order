import os
from typing import Callable
from dotenv import load_dotenv
import logging
from playwright.async_api import Page

# Logger Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
LOGIN_BUTTON_SELECTOR = "[aria-label='Community login']"
EMAIL_INPUT_SELECTOR = 'input[placeholder*="Email"]'
PASSWORD_INPUT_SELECTOR = 'input[placeholder*="Password"]'
DEFAULT_PAGE_SIZE_OPTION = "50"

# Load environment variables
load_dotenv()

def validate_environment_variables(*required_vars: str):
    """
    Ensures all required environment variables are defined.

    :param required_vars: List of environment variable names to validate.
    :raises EnvironmentError: If any required variable is missing.
    """
    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"Environment variable '{var}' is not defined.")

class SalesOrderDataExtractor:
    """
    Handles automation for data extraction and processing from a Sales Order system.
    """

    def __init__(self, page: Page):
        try:
            validate_environment_variables('LOGIN_EMAIL', 'LOGIN_PASSWORD', 'LOGIN_EMAIL2', 'LOGIN_PASSWORD2')
            self.page = page
        except Exception as error:
            logger.error(f"Error during environment variable validation: {error}")
            raise

    async def login(self, target_url: str):
        """
        Logs in to the Sales Order system using credentials from environment variables.

        :param target_url: The URL of the login page.
        :raises Exception: If an error occurs during login.
        """
        try:
            await self.page.goto(target_url)

            if await self.page.query_selector(LOGIN_BUTTON_SELECTOR):
                await self.page.click(LOGIN_BUTTON_SELECTOR)
                await self.page.fill(EMAIL_INPUT_SELECTOR, os.getenv('LOGIN_EMAIL'))
                await self.page.click("button.slds-button")
                await self.page.fill(PASSWORD_INPUT_SELECTOR, os.getenv('LOGIN_PASSWORD'))
                await self.page.click("button.button.slds-button_brand")

            await self.page.fill('input[type="email"]', os.getenv('LOGIN_EMAIL2'))
            await self.page.fill('input[type="password"]', os.getenv('LOGIN_PASSWORD2'))
            await self.page.click("a.btn")

            logger.info("Login successful.")
        except Exception as error:
            logger.error(f"Error during login process: {error}")
            raise

    async def open_query_page(self, route_interceptor: Callable, query_page_url: str) -> Page:
        """
        Opens the query page and sets up route interception.

        :param route_interceptor: Callback for handling intercepted routes.
        :param query_page_url: URL of the query page.
        :return: New page instance with query capabilities.
        :raises Exception: If an error occurs during page setup.
        """
        try:
            query_page = await self.page.context.new_page()
            await query_page.route('**/*', route_interceptor)
            await query_page.goto(query_page_url)
            logger.info("Query page opened successfully.")
            return query_page
        except Exception as error:
            logger.error(f"Error opening query page: {error}")
            raise

    async def track_order_status(self, query_page: Page, tracking_id: str) -> dict[str, str]:
        """
        Checks the status of a sales order by its tracking number.

        :param query_page: Page instance to interact with.
        :param tracking_id: Tracking number to query.
        :return: Dictionary with delivery status and scheduled delivery date.
        :raises Exception: If an error occurs during order tracking.
        """
        try:
            await query_page.fill("#inputTrackingNo", tracking_id)
            await query_page.click("#btnCheckStatus")
            await query_page.wait_for_selector("#shipmentStatus tr:last-child td:last-child")

            delivery_status_element = await query_page.query_selector("#shipmentStatus tr:last-child td:last-child")
            delivery_status_text = await delivery_status_element.inner_text()

            return {
                "is_delivered": delivery_status_text == "Delivered",
                "scheduled_delivery": delivery_status_text
            }
        except Exception as error:
            logger.error(f"Error tracking order '{tracking_id}': {error}")
            raise

    async def process_orders(self, query_page: Page, script_path: str) -> list[dict]:
        """
        Processes sales orders and retrieves tracking information.

        :param query_page: Query page instance.
        :param script_path: Path to the JavaScript file containing client-side functions.
        :return: List of processed orders with tracking details.
        :raises Exception: If an error occurs during processing.
        """
        try:
            script_content = self.load_script_content(script_path)
            await self.page.add_init_script(f"window.getFilteredRows = {script_content}")

            await self.page.click("#accordionSidebar > li:nth-child(9) > a")
            await self.page.wait_for_selector("#salesOrderDataTable")
            sales_order_table = await self.page.query_selector("#salesOrderDataTable")

            await self.page.select_option("select[name='salesOrderDataTable_length']", DEFAULT_PAGE_SIZE_OPTION)

            filtered_rows = await self.page.evaluate("getFilteredRows()")
            processed_orders = []
            rows_to_expand = []

            for row in filtered_rows:
                all_delivered = True
                tracking_details = []

                for tracking_id in row["elements"]:
                    try:
                        tracking_status = await self.track_order_status(query_page, tracking_id)
                        tracking_details.append({
                            "tracking_id": tracking_id,
                            "status": tracking_status["scheduled_delivery"]
                        })
                        if not tracking_status["is_delivered"]:
                            all_delivered = False
                            break
                    except Exception as error:
                        logger.warning(f"Failed to process tracking ID '{tracking_id}': {error}")
                        continue

                processed_orders.append({
                    "sales_order_id": row["SoOrder"],
                    "tracking_details": tracking_details,
                    "invoice_sent": all_delivered
                })

                if all_delivered:
                    rows_to_expand.append(row['index'])

            await self.page.bring_to_front()
            for row_index in rows_to_expand:    
                await self.expand_and_click_order_row(sales_order_table, row_index)

            logger.info(f"Processing completed. Total orders: {len(processed_orders)}")
            return processed_orders
        except Exception as error:
            logger.error(f"Error processing sales orders: {error}")
            raise

    async def expand_and_click_order_row(self, table: Page, row_index: int):
        """
        Expands and interacts with a specific order row.

        :param table: Table element containing order rows.
        :param row_index: Index of the row to interact with.
        :raises Exception: If an error occurs during interaction.
        """
        try:
            row_element = await table.query_selector(f"tbody > tr:nth-child({row_index}) > td")
            await row_element.click()
            expand_button = await table.query_selector(f"tbody > tr:nth-child({row_index}) + tr button")
            await expand_button.click()
        except Exception as error:
            logger.warning(f"Error expanding row at index {row_index}: {error}")

    @staticmethod
    def load_script_content(script_path: str) -> str:
        """
        Reads and returns the content of a JavaScript file.

        :param script_path: Path to the JavaScript file.
        :return: JavaScript file content as a string.
        :raises Exception: If the file cannot be read.
        """
        try:
            with open(script_path, "r") as script_file:
                return script_file.read()
        except Exception as error:
            logger.error(f"Error loading script from path '{script_path}': {error}")
            raise
