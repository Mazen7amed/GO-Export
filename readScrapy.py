from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scraper.autoScout24_de import AutoScout24De
from crochet import setup, wait_for
from pipeline import SaveDataPipeline, scraped_data  # Import the pipeline and scraped_data

setup()


@wait_for(25)
def run_spider(url):
    """Run spider with AutoScout24De"""
    settings = get_project_settings()
    settings.set('ITEM_PIPELINES', {
        'pipeline.SaveDataPipeline': 100,  # Reference the pipeline correctly
    })

    crawler = CrawlerRunner(settings)
    d = crawler.crawl(AutoScout24De, urls=[url])
    return d


def get_scraped_data():
    """Get the scraped data"""
    return scraped_data.pop()
