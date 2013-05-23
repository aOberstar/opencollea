
var app = angular.module('opencollea', ['opencolleaServices','http-auth-interceptor', 'md5', 'ui-gravatar', 'ui.bootstrap']).
    config(['$routeProvider', function($routeProvider) {
        $routeProvider
            .when('/home/:courseTitle', {templateUrl: '/static/partials/home/home.html', controller: 'HomeCtrl'})
            .when('/discover', {templateUrl: '/static/partials/discover/discover.html', controller: 'DiscoverCtrl'})
            .when('/course-list', {templateUrl: '/static/partials/course/course-list.html', controller: CourseListCtrl})
            .when('/course/:courseTitle', {redirectTo: '/course/:courseTitle/activity'})
            .when('/course/:courseTitle/:subpage', {templateUrl: 'static/partials/course/course-detail.html', controller: 'CourseCtrl'})
            .when('/course/:courseTitle/:subpage/:subpageParam', {templateUrl: 'static/partials/course/course-detail.html', controller: 'CourseCtrl'})
            .when('/profile/:username', {templateUrl: '/static/partials/profile/user-profile-class.html' })
            .when('/profile/:username/edit', {templateUrl: '/static/partials/profile/user-profile-form.html', controller: 'UserProfileEditCtrl'})
            .when('/auth/edit', {templateUrl: '/static/partials/profile/user-registration-edit-form.html', controller: 'UserRegistrationDetailsEditCtrl'})
            .when('/new-course', {templateUrl: '/static/partials/course/new-course.html', controller: CourseCtrl})
            .when('/chat', {templateUrl: '/static/partials/chat/chat.html', controller: 'ChatCtrl'})
            .otherwise({redirectTo: '/home/'});
    }]);

/**
 * Inicializacija
 */
app.run(function($rootScope, Auth) {
    $rootScope.currentUser = Auth.getCurrentUser();
});
