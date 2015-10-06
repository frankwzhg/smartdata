##################################################################################################
## all letter is litte in keyword, and view word is at the end of keyword. under sash between words
####################################################################################################


from django.contrib.auth.decorators import login_required
from django.core.context_processors import csrf
from forms import *
from models import *
import hashlib, random, datetime
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User



# Create your views here.

## user registrate and save it into database, and the same time save user profile into userprofile table in database

def user_registration_view(request):
    args = {}  # parameter dictionary
    args.update(csrf(request))   # update request information in dictionary

    if request.method == "POST":
        form = RegistrationForm(request.POST)  # registraiton form save a variable user
        args['form'] = form   # form add parameter dictionary
        if form.is_valid():
            form.save()  # if form is valid, we will save registration form inform into database and create a user
            # account recoder, and set user is inactive status by regtistrationForm save attribute
            username = form.cleaned_data['username']  #get post username and email cleaned
            email = form.cleaned_data['email']
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]  # randomly create salt
            activation_key = hashlib.sha1(salt+email).hexdigest()    # random salt and mail, create activation key
            key_expires = datetime.date.today() + datetime.timedelta(1)  # set expires date after 48 hours

            # get user object form user table
            user = User.objects.get(username=username)

            # create and save user profile, and set default value for website is blank, birthday is blank, head pic is blank

            new_profile = UserProfle(user=user, activation_key=activation_key, key_expires=key_expires)
            new_profile.birthday = datetime.datetime.today()
            new_profile.save()

            # send mail with active url
            email_subject = 'Account confirm'
            email_body = 'Hey %s, thanks for your registration. your activation link will expire in 48 hours, please log ' \
                         'in your mail box to click http://localhost:8000/accounts/confirm/%s' %(username, activation_key)
            send_mail(email_subject, email_body, 'admin@frankdata.com.cn', [email], fail_silently=False)
            return HttpResponse("you have registrated your account successfully, please login your mailbox to active it")
        else:
             print form.errors
    else:

        args['form'] = RegistrationForm()

    return render_to_response('accounts/registration.html', args, RequestContext(request))

def user_active_view(request, activation_key):
    # get request user record from user profile table
    user_profile = get_object_or_404(UserProfle, activation_key=activation_key)

    status_dic = {}
    #check if the activation key has expired, if it hase then render confirm_expired.html
    if user_profile.key_expires < timezone.now():
        status_dic['status'] = 'expired'
        status_dic['message'] = 'please contact your admin'
        # if the key hasn't expired save user and set him as active and render some template to confirm activation
    else:
        user = user_profile.user
        user.is_active = True
        user.save()
        status_dic['status'] = 'active'
        status_dic['url'] = '../../login'
    print status_dic
    return render_to_response('accounts/user_active.html', status_dic, RequestContext(request))


def user_login_view(request):
    context = RequestContext(request)
    context_dict = {}
    if request.user.is_authenticated():
        context_dict['login'] = 'you have been loged in'
    # If this request is http post, try to pull out the relevant information
    if request.method == 'POST':
        # Gather username and password provided by user
        # This information is obtained from the login form
            # We use request.POST.get(<variable>) as opposed to request.POST['<variable>'],
            # because the request.POST.get(<variable>)return None, if the value does not exist
            # While the request.POST(<variable>) will raise key error exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Use django's machinery to attempt to see if username/password
        # combination is valide - a user object is returned if it is
        user = authenticate(username=username, password=password)

        # If we have a user object, the details are correct
        # If None( Python's way of representing the absence of a value), no user
        # with matching credentials was found
        if user is not None:
            # is the account is active? it can have been disable.
            if user.is_active:
                # If the account is valid and active, we can log the user in
                # We can send this user back to homepage
                login(request, user)
                # return HttpResponseRedirect('/rango/')
                return HttpResponse("you have loged in")
            else:
                # An inactive account was used - no logging in
                context_dict['disableed_account'] = True
                return HttpResponse("Your rango's account is disable")
        else:
            # Bad login details were provide, So we can't log the user in
            context_dict["user_name"] = username
            context_dict['Password'] = password
            context_dict['bad_details'] = True
            # return HttpResponse('Invalid login details supplied')
            # return HttpResponseRedirect('/rango/login/')
            return render_to_response('accounts/login.html', context_dict, context)
            # return HttpResponse("please input right user information")
    # The request is not a HTTP POST, so display login form
    # This scenario would most likely be a HTTP GET
    else:
        # No context variable to pass to the template system, hence the
        # blank dictionary object
        return render_to_response('accounts/login.html', context_dict, context)

@login_required
def user_logout(request):
    logout(request)
    # return HttpResponseRedirect('/rango/login/')
    return HttpResponseRedirect('/')


