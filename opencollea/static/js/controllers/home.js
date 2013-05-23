app

    .controller('HomeCtrl', ['$scope', '$routeParams', '$location', 'Question', 'Answer', 'UserProfile', 'Course','CoursesUserNotEnrolled', 'CoursesUserEnrolled',
        function($scope, $routeParams, $location, Question, Answer, UserProfile, Course, CoursesUserNotEnrolled, CoursesUserEnrolled) {

            $scope.user_profile = UserProfile.get({userId: $scope.currentUser.id});

            Course.get({machine_readable_title: $routeParams.courseTitle}, function (course) {
                $scope.course = course.objects[0];
            });

            CoursesUserNotEnrolled.get({userId: $scope.currentUser.id}, function (data) {
                $scope.courses_not_enrolled = data.objects;
            });

            CoursesUserEnrolled.get({userId: $scope.currentUser.id}, function (data) {
                $scope.courses_enrolled = data.objects;
            });

            $scope.showFeed = true;
            if ($location.path() === '/home/') {
                $scope.showFeed = false;
            }

    }])