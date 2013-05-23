
app

.factory('CoursesUserNotEnrolled', ['$resource', function ($resource) {
   return $resource('/api/v1/user_profile/:userId/courses_not_enrolled');
}])


.factory('MoocCoursesNooneTook', ['$resource', function ($resource) {
   return $resource('/api/v1/course/mooc_courses_noone_took');
}])


.factory('CoursesUserEnrolled', ['$resource', function ($resource) {
   return $resource('/api/v1/user_profile/:userId/courses_enrolled');
}])

;
