import csv 
import math
import sys
import random
from operator import itemgetter


def buildRatingList(csvname):
#this function is used to build a rating list from the csv file

	global movienum
	ratings= open(csvname,"r")
	reader = csv.reader(ratings)
	
	#initialization
	ratingDic = {}
	ratinglist = []
	userlist = []
	start = 1

	next(reader,None)

	maxmovieid = 0
	for item in reader:
		if int(item[0]) != start:
			userlist.append(start)
			userlist.append(ratingDic)
			ratinglist.append(userlist)
			start+=1
			ratingDic = {}
			userlist = []

		#put into the dictionary
		ratingDic[int(item[1])] = [float(item[2]),int(item[3])]

		if int(item[1]) > int(maxmovieid):
			maxmovieid = item[1]

	movienum = maxmovieid

	#put into userlist
	userlist.append(610)
	userlist.append(ratingDic)
	ratinglist.append(userlist)
	#ratinglist is a list of list, the inner list has dictionaries

	return ratinglist

def buildMovieDic(csvname):
#function for building movie dictionaries

	csvFile = open(csvname,"r",encoding = "utf8")
	reader = csv.reader(csvFile)

	movieDic = {}
	for item in reader:
		if reader.line_num == 1:
			continue
		movieDic[item[0]] = [item[1],item[2]]

	csvFile.close()
	return movieDic

def EucDis(user1,user2,ratinglist):
#euc distance function between two users

	#user1 is being compared to user2
	sharedlist = []

	#get the user1 list
	user1list = list(ratinglist[user1-1][1].keys())
	user2list = list(ratinglist[user2-1][1].keys())

	#get shared movie list
	for i in user1list:
		for j in user2list:
			if i == j:
				sharedlist.append(i)
	
	#threshold for enough amount of shared movies
	if len(sharedlist) <= 5:
		return math.inf

	halfEucDis = 0
	for item in sharedlist:
		halfEucDis += (ratinglist[user1-1][1].get(item)[0] - ratinglist[user2-1][1].get(item)[0])**2

	finalEucDis = math.sqrt(halfEucDis)
	return finalEucDis

def cosine(user1,user2,ratinglist):

#for the cosine function, a minimum of five movies should be shared to find the most similar users
	sharedlist = []

	#get the user1 list
	user1list = list(ratinglist[user1-1][1].keys())
	user2list = list(ratinglist[user2-1][1].keys())

	for i in user1list:
		for j in user2list:
			if i == j:
				sharedlist.append(i)
	
	#sharedlist size have to be > 5
	if len(sharedlist) <= 5:
		return 2;

	halfcosAngle = 0.0
	firstveccos = 0.0
	secveccos = 0.0
	denominator = 0.0
	for item in sharedlist:
		halfcosAngle += ratinglist[user1-1][1].get(item)[0] * ratinglist[user2-1][1].get(item)[0]

	for item in sharedlist:
		firstveccos += ratinglist[user1-1][1].get(item)[0]**2

	sqrtfirstveccos = math.sqrt(firstveccos)

	for item in sharedlist:
		secveccos += ratinglist[user2-1][1].get(item)[0]**2
	sqrtsecveccos = math.sqrt(secveccos)

	#implementing the formula
	denominator = sqrtfirstveccos * sqrtsecveccos

	finalcosAngle = halfcosAngle / denominator

	return finalcosAngle

def pearson(user1,user2,ratinglist):
	sharedlist = []

	#pearson correlation implementation

	#skip over the users when the numerator is 0, just return 0, because their ratings for shared movies are the same
	#get the user1 list
	user1list = list(ratinglist[user1-1][1].keys()) #all movies he has watched
	user2list = list(ratinglist[user2-1][1].keys()) #all movies he has watched

	for i in user1list:
		for j in user2list:
			if i == j:
				sharedlist.append(i)
	
	if len(sharedlist) < 5:
		return -20

	size = len(sharedlist)
	meanuser1 = 0.0
	meanuser2 = 0.0
	numerator = 0.0
	denominator = 0.0
	denominator1 = 0.0
	denominator2 = 0.0

	#implementing the formula
	for x in sharedlist:
		meanuser1 += ratinglist[user1-1][1].get(x)[0]
	meanuser1 = meanuser1/size

	for x in sharedlist:
		meanuser2 += ratinglist[user2-1][1].get(x)[0]
	meanuser2 = meanuser2/size

	for item in sharedlist:
		numerator += (ratinglist[user1-1][1].get(item)[0] - meanuser1) * (ratinglist[user2-1][1].get(item)[0] - meanuser2)
		denominator1 += ((ratinglist[user1-1][1].get(item)[0] - meanuser1)**2)
		denominator2 += ((ratinglist[user2-1][1].get(item)[0] - meanuser2)**2)

	if numerator == 0:
			return 0

	denominator1 = math.sqrt(denominator1)
	denominator2 = math.sqrt(denominator2)
	denominator = denominator1 * denominator2

	return numerator/denominator