## reset user password when user don't remeber his/her password and can't login. user have to provide mail address
# that he/she registrate account
def reset_password_view(request):
    context_dic = {}   # define blank dictionary for form errors message
    if request.method == "POST":  # adjust if post method
        form = ResetPasswordForm(request.POST)  # get form
        context_dic['form'] = form
        if form.is_valid():  # check form is valid
            username = form.cleaned_data['username']
            mail = form.cleaned_data['email']
            newpassword1 = form.cleaned_data['password1']
            newpassword2 = form.cleaned_data['password2']

            if newpassword1 != newpassword2 or len(newpassword1)<4:   #check user password matching and length
                context_dic['pwd_errors'] = "your password doesn't matching or is short"  #return error message
            else:
                try:
                    user = User.objects.get(username=username, email=mail)
                    user.set_password(newpassword1)
                    user.is_active = False
                    user.save()

                    # user_profile = UserProfle.objects.get(user_id=user.id)
                    # username = form.cleaned_data['username']  #get post username and email cleaned
                    email = form.cleaned_data['email']
                    salt = hashlib.sha1(str(random.random())).hexdigest()[:5]  # randomly create salt
                    activation_key = hashlib.sha1(salt+email).hexdigest()    # random salt and mail, create activation key
                    key_expires = datetime.date.today() + datetime.timedelta(1)  # set expires date after 48 hours
                    user_profile = UserProfle.objects.get(user_id=user.id)
                    user_profile.activation_key = activation_key
                    user_profile.key_expires = key_expires
                    user_profile.save()
                    # send mail with active url
                    email_subject = 'Account confirm'
                    email_body = 'Hey %s, your password has benn reset, but you account is inactive now, ' \
                                 'so you have to log in your mailbox to active it. your activation link ' \
                                 'will ' \
                                 'expire in 48 hours, please log ' \
                             'in your mail box to click http://localhost:8000/accounts/confirm/%s' %(username, activation_key)
                    send_mail(email_subject, email_body, 'admin@frankdata.com.cn', [email], fail_silently=False)
                    return HttpResponse("your password is reset successfully now, please login your mailbox "
                                        "to active "
                                        "it")
                except:
                    context_dic['errors'] = 'please check your information, then try it again'

        else:
            print form.errors


    return render_to_response('accounts/resetpassword.html', context_dic, RequestContext(request))

# user know account password, but he/she want to change it to newpassword for some reason
@login_required
def change_passwd_view(request):
    args = {}
    user_name = request.user.username  #get request user id
    print user_name
    # object = User.objects.get(username=user_name)  #get user object from User table
    if request.method == 'POST':
        print request.user.username
        username = request.POST.get('username')
        if username == user_name:
        # form = ChangePasswordForm(request.POST)
            old_password = request.POST.get('old_password')  #get user old password
            user = authenticate(username=user_name, password=old_password)  # authenticate user is validation user

            if user is not None:  #if user object exist
                print 'test'
                newpassword1 = request.POST.get('new_password1')
                newpassword2 = request.POST.get('new_password2')
                if newpassword1 != newpassword2 or len(newpassword1)<4:
                    print 'test1'
                    args['pwd_errors'] = "your password does not match, or it is too short"
                else:
                    print 'test1'
                    user.set_password(newpassword1)
                    user.save()
                    args['success'] = 'your password is changed'
        else:
            args['other_user'] = 'you can only change your password by this application'
    return render_to_response('accounts/change_password.html', args, RequestContext(request))



# update user profile

@login_required
def update_profile_view(request):
    user_id = request.user.id
    if request.method == 'GET':
        # get information from database:

        try:
            user_info = UserProfle.objects.get(user_id=user_id)
            print user_info.birthday
            user = User.objects.get(id=user_id)
            context_dic = {'form': user_info, 'user_id': user_info.user_id, 'user_picture': user_info.picture, 'birth_day': user_info.birthday, 'website':user_info.website, 'user_firstname':user.first_name, 'user_lastname':user.last_name, 'user_email':user.email}
            return render_to_response('accounts/user_profile_update.html', context_dic, RequestContext(request))
        except:
            return render_to_response('accounts/user_profile_update.html', {}, RequestContext(request))
    else:
        user = User.objects.get(id=user_id)
        user_profile = UserProfle.objects.get(user_id=user_id)
        user_form = UserInfoForm(request.POST, instance=User(id=user_id))
        profile_form = ProfileForm(request.POST, instance=UserProfle(user_id=user_id))
        if user_form.is_valid() and profile_form.is_valid():
            user.first_name = request.POST.get('firstname')
            user.last_name = request.POST.get('lastname')
            user.email = request.POST.get('email')
            user.save()




            user_profile.website = request.POST.get('website')
            user_profile.birthday = request.POST.get('birthday')
            user_profile.save()
            # args = {}
            # return

        # user_form.first_name = request.POST.get('firstname')
        # print request.POST.get('firstname')
        # user_form.last_name = request.POST.get('lastname')
        # print user_
        # profile_form = [ProfileForm(request.POST, prefix=str(x), instance=UserProfle(user_id=user_id)) for x in
        #                 range(0,3)]
        # if user_form.is_valid() and all([cf.is_valid() for cf in profile_form]):
        #     print "test"
        #     # new_user = user_form.save()
        #     # print new_user
        #     for cf in profile_form:
        #         new_profile = cf.save()
        #         print new_profile
        #         new_profile.user = new_user
                # new_profile.save()
    return render_to_response('accounts/user_profile_update.html', {}, RequestContext(request))
    #     if profile_form.is_valid():
    #         user_profile = UserProfile.objects.get(user_id=user_id)
    #         profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
    #         profile_form.save()
    #         return redirect('/rango/')
    #
    #     else:
    #         user_profile = UserProfile.objects.get(user_id=user_id)
    #         profile_form = UserProfileForm(instance=user_profile)
    #         url = request.POST.get("website")
    #         birthday = request.POST.get("birthday")
    #         pic = request.POST.get("picture")
    #         # print url
    #         # print birthday
    #         # print pic
    #         return render_to_response('rango/user_profile_update.html', {'form': profile_form}, context_instance=RequestContext(request))
    #     # user_info = UserProfile.objects.get(user_id=user_id)