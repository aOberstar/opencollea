from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from tastypie.authorization import Authorization
from tastypie.http import HttpUnauthorized
from tastypie.resources import ModelResource, ALL
from django.conf.urls import url
from tastypie.utils import trailing_slash
from tastypie import fields, resources

from opencollea.models import Course, UserProfile, Question, EtherpadNote, \
    CourseActivity
from opencollea.forms import UserProfileForm, RegistrationDetailsForm, \
    EtherpadNoteForm, Answer, AnswerForm, QuestionForm

from fixes.tastypie.validation import ModelCleanedDataFormValidation
import code_register.resources
from find_courses.models import Course as MoocCourse
from find_courses.resources import MoocCourseResource


class LoginResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'auth'
        excludes = ['email', 'password', 'is_superuser']
        #authentication = SessionAuthentication()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/login%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('login'), name="api_login"),
            url(r'^(?P<resource_name>%s)/logout%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('logout'), name='api_logout'),
            url(r'^(?P<resource_name>%s)/currentUser%s$' %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('current_user'), name='api_current_user'),
        ]

    def login(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        data = self.deserialize(request, request.raw_post_data,
                                format=request.META.get('CONTENT_TYPE',
                                                        'application/json'))

        username = data.get('username', '')
        password = data.get('password', '')
        redirect_to = data.get('redirectTo', '/')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return self.create_response(request, {
                    'success': True,
                    'redirectTo': redirect_to
                })
            else:
                return self.create_response(request, {
                    'success': False,
                    'reason': 'inactive',
                })
        else:
            return self.create_response(request, {
                'success': False,
                'reason': 'incorrect',
            })

    def logout(self, request, **kwargs):
        self.method_check(request, allowed=['get'])
        if request.user and request.user.is_authenticated():
            logout(request)
            return self.create_response(request, {'success': True})
        else:
            return self.create_response(request, {'success': False},
                                        HttpUnauthorized)

    def current_user(self, request, **kwargs):
        user = {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'resource_uri': '/api/v1/user_profile/' + str(request.user.id)
        }
        return self.create_response(request, user)


class UserProfileResource(ModelResource):
    courses_enrolled = fields.ToManyField(
        'opencollea.resources.CourseResource', 'courses_enrolled',
        related_name='courses_enrolled')
    language_code = fields.ForeignKey(
        code_register.resources.LanguageResource, 'language_code', null=True)
    age_range = fields.ForeignKey(
        code_register.resources.AgeRangeResource, 'age_range', null=True)
    gender = fields.ForeignKey(
        code_register.resources.GenderResource, 'gender', null=True)
    occupation = fields.ForeignKey(
        code_register.resources.OccupationResource, 'occupation', null=True)
    area_of_study = fields.ForeignKey(
        code_register.resources.AreaOfStudyResource,
        'area_of_study', null=True)

    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'user_profile'
        filtering = {
            'username': ALL,
        }
        excludes = ['password', 'courses_enrolled']
        put_excludes = ['courses_enrolled']
        post_excludes = ['courses_enrolled']
        authorization = Authorization()
        validation = ModelCleanedDataFormValidation(form_class=UserProfileForm)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)"
                r"/courses_not_enrolled%s$"
                % (self._meta.resource_name,
                   trailing_slash()),
                self.wrap_view('get_courses_not_enrolled'),
                name="api_get_courses_not_enrolled"),
        ]

    def save_m2m(self, bundle):
        """
        Handles the saving of related M2M data.

        Due to the way Django works, the M2M data must be handled after the
        main instance, which is why this isn't a part of the main ``save``
        bits.

        Currently slightly inefficient in that it will clear out the whole
        relation and recreate the related data as needed.
        """
        for field_name, field_object in self.fields.items():
            if not getattr(field_object, 'is_m2m', False):
                continue

            if not field_object.attribute:
                continue

            if field_object.blank:
                continue

            if field_object.readonly:
                continue

            # Get the manager.
            related_mngr = getattr(bundle.obj, field_object.attribute)
            through_class = getattr(related_mngr, 'through', None)

            if through_class and not through_class._meta.auto_created:
                # ManyToMany with an explicit intermediary table.
                # This should be handled by with specific code, so continue
                # without modifying anything.
                # NOTE: this leaves the bundle.needs_save set to True
                continue

            related_bundles = bundle.data[field_name]

            # Remove any relations that were not POSTed
            if through_class:
                # ManyToMany with hidden intermediary table.
                # Use the manager to clear out the relations.
                related_mngr.clear()
            else:
                # OneToMany with foreign keys to this object.
                # Explicitly delete objects to pass in the user.
                posted_pks = [b.obj.pk
                              for b in related_bundles if b.obj.pk]
                if self._meta.pass_request_user_to_django:
                    tmpArr = related_mngr.for_user(user=bundle.request.user)
                    for obj in tmpArr.exclude(pk__in=posted_pks):
                        obj.delete(user=bundle.request.user)
                else:
                    for obj in related_mngr.all().exclude(pk__in=posted_pks):
                        obj.delete()

            # Save the posted related objects
            related_objs = []
            for related_bundle in related_bundles:
                related_objs.append(related_bundle.obj)
                """
                if related_bundle.needs_save:
                    if self._meta.pass_request_user_to_django:
                        related_bundle.obj.save(user=bundle.request.user)
                    else:
                        related_bundle.obj.save()
                    related_bundle.needs_save = False
                """

            if through_class:
                # ManyToMany with hidden intermediary table. Since the save
                # method on a hidden table can not be overridden we can use the
                # related_mngr to add.
                related_mngr.add(*related_objs)

    def get_courses_not_enrolled(self, request, **kwargs):
        """
        Za uporabnika vrne razreda v katere ni vpisan.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        course_resource = CourseResource()
        objects = []
        for course in Course.objects.exclude(
                id__in=[c.id for c in UserProfile.objects.get
                        (pk=kwargs.get('pk', 0)).courses_enrolled.all()]
        ):
            bundle = course_resource.build_bundle(obj=course, request=request)
            bundle = course_resource.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)


class QuestionResource(ModelResource):
    # dostop preko foreignKey
    course = fields.ToOneField('opencollea.resources.CourseResource', 'course')
    user = fields.ToOneField(UserProfileResource, 'user', full=True)
    answers = fields.ToManyField('opencollea.resources.AnswerResource',
                                 'answers', full=True, null=True)

    class Meta:
        queryset = Question.objects.all()
        resource_name = 'question'
        authorization = Authorization()
        validation = ModelCleanedDataFormValidation(
            form_class=QuestionForm
        )
        ordering = ['published']


class AnswerResource(ModelResource):
    user = fields.ToOneField(UserProfileResource, 'user', full=True)
    question = fields.ToOneField(QuestionResource, 'question')

    class Meta:
        queryset = Answer.objects.all()
        resource_name = 'answer'
        filtering = {
            'question': ALL,
        }
        ordering = ['id']
        authorization = Authorization()
        validation = ModelCleanedDataFormValidation(
            form_class=AnswerForm
        )


class CourseResource(ModelResource):
    mooc = fields.ForeignKey('find_courses.resources.MoocCourseResource',
                             'mooc', null=True)
    questions = fields.ToManyField('opencollea.resources.QuestionResource',
                                   'questions', null=True, full=True)

    class Meta:
        queryset = Course.objects.all()
        resource_name = 'course'
        filtering = {
            'id': ALL,
            'machine_readable_title': ALL,
            'mooc': ALL,
        }
        ordering = ['id']
        authorization = Authorization()

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/new%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('new'), name="course_new"),
            url(r"^(?P<resource_name>%s)/mooc_courses_noone_took%s$" %
                (self._meta.resource_name, trailing_slash()),
                self.wrap_view('mooc_courses_noone_took'),
                name="api_mooc_courses_noone_took"),
        ]

    def new(self, request, **kwargs):
        from opencollea.models import Course

        self.method_check(request, allowed=['post'])
        required = []
        data = self.deserialize(request, request.raw_post_data,
                                format=request.META.get('CONTENT_TYPE',
                                                        'application/json'))

        c = Course()
        c.title = data.get('title', '')  # required
        c.machine_readable_title = data.get('machine_readable_title', '')
        c.description = data.get('description', '')  # required
        c.website = data.get('website', '')

        if c.title == '':
            required.append('title')

        if c.description == '':
            required.append('description')

        if len(required) > 0:
            return self.create_response(request, {
                'required': required
            })
        else:
            c.save()

        #, machine_readable_title = d_machine_readable_title,
        # description = d_description, website = d_website
        if c.pk > 0:
            return self.create_response(request, {
                'success': True
            })
        else:
            return self.create_response(request, {
                'error': 'Entry not successful'
            })

    def mooc_courses_noone_took(self, request, **kwargs):
        """
        Mooc coursi iz katerih se ni narejenega nobenega "nasega" razreda.
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        mooc_resource = MoocCourseResource()
        objects = []
        for mooc in MoocCourse.objects.exclude(
                pk__in=[c.mooc_id for c in
                        Course.objects.filter(mooc__isnull=False)]
        ):
            bundle = mooc_resource.build_bundle(obj=mooc, request=request)
            bundle = mooc_resource.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)


