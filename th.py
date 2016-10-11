import json
from db import *
from flask import Flask,render_template,url_for, redirect,send_from_directory,make_response
import os
import urllib
import time
import datetime


app = Flask(__name__)
homePath = ""

@app.route('/')
def index():
	#return render_template('index.html')
	return send_from_directory(homePath + 'static', 'index.html')

@app.route('/getplans', methods=['GET', 'POST'])
def getPlans():
	foo = queryDB("select * from tblPlan where planName not like '%archived%' order by planName")
	return json.dumps(foo, ensure_ascii=False)

@app.route('/getplandetail/<planID>', methods=['GET', 'POST'])
def getPlanDetail(planID):
	sql = """
		select PlanWorkoutId, PlanId, a.WorkoutFileID, FileUrl,
			Week, DayOfWeek, Name, Duration, TSS, IntensityFactor,
			Description, Goals
	 		from tblPlanWorkout a
				join tblworkoutfile b on a.WorkoutFileID = b.WorkoutFileID
			where a.PlanId='{}'
			order by Week, DayOfWeek
	""".format(planID)
	foo = queryDB(sql)
	return json.dumps(foo, ensure_ascii=False)

@app.route('/downloadworkout/<fileID>/<ftp>', methods=['GET', 'POST'])
def downloadWorkout(fileID, ftp):
	steps = weightWorkout(parseWorkoutFile(fileID), ftp)

	sql = """
	select Name
			from tblworkoutfile
			where WorkoutFileID='{}'
	""".format(fileID)
	workoutName = queryDBScalar(sql) + "_" + ftp

	response = make_response(render_template('workoutTemplate.tcx', steps=steps, workoutName=workoutName.strip()))
	response.headers['Content-Disposition'] = "attachment; filename={}.tcx".format(workoutName)
	return response


@app.route('/downloadcalendar/<planID>/<ftp>/<firstWeekBegin>', methods=['GET', 'POST'])
def downloadCalendar(planID, ftp, firstWeekBegin):

	planSql = """
		select PlanWorkoutId, PlanId, a.WorkoutFileID, FileUrl,
			Week, DayOfWeek, Name, Duration, TSS, IntensityFactor,
			Description, Goals
	 		from tblPlanWorkout a
				join tblworkoutfile b on a.WorkoutFileID = b.WorkoutFileID
			where a.PlanId='{}'
			order by Week, DayOfWeek
	""".format(planID)

	workoutList = queryDB(planSql)
	startDate = datetime.datetime.strptime(firstWeekBegin, '%Y-%m-%d')

	print(startDate)
	workouts = []
	for workout in workoutList:
		dayOffset = (workout["Week"] * 7) + workout["DayOfWeek"]
		woDay = startDate + datetime.timedelta(days=dayOffset)
		workouts.append({
			'steps' : weightWorkout(parseWorkoutFile(workout["WorkoutFileID"]), ftp),
			'workoutName' : woDay.strftime('%m%d') + "_" + workout["Name"].strip() + "_" + ftp ,
			'scheduledOn' : woDay.strftime('%Y-%m-%d')
		})

	response = make_response(render_template('calendarTemplate.tcx', workouts=workouts))
	response.headers['Content-Disposition'] = "attachment; filename={}.tcx".format("calendar")
	return response
	#return json.dumps(workouts, ensure_ascii=False)

@app.route('/getworkoutdetail/<fileID>', methods=['GET', 'POST'])
def getworkoutdetail(fileID):
	steps = parseWorkoutFile(fileID)
	return json.dumps(steps, ensure_ascii=False)



def parseWorkoutFile(fileID):
	sql = """
	select FileUrl
			from tblworkoutfile
			where WorkoutFileID='{}'
	""".format(fileID)
	remoteUrl = queryDBScalar(sql)
	filePath = homePath + "workouts/{}.txt".format(fileID)

	if not os.path.exists(filePath):
		urllib.request.urlretrieve(remoteUrl, filePath)
		#foo = urllib.URLopener()
		#foo.retrieve(remoteUrl, filePath)


	file = open(homePath + "workouts/{}.txt".format(fileID), 'r')
	inCourse = False
	steps = []
	for line in file:
		if line.startswith("[END COURSE DATA]"):
			break

		if inCourse:
			line = line.replace("\n", "")
			line = line.replace("\r", "")
			line2 = line.split("\t")
			lineIndex += 1

			if lineIndex % 2 != 0:
				minute1 = float(line2[0] )
				target1 = float(line2[1] )
			else:
				minute2 = float(line2[0])
				target2 = float(line2[1])


				duration = int((minute2 - minute1) * 60)
				percOfFTP = int((target1 + target2) / 2)

				if duration == 0 :
					minute2 = minute1
					target2 = target1

					minute1 = lastMinute2
					target1 = lastTarget2





				stepIndex += 1
				steps.append(
					{
					'id' : stepIndex,
					'beginTime' : minute1,
					'endTime' : minute2,
					'duration' : duration,
					'percOfFTP' : percOfFTP
					}
				)

				lastTarget2 = target2
				lastMinute2 = minute2

		if line.startswith("[COURSE DATA]"):
			inCourse = True
			lineIndex = 0
			stepIndex = 0
	#print(steps)
	return steps

def weightWorkout(stepsPercOfFTP, myFTP):

	steps = []
	for step in stepsPercOfFTP:

		minTargetPower = int(int(myFTP) * step['percOfFTP'] / 100) - 7
		maxTargetPower = int(int(myFTP) * step["percOfFTP"] / 100) + 7
		steps.append(
			{

			'id' : step['id'],
			'duration' : step['duration'],
			'minPower' : minTargetPower,
			'maxPower' : maxTargetPower
			}
		)

	return steps







@app.route('/downloadall/', methods=['GET', 'POST'])
def downloadAll():
	sql = """
	select FileUrl, WorkoutFileID, Name
			from tblworkoutfile
	"""

	workouts = queryDB(sql)

	for workout in workouts:
		print(workout)
		filePath = homePath + "workouts/{}.txt".format(workout["WorkoutFileID"])

		if not os.path.exists(filePath):
			urllib.request.urlretrieve(workout["FileURL"], filePath)
			print("sleep.")
			time.sleep(10)
	return "OK"



if __name__ == '__main__':
    app.run(debug=True)
