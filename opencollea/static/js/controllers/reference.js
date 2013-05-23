
app

    .controller('ReferenceCtrl', ['$scope', '$rootScope', '$routeParams', 'Reference', 'Course',
    function($scope, $rootScope, $routeParams, Reference, Course) {

        Course.get({machine_readable_title: $routeParams.courseTitle}, function (course) {
            // Success
            $rootScope.course = course.objects[0];
        }, function () {
            // Fail
        });

        $scope.references = Reference.query();

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

        $scope.createNewReference = function () {
            $scope.loading = true;
            var r = new Reference({
                user: $scope.currentUser.resource_uri,
                course: $rootScope.course.resource_uri,
                author: $scope.author,
                title: $scope.title,
                abstract: $scope.abstract,
                link: $scope.link,
                note: $scope.note

            });

            r.$save(function () {
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
;
