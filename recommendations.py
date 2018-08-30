# make a dictionary of ratings 
# for large number of entries its better to use a database
import seaborn as sns
from math import sqrt
import matplotlib.pyplot as plt
import pandas as pd

critics = {
'Lisa Rose':{'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,'Just My Luck': 3.0, 'Superman Returns': 3.5, 
'You, Me and Dupree': 2.5,'The Night Listener': 3.0},
'Gene Seymour': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5,'Just My Luck': 1.5, 'Superman Returns': 5.0,
'The Night Listener': 3.0,'You, Me and Dupree': 3.5},
'Michael Phillips': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,'Superman Returns': 3.5, 
'The Night Listener': 4.0},
'Claudia Puig': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,'The Night Listener': 4.5, 'Superman Returns': 4.0,
'You, Me and Dupree': 2.5},
'Mick LaSalle': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,'Just My Luck': 2.0, 'Superman Returns': 3.0, 
'The Night Listener': 3.0,'You, Me and Dupree': 2.0},
'Jack Matthews': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,'The Night Listener': 3.0, 
'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
'Toby': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0},
}

def eulecdian_distance(prefs,person1,person2):
    si={}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item]=1
    if len(si)==0: return 0
    
    sum_of_squares=sum([pow(prefs[person1][item]-prefs[person2][item],2)
                        for item in prefs[person1] if item in prefs[person2]])
    
    return 1/(1+sum_of_squares)

data = {'x' : critics['Mick LaSalle'],'y' : critics['Lisa Rose']}
data = pd.DataFrame(data)
          
sns.regplot(data=data, x="x", y="y", fit_reg=True, color="skyblue")
plt.title('Pearson Correlation Plot')
plt.xlabel('Mick LaSalle')
plt.ylabel('Lisa Rose')
plt.show()

def pearson_correlation(prefs,p1,p2):
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1
    N = len(si)
    if N == 0:
        return 0
    
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])
    
    sum1Sq = sum([pow(prefs[p1][it],2) for it in si])
    sum2Sq = sum([pow(prefs[p2][it],2) for it in si])
    
    pSum=sum([prefs[p1][it]*prefs[p2][it] for it in si])
    
    numerator = N*pSum - (sum1*sum2)
    denominator = sqrt(((N*sum1Sq)-(sum1*sum1))*((N*sum2Sq)-(sum2*sum2)))
    if denominator==0: 
        return 0
    pcc=numerator/denominator
    
    return pcc

# returns top 5 scores
def top_matches(prefs,person,n=5,similarity=pearson_correlation):
    scores = [(similarity(prefs,person,other),other)
                for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]

def getRecommendations(prefs,person,similarity=pearson_correlation,n=5):
    totals = {}
    simSums = {}
    for other in prefs:
        if other != person:
            sim = similarity(prefs,person,other)
            if sim > 0 :
                for item in prefs[other]:
                    if item not in prefs[person] or prefs[person][item]==0:
                        totals.setdefault(item,0)
                        totals[item]+=prefs[other][item]*sim
                        simSums.setdefault(item,0)
                        simSums[item]+=sim
    rankings=[(total/simSums[item],item) for item,total in totals.items()]
    rankings.sort()
    rankings.reverse()
    return rankings[0:n]                    
            
def transformPrefs(prefs):
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item,{})
            result[item][person]=prefs[person][item]
    return result

links = pd.read_csv('links.csv') 
movies = pd.read_csv('movies.csv') 
ratings = pd.read_csv('ratings.csv') 
tags = pd.read_csv('tags.csv') 

def dataFrameToDict():
    prefs = {}
    for uId in set(ratings['userId']):
        temp = ratings.loc[ratings['userId']==uId].loc[:,['movieId','rating']]
        mov = []
        rat = []
        for movieId,rating in temp.itertuples(index=False):
            title = movies.loc[movies['movieId'] == movieId,'title'].iloc[0]
            mov.append(title)
            rat.append(rating)
        prefs.setdefault(uId,{})
        prefs[uId] = dict(zip(mov,rat))
    return prefs

def calculateSimilarities(prefs,n=10):
    result = {}
    itemPrefs=transformPrefs(prefs)
    c=0
    for item in itemPrefs:
        c = c+1
        if c%100==0: 
            print("%d / %d" % (c,len(itemPrefs)))
        scores=top_matches(itemPrefs,item,n=n,similarity=pearson_correlation)
        result[item] = scores
    return result

# itemMatch can be calculated using calculateSimilarities
def getRecommendedItems(prefs,itemMatch,user):
    userRatings=prefs[user]
    scores={}
    totalSim={}
    for (item,rating) in userRatings.items():
        for (similarity,item2) in itemMatch[item]:
            if item2 in userRatings: continue
            scores.setdefault(item2,0)
            scores[item2]+=similarity*rating
            totalSim.setdefault(item2,0)
            totalSim[item2]+=similarity
    rankings=[(score/totalSim[item],item) for item,score in scores.items() if totalSim[item] != 0]
    rankings.sort()
    rankings.reverse()
    return rankings        


        
            