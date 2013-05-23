/*
(function() {

    // Override the SocketIO constructor to provide a default
    // value for the port, which is added to os.environ in the
    // runserver_socketio management command.
    var prototype = io.Socket.prototype;
    io.Socket = function(host, options) {
        options = options || {};
        options.port = 8000;
        return prototype.constructor.call(this, host, options);
    };

    // We need to reassign all members for the above to work.
    for (var name in prototype) {
        io.Socket.prototype[name] = prototype[name];
    }

    // Arrays are transferred as individual messages in Socket.IO,
    // so we put them into an object and check for the __array__
    // message on the server to handle them consistently.
    var send = io.Socket.prototype.send;
    io.Socket.prototype.send = function(data) {
        if (data.constructor == Array) {
            channel =  data[0] == '__subscribe__' || data[0] == '__unsubscribe__';
            if (!channel) {
                data = ['__array__', data];
            }
        }
        return send.call(this, data);
    };

    // Set up the subscription methods.
    io.Socket.prototype.subscribe = function(channel) {
        this.send(['__subscribe__', channel]);
        return this;
    };
    io.Socket.prototype.unsubscribe = function(channel) {
        this.send(['__unsubscribe__', channel]);
        return this;
    };

})();


    var name, started = false;

    var addItem = function(selector, item) {
        var template = $(selector).find('script[type="text/x-jquery-tmpl"]');
        template.tmpl(item).appendTo(selector);
    };

    var addUser = function(data, show) {
        addItem('#users', data);
        if (show) {
            data.message = 'joins';
            addMessage(data);
        }
    };

    var removeUser = function(data) {
        $('#user-' + data.id).remove();
        data.message = 'leaves';
        addMessage(data);
    };

    var addMessage = function(data) {
        var d = new Date();
        var win = $(window), doc = $(window.document);
        var bottom = win.scrollTop() + win.height() == doc.height();
        data.time = $.map([d.getHours(), d.getMinutes(), d.getSeconds()],
                          function(s) {
                              s = String(s);
                              return (s.length == 1 ? '0' : '') + s;
                          }).join(':');
        addItem('#messages', data);
        if (bottom) {
            window.scrollBy(0, 10000);
        }
    };


    var socket;

    var connected = function() {
        socket.subscribe('room-' + window.room);
        if (name) {
            socket.send({room: window.room, action: 'start', name: name});
        } else {
            showForm();
        }
    };

    var disconnected = function() {
        setTimeout(start, 1000);
    };

    var messaged = function(data) {
        switch (data.action) {
            case 'in-use':
                alert('Name is in use, please choose another');
                break;
            case 'started':
                started = true;
                $('#submit').val('Send');
                $('#users').slideDown();
                $.each(data.users, function(i, name) {
                    addUser({name: name});
                });
                break;
            case 'join':
                addUser(data, true);
                break;
            case 'leave':
                removeUser(data);
                break;
            case 'message':
                addMessage(data);
                break;
            case 'system':
                data['name'] = 'SYSTEM';
                addMessage(data);
                break;
        }
    };
*/
$(function() {
    var start = function() {
        socket = new io.Socket();
        socket.connect();
        socket.on('connect', connected);
        socket.on('disconnect', disconnected);
        socket.on('message', messaged);
    };

    //start();

});


app

.controller('ChatCtrl', ['$scope', '$window', '$http', 'UserProfile', 'Course', 'Chat',
    function ($scope, $window, $http, UserProfile, Course, Chat) {
        $scope.messages = new Array();
        $scope.$watch('chatData', function (newValue, oldValue) {
            if (newValue!=oldValue) {
                $scope.messages = $scope.chatData.objects;
            }
        }, true);
        $scope.loadData = function () {
            $scope.chatData = Chat.query();

            var timer = setInterval(function(){
                $scope.chatData = Chat.query();
                $scope.$apply();
            }, 5000);
        };
        //initial load
        $scope.loadData();

        $scope.user_profile = UserProfile.get({userId: $scope.currentUser.id});
        $scope.postMessage = function() {
            $scope.messages.push({
                user: {
                    email: $scope.currentUser.email,
                    first_name: $scope.user_profile.first_name,
                    last_name: $scope.user_profile.last_name
                },
                when: 'Just now',
                content: this.messageTextArea});


            //if (!started) {
            //    data = {room: window.room, action: 'start', name: 'liveChat'};
            //} else {
            //    data = {room: window.room, action: 'message', message: this.messageTextArea};
            //}
            //socket.send(data);

            $scope.loading = true;
            var c = new Chat({
                    user: $scope.currentUser.resource_uri,
                content: $scope.messageTextArea
            });

            c.$save(function () {
                // Success
                console.log('success');
                this.messageTextArea = '';
                /*Course.get({id: $rootScope.course.id}, function (course) {
                    $rootScope.course = course;
                    $scope.isError = false;
                    $scope.loading = false;
                    $scope.isModalOpen = false;
                });*/
            }, function (response) {
                $scope.errors = response.data;
                $scope.isError = true;
                $scope.loading = false;
            });

        }
    }
])

.filter('reverse', function() {
  return function(items) {
    if (items == undefined) return null;
    return items.slice().reverse();
  };
});


