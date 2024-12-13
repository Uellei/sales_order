import traceback
from playwright.async_api import async_playwright, BrowserContext

class BotBrowser:
    def __init__(self, bot_name, tmpdirname):
        """
        Initializes the BotBrowser instance with bot name and temporary directory.
        :param bot_name: Name of the bot to execute.
        :param tmpdirname: Temporary directory to store browser data.
        """
        self.bot_name = bot_name
        self.tmpdirname = tmpdirname
        self.browser = None
        self.playwright = None

    async def launch_chromium(self, is_headless=False):
        """
        Launches a Chromium browser instance in persistent context mode.
        :param is_headless: Boolean to determine if the browser should run in headless mode.
        """
        self.playwright = await async_playwright().start()
        
        try:
            # Attempt to launch Chromium with custom arguments
            self.browser = await self.playwright.chromium.launch_persistent_context(
                self.tmpdirname,
                headless=is_headless,
                args=[
                    "--no-sandbox",  # Disables the sandbox for Chromium
                    "--disable-gpu",  # Disables GPU hardware acceleration
                    "--disable-blink-features=AutomationControlled",  # Avoids detection by websites
                ],
                viewport={"width": 1320, "height": 700}  # Sets the default viewport size
            )
        except Exception as e:
            # If an error occurs, log the traceback and retry with default settings
            traceback_error = traceback.format_exc()
            print(
                f"Error launching the browser. Retrying with default settings.\n{traceback_error}"
            )
            self.browser = await self.playwright.chromium.launch_persistent_context(
                self.tmpdirname,
                headless=is_headless,
            )

    def get_page(self, index: int = 0):
        """
        Retrieves a specific page by its index in the browser's context.
        :param index: Index of the page to retrieve.
        :return: Page instance at the specified index.
        :raises RuntimeError: If no page is found at the given index.
        """
        if not self.browser or len(self.browser.pages) <= index:
            raise RuntimeError(f"Page at index {index} not found.")
        return self.browser.pages[index]
    
    async def __call__(self):
        """
        Makes the class callable, launching the Chromium browser when invoked.
        :return: Instance of the BotBrowser class with an active browser.
        """
        await self.launch_chromium(is_headless=False)
        return self
