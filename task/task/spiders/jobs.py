
import scrapy
import urllib


class JobsSpider(scrapy.Spider):
    name = 'jobs'
    allowed_domains = ['careerguide.com/career-options']
    start_urls = ['https://www.careerguide.com/career-options/']     


    def parse(self, response):
        choosenJobs = []
        url = 'https://in.linkedin.com/jobs'
        for job in response.xpath("//div[@class='row']/div"):
            a = job.xpath("./ul/li/a/text()").extract()
            for i in a:
                choosenJobs.append(i)
        for job in choosenJobs:
            yield scrapy.Request(url,callback=self.links,
            errback = self.errback_httpbin,dont_filter=True,meta = {'link':job})
            
    def links(self,response):
        link = response.request.meta['link']
        # Using parameters from searching job in LinkedIn
        params = {
                'keyword': link,
                'location' : 'Hyderabad,Telangana,India'
                }
        url = f'https://in.linkedin.com/jobs/search?{urllib.parse.urlencode(params)}'
        # Requesting the LinkedIn page for jobs as per the category.
        request = scrapy.Request(url, callback=self.parse_data,
        errback = self.errback_httpbin,dont_filter=True,meta = {'link':link})
        yield request

    def parse_data(self, response):
        link = response.request.meta['link']
        # Looping to the responses for the required details.
        for job in response.xpath("//div[@class='base-search-card__info']"):
            details = job.xpath("./h3/text()").extract()
            company_name = job.xpath("./h4/a/text()").extract() or job.xpath("./h4/div/text()").extract()
            location = job.xpath("./div/span[@class='job-search-card__location']/text()").extract()
            url = response.xpath("//a[@class='base-card__full-link']/@herf")
            yield{
                'Job Category' : link,
                'job' : details,
                'company name' : company_name,
                'location' : location
            }

    # Requesting the page again if there is any error.
    def errback_httpbin(self, failure): 
      self.logger.error(repr(failure))