def compare(ratinglist,userID,method):
#compare function compare the userID with every other user in the system

	comparelist = []
	distpair = []
	toplist= []
	size = len(ratinglist)

	for i in range(size):
		if userID == i:
			continue
		else:
			if method == 'euc':
				dist = EucDis(i,userID,ratinglist)
				if dist != 0:
					distpair.append((i,dist))
			elif method == 'cos':
				dist = cosine(i,userID,ratinglist)
				if dist != 2:
					distpair.append((i,dist))
			else:
				dist = pearson(i,userID,ratinglist)
				distpair.append((i,dist))
	distpair=sorted(distpair,key=itemgetter(1))
	
	#choose which method to use
	if method == 'cos':
		distpair = distpair[-5:]
		distpair = distpair[::-1]
		return distpair,userID
	elif method == 'euc':
		return distpair[0:5],userID

	else:
		distpair = distpair[-5:]
		distpair = distpair[::-1]
		return distpair,userID

def findtoplist(ratinglist,movieDic):

#findtoplist will return the movie lists from top rated to least rated
	mean = 0.0
	count = 0
	toplist = [(0,0)] * 1000
	for i in range (1,int(movienum)+1):
		for j in range(len(ratinglist)):
			if(ratinglist[j][1].get(i) != None):

				#print(count), calcute all ratings mean
				mean += ratinglist[j][1].get(i)[0]
				count += 1

		if(count > 20):
			mean = mean / count
		else:
			mean = 0

		if (mean > toplist[0][1]):
			toplist[0] = (i,mean)
			toplist=sorted(toplist,key=itemgetter(1))
		
		count = 0
		mean = 0.0

	#swtich it back and get movie names
	toplist = toplist[::-1]
	toplistnames = []
	for item in toplist:
		toplistnames.append(movieDic.get(str(item[0]))[0])
		


	return toplistnames,toplist

def recommendation(ratinglist,movieDic,reclist):
#final recommendation based on the compare function returning list

	userlist = []
	sharedlist = []
	leftoverlist = []
	valuelist = []
	finallist = []
	finalrec = []

	#for each most similar user, append two new movies to the list(top rated)
	for i in range(len(reclist[0])):
		userlist = list(ratinglist[reclist[0][i][0]-1][1].keys()) #all movies he has watchedreclist[i][0]
		user2list = list(ratinglist[reclist[1]-1][1].keys())
		for k in userlist:
			for j in user2list:
				if k == j:
					sharedlist.append(k)
		leftoverlist = list(set(userlist) - set(sharedlist))
		for item in leftoverlist:
			valuelist.append((item,ratinglist[reclist[0][i][0]-1][1].get(item)[0]))
		valuelist=sorted(valuelist,key=itemgetter(1))
		valuelist = valuelist[-2:]
		for item in valuelist:
			finallist.append(item)
		valuelist = []

	#sometimes recommends twice
	for item in finallist:
		finalrec.append(movieDic.get(str(item[0]))[0])
	return finalrec

def main():

	print("\n\n\n   System initializing, please wait.......\n\n\n")

	ratinglist = buildRatingList("ratings.csv")
	movieDic = buildMovieDic("movies.csv")
	userDic = {}
	userID = 611
	toplistnames = findtoplist(ratinglist,movieDic)[0]
	toplist = findtoplist(ratinglist,movieDic)[1]

	#cold user setup
	colduser = input("Are you a returning user? Please answer yes or no.\n")
	if colduser.lower() == 'no':

		ratecount = 0
		moviecount = 0
		userdict = {}
		print("\nHere is out top movies recommended for you based on users' favourite, please rate it from 0-5 if you've watched it. Or press ENTER \n")
		while (ratecount < 10 and moviecount< 1000):
			print(toplistnames[moviecount])
			userrate = input("please rate 0-5 or ENTER: \n")
			if userrate != "" and (float(userrate) <= 5 and float(userrate) >=0):
				userDic[toplist[moviecount][0]] = [float(userrate),0] 
				ratecount += 1
				moviecount += 1
			else:
				userrate = input("please rate 0-5 or ENTER: ")

		if ratecount == 10:
			print("your top 10 recommendations are: \n")
			#dynamic update ratinglist
			ulist = [int(userID)]
			ulist.append(userDic)
			ratinglist.append(ulist)

			reclist = compare(ratinglist,userID,'euc')
			finalrec = recommendation(ratinglist,movieDic,reclist)
			
			for item in finalrec:
				print(item)
				print("\n")

		else:
			print("Becuase you haven't watched enough films, your top 10 recommendations are: \n")
			for item in toplist[:10]:
				print(item)
				print("\n")

	#hot user
	else:
		change = 'yes'
		while change.lower() == 'yes':
			userID = input("Please tell us your userID: (from 1 - 610) \n")

			methodchange = 'yes'
			while methodchange.lower() == 'yes':
				method = input("Please tell us the method you want: (euc,cos,pearson) \n")
				if method == "euc":
					print("your top 10 recommendations are: \n")
					reclist = compare(ratinglist,int(userID),'euc')
					finalrec = recommendation(ratinglist,movieDic,reclist)
					for item in finalrec:
						print(item)
						print("\n")

				elif method == 'cos':
					print("your top 10 recommendations are: \n")
					reclist = compare(ratinglist,int(userID),'cos')
					finalrec = recommendation(ratinglist,movieDic,reclist)
					for item in finalrec:
						print(item)
						print("\n")

				else:
					print("your top 10 recommendations are: \n")
					reclist = compare(ratinglist,int(userID),'pearson')
					finalrec = recommendation(ratinglist,movieDic,reclist)
					for item in finalrec:
						print(item)
						print("\n")
				methodchange = input("Do you want to use another method: (yes or no) \n")

			change = input("Do you want to see result for other users: (yes or no) \n")

main()

