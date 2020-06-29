# AI-drug
This is a data analysis and visualization project on AI starups in drug discovery field.

As a machine learning researcher in the biology field, I have been keeping an eye on the recently emerging field of AI in drug discovery. Living in Toronto myself, where many "star" companies in this field were founded (Atomwise, BenchSci, Cyclica, Deep Genomics, ProteinQure... just to name a few!), I talked to many people in this field, and attended a few meetup events about this topic. What I learned is that this field is growing at such a rapid speed, and it is becoming increasing hard to keep track of all companies in this field and get a comprehensive view of them. Therefore, I decide to use my data science skills to track and analyze the companies in this field, and build an interactive dashboard (click [here](https://ai-drug-dash.herokuapp.com/) if you can't wait till the end of this post!) to visualize some key insights from my analysis.

## Dataset
The Chief Strategy Officer of BenchSci (one of the "star" AI-drug startups in Toronto), Simon Smith, is an excellent observer and communicator in the AI-drug discovery field. I have been following his podcast and blog about industry trends and new companies. He wroted a [blog](https://blog.benchsci.com/startups-using-artificial-intelligence-in-drug-discovery#understand_mechanisms_of_disease) in 2017 listing all startups in AI-drug discovery field, and has been updating this list since then. This blog is what I have found to be the most comprehensive list of companies in this field (230 startups as of April 2020), and therefore I decided to use his [blog](https://blog.benchsci.com/startups-using-artificial-intelligence-in-drug-discovery#understand_mechanisms_of_disease) as my main data source.

## Data Preprocessing
Since the blog simply listed companies as different paragraphs, I first scraped company information from the blog using [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/). Then, I converted the scraped data into DataFrame format using Pandas. The dataframe looks like this:

<p align="center">
<img src="/imgs/data_table.png">
</p>

In order to visualize these companies' locations in a map, I converted the address information in this table to latitude and longtitude using [Geopy](https://geopy.readthedocs.io/en/stable/):
```Python
# match address to latitude and longitude.
from geopy.geocoders import Nominatim
locator = Nominatim(user_agent="ai_drug")
lat, lng = [], []

for i, row in df.iterrows():
    location = locator.geocode(row.headquarters) or locator.geocode(row.city+','+row.country)
    lat.append(location.latitude)
    lng.append(location.longitude)

df['latitude'] = lat
df['longitude'] = lng
```

The funding information about these startups are not in the blog, therefore I searched for all 230 companies on [crunchbase](https://www.crunchbase.com/) and [pitchbook](https://pitchbook.com/), and added these information to my dataset too.

## Exploratory Data Analysis
I did some exploratory data analysis of the cleaned dataset, and noticed a few interesting things.

### 1. Explosion of startups since 2010
We can see this area didn't really start existing until 1999. Schrödinger, the company that devolops chemical simulation software, was founded in 1990 and listed here, but I am not sure if their drug discovery platform has already started using AI in 1990... The explosion of startups started in post-2010 era, around the same time when the "AI-hype" started, and peaked in 2017.

<p align="center">
<img src="/imgs/chronological_trend.png">
</p>

### 2. Most VC fundings are early-stage
We can see the majority of companies that received funding are still in early stages of venture capital funding (Pre-seed to Series A), which might be due to the fact that most AI-drug startups are still at the stage of exploring business models and developing technologies and products rather than scaling the company size.

<p align="center">
<img src="/imgs/funding_stages.png">
</p>
  
### 3. US is dominating the rest of the world
This may not come as a surprise, but US is dominating the rest of the world in this field. More than half of the companies are headquartered in US; More than 80% of the VC money went to US startups! UK is the No. 2 both in number of companies and funding. Canada is the No. 3 in number of companies, but not in funding - China is. There are quite a few promising Chinese startups in this field. For example, Adagene, an antibody discovery & development company in Suzhou, just raised $69,000,000 D-series funding in January 2020.

<p align="center">
<img src="/imgs/countries.png">
</p>
   
### 4. Novel drug candidate generation is the focus area of AI usage
We can see that the R&D category that attracts most attention and funding is the generation of novel drug candidates. Personally, I also thinks this is where AI can achieves its most power, i.e. predicting target-drug interactions using machine learning, by leveraging the large amount of existing test data.

<p align="center">
<img src="/imgs/categories.png">
</p>

## Interactive Dashboard
I used Plotly Dash to build an interactive dashboard to visualize my dataset and deliver analysis insights. Dash is Python-based framework for building analytical web applications, and it's free! The completed dashboard can be viewed at [https://ai-drug-dash.herokuapp.com/](https://ai-drug-dash.herokuapp.com/).

<p align="center">
<img src="/imgs/dashboard.png">
</p>
<br>

***References***:  

[1] Simon Smith, 230 Startups Using Artificial Intelligence in Drug Discovery. https://blog.benchsci.com/startups-using-artificial-intelligence-in-drug-discovery#understand_mechanisms_of_disease  
[2] https://www.crunchbase.com/  
[3] https://pitchbook.com/  
[4] David Comfort, How to Build a Reporting Dashboard using Dash and Plotly. https://towardsdatascience.com/how-to-build-a-complex-reporting-dashboard-using-dash-and-plotl-4f4257c18a7f
