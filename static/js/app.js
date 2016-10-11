(function () {

    var app = angular.module('mainModule', ['ui.bootstrap', 'chieffancypants.loadingBar', 'toaster', 'ngAnimate', 'ngSanitize']).config(function (cfpLoadingBarProvider) {
		cfpLoadingBarProvider.includeSpinner = false;
	});

	app.filter('fixMinute', function () {
		return function (input, tab) {

      var date = new Date(null);
      date.setSeconds(input * 60);
      return date.toISOString().substr(11, 8);

		}
	});

	app.directive('ngConfirmClick', [
	  function () {
	  	return {
	  		priority: -1,
	  		restrict: 'A',
	  		link: function (scope, element, attrs) {
	  			element.bind('click', function (e) {
	  				var message = attrs.ngConfirmClick;
	  				if (message && !confirm(message)) {
	  					e.stopImmediatePropagation();
	  					e.preventDefault();
	  				}
	  			});
	  		}
	  	}
	  }
	]);

	app.factory('myRequester', function ($q, $http) {
		var urlx = "/";

		return {
			postData: function (req) {

				var deferred = $q.defer();
				$http({
					url: urlx + req.action,
					method: 'POST',
					data: req.request,
					headers: { 'Content-Type': 'application/json;charset=utf-8' }
				}).success(function (data, status, headers, config) {
					deferred.resolve(data);
				}).error(function (data, status, headers, config) {
					deferred.reject(status);
				});

				return deferred.promise;
			}
		};
	});




})();