class RegistrationDetailsResource(ModelResource):
    class Meta:
        queryset = UserProfile.objects.all()
        resource_name = 'registration_details'
        fields = ['first_name', 'last_name', 'email', 'password']
        authorization = Authorization()
        validation = ModelCleanedDataFormValidation(
            form_class=RegistrationDetailsForm)

    def dehydrate(self, bundle):
        # We don't send password to client
        bundle.data['password'] = ''

        return bundle


class EtherpadNoteResource(ModelResource):
    user = fields.ForeignKey(UserProfileResource, 'user')
    course = fields.ForeignKey(CourseResource, 'course')

    class Meta:
        queryset = EtherpadNote.objects.all()
        resource_name = 'etherpad_note'
        filtering = {
            'pad_id': ALL,
            'machine_readable_title': ALL,
            'course': ALL,
        }
        ordering = ['id']
        authorization = Authorization()
        validation = ModelCleanedDataFormValidation(
            form_class=EtherpadNoteForm
        )


class CourseActivityResource(ModelResource):
    user = fields.ForeignKey(UserProfileResource, 'user', full=True)
    course = fields.ForeignKey(CourseResource, 'course')
    class Meta:
        queryset = CourseActivity.objects.all()
        resource_name = 'course_activity'
        filtering = {
            'user': ALL,
            'course': ALL,
        }

