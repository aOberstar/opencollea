angular.module('opencolleaServices', ['ngResource'])
    .factory('Auth', function ($resource) {
        return $resource('/api/v1/auth/currentUser', {}, {
            'getCurrentUser': {method: 'GET'}
        });
    });
