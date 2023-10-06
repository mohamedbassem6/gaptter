from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def chat_home(request):
    # user = request.user

    # convos = user.conversation_set.all()

    # context_convo = dict()
    # context_convo_list = list()
    # for convo in convos:
    #     context_convo['user'] = convo.users.exclude(username=user.username)
    #     context_convo['last_message'] = convo.message_set.last()

    return render(request, 'chat/chat_home.html')

@login_required
def chat_convo(request, convo_id):
    return render(request, 'chat/chat_convo.html')