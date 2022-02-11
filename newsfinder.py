# HTTP GET requests for getting HTML data
import requests

# Parsing raw HTML code and helping to traverse DOM
from bs4 import BeautifulSoup

# Compares and give similarity between 2 strings
from difflib import SequenceMatcher

# Time how long the functions takes
import time

# Better selection tools in the terminal
import inquirer

# Colored text
def colored(color, text):

    # Return some hexidecimal format based off of rainbow colors
    match color:

        case "red":

            return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(255, 0, 0, text)

        case "orange":

            return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(255, 140, 0, text)

        case "yellow":

            return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(255, 255, 0, text)

        case "green":

            return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(0, 255, 0, text)

        case "blue":

            return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(0, 0, 255, text)

        case "purple":

            return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(128, 0, 128, text)

# Checks similarity of 2 strings
def similar(a, b):

    return SequenceMatcher(None, a, b).ratio()

# Function scrape websites of news headlins
def scrapeWebsite(url, articleClass, titleClass):

    # Contains titles
    titlesList = {"titles":[], "source": url}

    # Send HTTP GET request to url, find all articles class in HTML
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'lxml')
    content = soup.body.find_all(attrs={"class": articleClass})

    # Loop through stories
    for story in content:

        # Find headline elements
        titles = story.find_all(attrs={"class": titleClass})

        for title in titles:

            # Add innerText of element to list if doesn't contain it already
            if any(title.text in s for s in titlesList)==False:
                titlesList['titles'].append(title.text)

    if len(titlesList) > 0:

        print(colored("green", str(len(titlesList["titles" ]))+" headlines")+"loaded from "+url)
    else:

        print(colored("red", "No content loaded from ")+url)


    # Return titles list
    return titlesList

# Gets simlar headlines
def printSimilarHeadlines(headlines):

    matchedHeadlines = []

    # Loops through all combinations of headlines
    for i in range(len(headlines)):

        for x in range(i):

            # Check if the match is strong enough
            if similar(headlines[x]["title"],headlines[i]["title"]) > .6:

                # If they're from different sources
                if headlines[x]["source"]!=headlines[i]["source"]:

                    matchedHeadlines.append([headlines[x]["source"],headlines[x]["title"], headlines[i]["source"],headlines[i]["title"]])

    return matchedHeadlines

# Concenates headlines into organized array
def concatAllHeadlines(headlines):

    concatHeadlines = []

    # Loop through all headlines
    for i in range(len(headlines)):

        for x in range(len(headlines[i]["titles"])):

            # Dictionary with headline and news source
            concatHeadlines.append({"source": headlines[i]["source"], "title": headlines[i]["titles"][x]})

    return concatHeadlines

# Multiple-select for new sources

newsSources = [
    "Select All (Recomended)",
    'Fox News',
    'CBC',
    'Wall Street Journal',
    'NY Times',
    'NBC',
    'Washington Post',
    'Global News',
    'Forbes',
    'CNBC',
    'NY Post'
]

questions = [
  inquirer.Checkbox(
    'interests',
    message="Select news websites with left and right arrow, navigate with up and down arrow",
    choices=newsSources,
    ),
]

answers = inquirer.prompt(questions)

# Proper DOM traversal instructions for each news source
choicesDict = {
    "Fox News": ['https://www.foxnews.com', 'article', 'title'],
    "CBC": ['https://www.cbc.ca', 'card-content', 'headline'],
    "Wall Street Journal": ['https://www.wsj.com', 'style--grid--SxS2So51', 'WSJTheme--headlineText--He1ANr9C'],
    "NY Times": ['https://www.nytimes.com', 'story-wrapper', 'css-eylb5n'],
    "LA Times": ['https://www.latimes.com', 'promo', 'promo-title'],
    "Washington Post": ['https://www.washingtonpost.com', 'card', 'font--headline'],
    "The Gaurdian": ['https://www.theguardian.com/international', 'fc-item', 'js-headline-text'],
    "NBC": ["https://www.nbcnews.com","alacarte__item","alacarte__headline"],
    "Global News": ["https://www.globalnews.ca", "c-posts__item", "c-posts__headlineText"],
    "Forbes": ["https://www.forbes.com/?sh=478e525d2254", "fbs-slider__slide", "happening__title"],
    "CNBC": ["https://www.cnbc.com", "RiverPlusCard-container", "RiverHeadline-headline"],
    "NY Post": ["https://www.nypost.com", "story__text", "story__headline"]
}

sourcesList = []

print("Collecting headlines from websites...")

# Passed on user input, scrape news websites
for i in answers["interests"]:

    # Select All Option
    if i=="Select All (Recomended)":

        for i in range(len(newsSources)):
            
            if newsSources[i] != "Select All (Recomended)":

                sourcesList.append(
                    scrapeWebsite(
                        choicesDict[newsSources[i]][0],
                        choicesDict[newsSources[i]][1],
                        choicesDict[newsSources[i]][2]
                    ))
    
    else : 
        sourcesList.append(
            scrapeWebsite(
                choicesDict[i][0],
                choicesDict[i][1],
                choicesDict[i][2]
            )
        )

#Start "timer"
start = time.time()

print("Headlines collected from all websites...")
print("Formatting headlines...")

# Concatenate all headlines into formated array
mylist = concatAllHeadlines(sourcesList)

print("Removing duplicates...")

# Use tuple, dictionary and set methods to remove dictionary duplicates
foundHeadlines = set()
uniqueHeadlines = []
deletedCount = 0

for d in mylist:
    t = tuple(d.items())
    if t not in foundHeadlines:

        foundHeadlines.add(t)
        uniqueHeadlines.append(d)
    else:

        deletedCount += 1
mylist = uniqueHeadlines

print(colored("red", deletedCount)+"headlines removed")

print()

print("Finding similar headlines...")
print("")

# Get the similar headlines
matchedHeadlines = printSimilarHeadlines(mylist)
print(colored("green",str(len(matchedHeadlines)))+"pairs found")

print(colored("green", "Deleted similar headline pairs"))
deletedCount = 0
toDeleteIndexs = []

# Print very similar headline pairs
for i in range(len(matchedHeadlines)):

    for x in range(i):

        # Catch any index errors
        try:
           # If too similar, delete
            if similar(
                matchedHeadlines[i][1]+matchedHeadlines[i][3],
                matchedHeadlines[x][1]+matchedHeadlines[x][3]
            ) > .4:

                deletedCount += 1
                toDeleteIndexs.append(i)
        except IndexError:

            print("Index error")
 
print(colored("red", deletedCount)+"headline pairs removed")

#Print off the matching headlines
for i in range(len(matchedHeadlines)):

    print(matchedHeadlines[i][0], matchedHeadlines[i][1])
    print(matchedHeadlines[i][2], matchedHeadlines[i][3])
    print("")
    continue

# Print elapsed time taken to exectute
end = time.time()
print("Elapsed time:", colored("green", str(end - start)) + "seconds")

