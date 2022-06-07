from django.db import models

# Create your models here.
class userTable(models.Model):
	username = models.CharField(max_length=30,unique=True)
	phno = models.BigIntegerField()
	email = models.EmailField(max_length = 30,unique=True)
	password = models.CharField(max_length=30)

class userstocks(models.Model):
	name = models.CharField(max_length=30,unique=True)
	user = models.ForeignKey('userTable', on_delete=models.CASCADE)


class userLogs(models.Model):
	time = models.DateTimeField()
	note = models.TextField(max_length = 300)

class stockList(models.Model):
	code = models.CharField(max_length = 20,unique=True)
	sector = models.CharField(max_length = 30,unique=True)
	longBusinessSummary = models.TextField()
	city = models.CharField(max_length = 30,unique=True)
	country = models.CharField(max_length = 30,unique=True)


class stockLogs(models.Model):
	time = models.DateTimeField()
	note = models.TextField(max_length = 300)


class countTable(models.Model):
	attr = models.CharField(max_length = 30)
	val = models.IntegerField()

