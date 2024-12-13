from tempfile import TemporaryDirectory
from service.bot_browser import BotBrowser

class BotService:
    def __init__(self, bot_name):
        """
        Initializes the BotService instance with the bot name.
        :param bot_name: Name of the bot to execute.
        """
        self.bot_name = bot_name
        self.browser_context = None
        self.page = None

    async def run_bot(self):
        """
        Launches the bot browser and retrieves the first page for the bot.
        Uses a temporary directory for browser persistence data.
        :return: The first page of the bot browser context.
        """
        with TemporaryDirectory() as tmpdirname:
            # Initialize the BotBrowser instance and launch the browser
            bot_browser = await BotBrowser(tmpdirname, self.bot_name)()
            self.browser_context = bot_browser.browser  # Store the browser context
            self.page = bot_browser.get_page(0)  # Get the first page in the browser context
        return self.page
    
    async def close(self):
        """
        Closes the browser context and any associated resources.
        Ensures the browser and page contexts are properly cleaned up.
        """
        if self.browser_context:
            await self.browser_context.close()  # Close the browser context
        if self.page:
            await self.page.context.close()  # Close the page's associated context
