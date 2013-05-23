from django_assets import Bundle, register

# CSS
css = Bundle('css/bootstrap.css',
             'css/bootstrap-responsive.css',
             'css/opencollea.css',
             filters='cssmin', output='css/opencollea.css')
register('css_all', css)

# JavaScript
js = Bundle('js/jquery-2.0.0.js',
            'js/bootstrap.js',
            'js/angular.js',
            #'js/angular_resource.js',
            'js/angular-resource.js',
            'js/http-auth-interceptor.js',
            'js/services.js',
            'js/app.js',
            'js/controllers.js',
            'js/raphael.js',
            'js/pie.js',
            'js/etherpad.js',
            'js/ui-bootstrap-tpls-0.3.0.js',
            'js/services/md5.js',
            'js/services/profile.js',
            'js/services/course.js',
            'js/services/discover.js',
            'js/services/chat.js',
            'code_register/app/scripts/services/code_register.js',
            'js/directives/form.js',
            'js/directives/gravatar.js',
            'js/controllers/profile.js',
            'js/controllers/course.js',
            'js/controllers/home.js',
            'js/controllers/discover.js',
            'js/socket.io.js',
            'js/controllers/chat.js',
            output='js/opencollea.js')
register('js_all', js)
