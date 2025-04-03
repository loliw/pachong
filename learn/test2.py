import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def multi_page_commits():
    browser_cfg = BrowserConfig(
        headless=False,  # Visible for demonstration
        verbose=True,
        extra_args = ['--disable-web-security']
    )
    session_id = "test"

    base_wait = """js:() => {
        const elements = document.querySelectorAll('#hnmain > tbody > tr:nth-child(3) > td > table > tbody tr.athing.submission');
        return elements.length > 0;
    }"""

    # Step 1: Load initial commits
    config1 = CrawlerRunConfig(
        wait_for=base_wait,
        session_id=session_id,
        cache_mode=CacheMode.BYPASS,
        log_console=True,
        # Not using js_only yet since it's our first load
    )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        result = await crawler.arun(
            url="https://news.ycombinator.com/",
            config=config1
        )
        print("Initial commits loaded. Count:", result.cleaned_html.count("comments"))

        # Step 2: For subsequent pages, we run JS to click 'Next Page' if it exists
        js_next_page = """
        button = document.querySelector('a.morelink');
        if (button) button.click();
        """

        # Wait until new commits appear
        wait_for_more = """js:() => {
            elements = document.querySelectorAll('#hnmain > tbody > tr:nth-child(3) > td > table > tbody tr.athing.submission');
            if (!window.firstCommit && elements.length>0) {
                window.firstCommit = elements[0].outerText;
                return false;
            }
            // If top commit changes, we have new commits
            const topNow = elements[0]?.outerText.trim();
            return topNow && topNow !== window.firstCommit;
        }"""

        for page in range(2):  # let's do 2 more "Next" pages
            config_next = CrawlerRunConfig(
                session_id=session_id,
                js_code=js_next_page,
                wait_for=wait_for_more,
                js_only=True,       # We're continuing from the open tab
                cache_mode=CacheMode.BYPASS
            )
            result2 = await crawler.arun(
                url="https://github.com/microsoft/TypeScript/commits/main",
                config=config_next
            )
            print(f"Page {page+2} commits count:", result2.cleaned_html.count("comments"))

        # Optionally kill session
        await crawler.crawler_strategy.kill_session(session_id)

async def main():
    await multi_page_commits()

if __name__ == "__main__":
    asyncio.run(main())