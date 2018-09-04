from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_str
from .models import YTSearchQuery
from .forms import UserForm
from random import randint
from bs4 import BeautifulSoup
import subprocess
import requests
import json
import os


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                if request.POST['next']:
                    return redirect(request.POST['next'])
                else:
                    homeURL = 'YTApp/base.html'
                    return render(request, homeURL)
            else:
                return render(request, 'YTApp/login.html', {'error_message': 'Your account has been disabled', 'squares':'fromLogin'})
        else:
            return render(request, 'YTApp/login.html', {'error_message': 'Invalid login', 'squares':'fromLogin'})
    return render(request, 'YTApp/login.html', {'squares':'fromLogin'})


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
        'squares': 'fromLogin',
    }
    return render(request, 'YTApp/login.html', context)


class UserFormView(View):
    form_class = UserForm
    template_name = 'YTApp/registration_form.html'

    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            username = smart_str(form.cleaned_data['username'])
            password = form.cleaned_data['password']

            if 'guest' in username:
                password = smart_str(password) + 'someRandWord'
                user.set_password(password)
                user.save()
                randGuest = Group.objects.get(name='RandomGuest')
                randGuest.user_set.add(user)
                if user is not None:
                    user = authenticate(username=username, password=password)  # **Auth here**
                    login(request, user)
                    return redirect('YTApp:ytHome')
            else:
                user.set_password(password)
                user.save()
                groupRandoms = Group.objects.get(name='RandomRegistered')
                groupRandoms.user_set.add(user)

            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('YTApp:ytHome')

        return render(request, self.template_name, {'form':form})


def ytHome(request):
    if request.user.is_authenticated():
        print('User is an authenticated user')
    else:
        print('--------------User is a New Guest. User That has not signed in. Special greetings here. -------------')
        usernameRand = 'G' + str(randint(0, 999999))
        passWord = usernameRand + 'exodppa'

        u = User.objects.create_user(username=usernameRand, password=passWord, first_name="Anonymous")
        randGuest = Group.objects.get(name='RandomGuest')
        randGuest.user_set.add(u)
        authenticate(user=u)
        login(request, u)

    return render(request, 'YTApp/base.html')


@login_required(login_url='/login_user/')
def YTmp3Success(request, ytVidUrlmp3):
    responseData={}
    max_yt_video_len = 30
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEDIA_ROOT_YTCC = os.path.join(BASE_DIR, 'media', 'ytmp3s')
    os.chdir(MEDIA_ROOT_YTCC)

    if request.GET['j']:
        a = request.GET['a']
        j = request.GET['j']
        aj = a + "?" + j
    else:
        aj = ytVidUrlmp3

    try:
        print('tyring')
        batcmdCheck = 'youtube-dl --skip-download --get-title ' + aj
        result = subprocess.check_output(batcmdCheck, shell=True)
        temp0 = result.decode("utf-8")
        temp = temp0.replace("\n", "")
        print(temp)
        mp3Name = temp + '.mp3'
        for f in os.listdir(MEDIA_ROOT_YTCC):
            if f == mp3Name:
                print('the q exist, fetch the mp3.')
                try:
                    responseData['mp3Name'] = mp3Name
                except:
                    responseData['result'] = 'oh no!'
                return HttpResponse(json.dumps(responseData), content_type='application/json')

        batcmdLen = 'youtube-dl --skip-download --get-duration ' + aj
        resultLen = subprocess.check_output(batcmdLen, shell=True)
        strResultLen = resultLen.decode("utf-8")
        temp00 = strResultLen.replace("\n", "")
        print(temp00)
        if ":" in temp00:
            if int(temp00.split(':')[0]) > max_yt_video_len:
                print('the video length is greater than 45 minutes, return with sorry.')
                responseData['mp3Name'] = 'oh no!'
                return HttpResponse(json.dumps(responseData), content_type='application/json')


        print('donwloading mp3')
        batcmdDwnld = 'youtube-dl -o "~/Desktop/YTPro/media/ytmp3s/%(title)s.%(ext)s" --extract-audio --audio-format mp3 ' + aj
        result2 = subprocess.check_output(batcmdDwnld, shell=True)
        resultString = result2.decode("utf-8")
        resultString.rsplit('/', 1)
        r = resultString.rsplit('/', 1)[1]
        r.rsplit('.', 1)
        mp3Name2 = r.rsplit('.', 1)[0] + '.mp3'

    except subprocess.CalledProcessError as e:
        print(e.output)

    try:
        responseData['mp3Name'] = mp3Name2
    except:
        responseData['message'] = 'error: did not run properly. Check views.py for handlingAjax. LoginReq'

    return HttpResponse(json.dumps(responseData), content_type='application/json')


@login_required(login_url='/login_user/')
def YTSearchSuccess(request):
    ytQuery = request.GET['ytQuery']
    if YTSearchQuery.objects.filter(ytQuery=ytQuery).count():
        ytQ = YTSearchQuery.objects.get(ytQuery=ytQuery)
        # Replacing unwanted symbols.
        a = ytQ.ytQueryUrls.replace("['", "")
        b = a.replace("[u'", "")
        c = b.replace("']", "")
        d = c.replace("'", "")
        e = d.replace(" ", "")
        myQlist = e.split(",")  # Refactor this later. Might break.

        x = ytQ.vidTitle.replace("'", "")
        y = x.replace('"', "")
        tList = y.split(",")
        responseData = {}
        try:
            responseData['myQueryList'] = myQlist
            responseData['myTitleList'] = tList
        except:
            responseData['message'] = 'error'

        return HttpResponse(json.dumps(responseData), content_type='application/json')

    else:
        myQueryList = []
        myTitleList = []
        url = 'https://www.youtube.com/results?search_query=' + ytQuery
        source_code = requests.get(url)
        plain_text = source_code.text
        soup = BeautifulSoup(plain_text, "html.parser")

        for i in soup.select("h3 > a"):
            if (i['href']).startswith("/watch"):
                myQueryList.append(i['href'])
                x = i['title'].replace(",", "")
                y = x.replace("'", "")
                z = y.replace('"', "")
                myTitleList.append(z)

        YTSearchQuery.objects.create(user=request.user,
                                     ytQuery=ytQuery,
                                     ytQueryUrls=myQueryList,
                                     vidTitle=myTitleList)

    responseData={}
    try:
        responseData['myQueryList'] = myQueryList
        responseData['myTitleList'] = myTitleList
    except:
        responseData['message'] = 'error: did not run properly. Check views.py for handlingAjax'

    return HttpResponse(json.dumps(responseData), content_type='application/json')
