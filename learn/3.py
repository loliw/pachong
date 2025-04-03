import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, BrowserConfig, LXMLWebScrapingStrategy
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter, BM25ContentFilter
async def main():
    # Step 1: Load initial Hacker News page
    browser_config = BrowserConfig(headless=False, extra_args = ['--disable-web-security'])
    session_id = "test"
    config = CrawlerRunConfig(
        word_count_threshold=10,
        session_id=session_id,
        excluded_tags=['form', 'header'],
        # exclude_external_links=True,

        # Content processing
        process_iframes=True,
        remove_overlay_elements=True,

        # Cache control
        cache_mode=CacheMode.BYPASS  # Use cache if available # Wait for 30 items
    )
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url="https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D%E5%9B%BD%E5%AE%B6%E5%BC%80%E6%94%BE%E5%A4%A7%E5%AD%A6",
            config=config
        )
        print(result.cleaned_html)

        # Step 2: Let's scroll and click the "More" link
        load_more_js = [
            "window.scrollTo(0, document.body.scrollHeight);",
            # The "More" link at page bottom
        ]
        js_next_page = """
                button = document.querySelector("#app > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div.module-page-fragment > div.m-container-max.m-top-nav > div > div > div > ul > li:nth-child(2) > span");
                if (button) button.click();
                window.scrollTo(0, document.body.scrollHeight);
                """
        #
        next_page_conf = CrawlerRunConfig(
            js_code=js_next_page,
            # Mark that we do not re-navigate, but run JS in the same session:
            js_only=True,
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
            scraping_strategy=LXMLWebScrapingStrategy(),
            markdown_generator=DefaultMarkdownGenerator(
                content_filter=PruningContentFilter(threshold=0.6),
                options={"ignore_links": True}
            )
        )
        #
        # Re-use the same crawler session
        result2 = await crawler.arun(
            url="https://m.weibo.cn/search?containerid=100103type%3D1%26q%3D%E5%9B%BD%E5%AE%B6%E5%BC%80%E6%94%BE%E5%A4%A7%E5%AD%A6",  # same URL but continuing session
            config=next_page_conf
        )
        # raw_html = result2.html
        # pruning_filter = PruningContentFilter(threshold=0.5, min_word_threshold=10)
        # pruned_chunks = pruning_filter.filter_content(raw_html)
        # pruned_html = "\n".join(pruned_chunks)
        # bm25_filter = BM25ContentFilter(
        #     user_query="machine learning",
        #     bm25_threshold=1.2,
        #     language="english"
        # )
        # total_items = result2.cleaned_html
        print(result2.markdown.fit_markdown)

if __name__ == "__main__":
    asyncio.run(main())