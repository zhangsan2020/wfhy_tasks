from task.cmeg.cme_spider import CmeSpider
if __name__ == '__main__':

    cme = CmeSpider()
    # zw.get_page_list(1,max_page=211)
    cme.run()