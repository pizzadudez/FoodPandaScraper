## Usage
- run splash image 
  `docker run -p 8050:8050 scrapinghub/splash --max-timeout 360`
- for now modify restaurant links in `spiders\main_spider => "start_urls"`
- in root directory run `scrapy crawl main_spider`
- output `output\scrapped.json`