
app

    .controller('CourseCtrl', ['$scope', '$rootScope', '$routeParams', 'Course', function ($scope, $rootScope, $routeParams, Course) {
        $scope.subpage = $routeParams.subpage === undefined ? 'MAIN' : $routeParams.subpage;
        $scope.param = $routeParams.subpageParam === undefined ? '' : $routeParams.subpageParam;

        Course.get({machine_readable_title: $routeParams.courseTitle}, function (course) {
            // Success
            $rootScope.course = course.objects[0];
        }, function () {
            // Fail
        });
    }])

    .controller('CreateNewNoteCtrl', ['$scope', '$rootScope', '$window', 'EtherpadNote', function($scope, $rootScope, $window, EtherpadNote) {
        $scope.isModalOpen = false;
        $scope.modalOpts = {
            backdropFade: true,
            dialogFade: true
        };

        $scope.openModal = function () {
            $scope.isModalOpen = true;
        };

        $scope.closeModal = function () {
            $scope.isModalOpen = false;
        };

        $scope.createNewNote = function () {
            // Save note and redirect to created note!
            var Note = new EtherpadNote({
                user: $scope.currentUser.resource_uri,
                course: $scope.course.resource_uri,
                title: $scope.title
            });
            Note.$save(function () {
                $rootScope.notifications = [{
                    class: 'alert-success',
                    content: 'Note added. You can start writing right away!'
                }];
                $scope.isModalOpen = false;
                $scope.isError = false;

                // Redirect user to this new note
                EtherpadNote.get({course: $scope.course.id, limit: 1, order_by: '-id'}, function (latestNote) {
                    latestNote = latestNote.objects[0];
                    $window.location.href = '#/course/' + $scope.course.machine_readable_title + '/notes/' + latestNote.machine_readable_title;
                });
            }, function () {
                $scope.isError = true;
            });
        };
    }])


    .controller('NotesListCtrl', ['$scope', 'EtherpadNote', function ($scope, EtherpadNote) {
        $scope.$watch('course', function (newValue, oldValue) {
            if (newValue !== undefined) {
                EtherpadNote.get({course: $scope.course.id}, function (notes) {
                    $scope.notes = notes.objects;
                });
            }
        });
    }])


    .controller('NoteCtrl', ['$scope', '$rootScope', '$window', 'EtherpadNote', function ($scope, $rootScope, $window, EtherpadNote) {

        $scope.$watch('course', function (newValue, oldValue) {
            if (newValue !== undefined) {
                EtherpadNote.get({course:$scope.course.id, machine_readable_title: $scope.param}, function (note) {
                    $scope.note = note.objects[0];
                    $('#etherpad').pad({padId: $scope.note.pad_id, height: 450,
                        showControls: true, showChat: true, userName: $scope.currentUser.username});
                }, function () {
                    // Fails
                });
            }
        });

        $scope.confirmNoteDeletion = function () {
            $('#deleteNoteAlert').show();
        }

        $scope.deleteThisNote = function () {
            EtherpadNote.delete({id: $scope.note.id}, function () {
                $rootScope.notifications = [{
                    class: 'alert-success',
                    content: 'Sucky note successfully deleted.'
                }];
                $window.location.href = '#/course/' + $scope.course.machine_readable_title + '/notes'
            });
        }
    }])

    .controller('QAController', ['$scope', '$rootScope', 'Question', 'Course', function ($scope, $rootScope, Question, Course) {
        $scope.errors = {};
        $scope.loading = false;
        $scope.isModalOpen = false;
        $scope.modalOpts = {
            backdropFade: true,
            dialogFade: true
        };

        $scope.openModal = function () {
            $scope.isModalOpen = true;
        };

        $scope.closeModal = function () {
            $scope.isModalOpen = false;
        };

        $scope.createNewQuestion = function () {
            $scope.loading = true;
            var q = new Question({
                user: $scope.currentUser.resource_uri,
                title: $scope.title,
                content: $scope.content,
                course: $rootScope.course.resource_uri
            });

            q.$save(function () {
                // Success
                Course.get({id: $rootScope.course.id}, function (course) {
                    $rootScope.course = course;
                    $scope.isError = false;
                    $scope.loading = false;
                    $scope.isModalOpen = false;
                });
            }, function (response) {
                $scope.errors = response.data;
                $scope.isError = true;
                $scope.loading = false;
            });
        }
    }])

    .controller('AnswerSubmission', ['$scope', '$rootScope', 'Answer', 'Course', function ($scope, $rootScope, Answer, Course) {
        $scope.errors = {};
        $scope.loading = false;

        $scope.answer = function (question) {
            $scope.loading = true;
            var ans = new Answer({
                question: question.resource_uri,
                user: $scope.currentUser.resource_uri,
                content: $scope.answerMessage
            });
            ans.$save(function () {
                // Success
                Course.get({id: $rootScope.course.id}, function (course) {
                    $rootScope.course = course;
                    $scope.isError = false;
                    $scope.loading = false;
                });
            }, function (response) {
                $scope.errors.answer = response.data.answer.content;
                $scope.isError = true;
                $scope.loading = false;
            });
        }
    }])


    .controller('ActivityCtrl', ['$scope', 'CourseActivity', function ($scope, CourseActivity) {
        $scope.$watch('course', function (newValue, oldValue) {
            if (newValue != oldValue) {
                $scope.activities = CourseActivity.get({course: $scope.course.id}, function () {
                    // Success
                    $scope.activities = $scope.activities.objects;
                });
            }
        });
    }])

;
