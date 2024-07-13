scraped_data = []


class SaveDataPipeline:
    def process_item(self, item, spider):
        scraped_data.append(item)
        return item
