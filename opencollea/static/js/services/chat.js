
app


    .factory('Chat', ['$resource', function ($resource) {
        return $resource('/api/v1/chat/:id', {}, {
            'query': {method: 'GET'},
            'postNew': {method: 'POST'}
        });
    }])
;
