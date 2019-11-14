## Usage
- run splash image 
  `docker run -p 8050:8050 scrapinghub/splash --max-timeout 360`
- in root directory run `scrapy crawl main_spider`
- output `output\scrapped.json` + postgres (settings.py > DATABASE)
