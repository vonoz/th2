(function () {

	angular.module('mainModule').controller('mainCtrl', ['$scope', '$timeout', 'myRequester', '$filter', '$compile', '$log', 'cfpLoadingBar', 'toaster', function ($scope, $timeout, myRequester, $filter, $compile, $log, cfpLoadingBar, toaster) {

		$scope.plans = []
		$scope.calendar = []
		$scope.planDetail = []
		$scope.scheduleStart = new Date(2016, 7, 15)



		$scope.selectedWorkout ;
		$scope.workoutdetailViewMode = 1;
		$scope.myFTP = 280;

		$scope.getPlans();
		$scope.selectedPlanID = 228;

    $scope.getPlans = function () {
        myRequester.postData({ action: "getplans", }).then(function (data) {
            $scope.plans = data;
        }).then(function () {

        })
    }



		$scope.downloadCalendarClicked = function() {


			window.location = "downloadcalendar/" + $scope.selectedPlanID + "/" + $scope.myFTP + "/" + $filter('date')($scope.scheduleStart , "yyyy-MM-dd", 2);

		};

		$scope.showWorkoutDetail = function(fileID) {

			myRequester.postData({ action: "getworkoutdetail/" + fileID, }).then(function (data) {
					$scope.selectedWorkout = {
						WorkoutFileID : fileID,
						details : angular.copy($filter('filter')($scope.planDetail, { WorkoutFileID: fileID })[0]),
						steps : data
					}
        	$('#workoutdetail').modal('show');
				})
		}

		 $scope.downloadButtonClicked = function (id) {

			 window.location = "downloadworkout/" + id + "/" + $scope.myFTP ;
		 };

		 $scope.buildCalendar = function () {
			 var weekLock = -1

			 $scope.calendar = [];
			 // weekData = ['','','','','','',''];
			 for (i=0; i < $scope.planDetail.length; i++) {
					 workout = $scope.planDetail[i];

					 if (workout.Week != weekLock) {
							 weekLock = workout.Week;

							 if (weekData)
								 $scope.calendar.push(weekData);
							 var weekData = ['','','','','','',''];
					 }

					 var targetDate =   new Date()
					// targetDate.setDate($scope.scheduleStart.getDate() + (workout.Week * 7 + workout.DayOfWeek));
					targetDate = addDays($scope.scheduleStart , (workout.Week * 7 + workout.DayOfWeek));

					 weekData[workout.DayOfWeek] = {
						 Name : workout.Name,
						 TSS : workout.TSS,
						 Duration : workout.Duration,
						 WorkoutFileID : workout.WorkoutFileID,
						 FileUrl : workout.FileUrl,
						 targetDate : targetDate
					 }

			 }
			 if (weekData) {
				 $scope.calendar.push(weekData);
			 }
		 }


		 function addDays(startDate,numberOfDays)
		 {
			 var returnDate = new Date(
									 startDate.getFullYear(),
									 startDate.getMonth(),
									 startDate.getDate()+numberOfDays,
									 startDate.getHours(),
									 startDate.getMinutes(),
									 startDate.getSeconds());
			 return returnDate;
		 }

		$scope.getPlanDetail = function() {
				myRequester.postData({ action: "getplandetail/" + $scope.selectedPlanID, }).then(function (data) {
						$scope.planDetail = data;
						$scope.buildCalendar();
				}).then(function () {

				})
			}






	}]);

})()
