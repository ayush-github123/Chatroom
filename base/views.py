from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q # We imported Q for the search functionality i.e. searching by name or email
from django.http import HttpResponse
from .models import Room, Topic, Messages, blog
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout # We imported the login and logout functions from the auth module
from .forms import RoomForm, BlogForm
from django.contrib import messages 
from django.contrib.auth.decorators import login_required # We imported the login_required decorator from the auth module
# Create your views here.

def home(request):
    return redirect('roomDisplay')


def room(request, pk):
    room = get_object_or_404(Room, pk=pk)   
    room_messages = room.messages_set.all().order_by('-created')
    room_participants = room.participants.all()

    if request.method == "POST":
        message = Messages.objects.create( # We used the create method to create a new message
            user=request.user,
            room=room,
            body=request.POST.get('message_body'), # We used the get method to get the message body from the POST request
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id) # Redirect to the room page after posting a message

    return render(request, 'base/room.html', {'room': room, 'room_messages': room_messages, 'room_participants': room_participants})



def userProfile(request, pk):
    user = get_object_or_404(User, pk=pk)
    room = user.room_set.all()
    room_messages = user.messages_set.all() # We used the message_set to get all messages from the user
    topics = Topic.objects.all()
    room_count = room.count()
    context = {"user":user, "rooms":room, "room_messages":room_messages, "topics":topics, "room_count":room_count}
    return render(request, 'base/profile.html', context)



def roomDisplay(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    topic = Topic.objects.all()
    room = Room.objects.filter(
        Q(topic__name__icontains=q) |   #The double underscore (__) is a Django ORM lookup to access related fields from a foreign key relationship.
        Q(name__icontains=q) |          # The | is a logical OR operator imported from django.db.models 
        Q( description__icontains=q) |  # The icontains is a lookup that returns all rows where the given field contains the specified value
        Q(host__username__icontains=q)  
    )
    room_messages = Messages.objects.filter(Q(room__topic__name__icontains=q)) # We used the filter method to filter the messages based on the search query
    room_count = room.count()   # We used the count() method to get the number of rooms that match the search query

    return render(request, 'base/home.html', {"rooms":room, "topics":topic, "room_count":room_count, "room_messages": room_messages})



@login_required(login_url='login')  # This is a decorator that checks if the user is logged in before allowing them to access the view
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)  # We did commit to False to prevent the room from being saved to the database yet
            room.host = request.user # We set the host of the room to the current user
            room.save()
            return redirect('roomDisplay')
    context = {'form':form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = get_object_or_404(Room, pk=pk)
    form = RoomForm(instance=room) #instance=room is for pre-filled data in the form

    if request.user != room.host:
        return HttpResponse("You don't have permission to update this room")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('roomDisplay')

    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == "POST":
        room.delete()
        return redirect('roomDisplay')
    return render(request, 'base/deleteRoom.html', {"obj":room})



@login_required(login_url='login')
def deleteMessage(request, pk):
    room_message = get_object_or_404(Messages, pk=pk)

    if request.method == "POST":
        room_message.delete()
        return redirect('room', pk=room_message.room.id)
        # return redirect(request.META.get('HTTP_REFERER', 'default_url')) # This will redirect the user back to the previous page or default_url if there is no previous page
    return render(request, 'base/deleteRoom.html', {"obj":room_message})




def registration(request):

    if request.user.is_authenticated:
        return redirect('roomDisplay')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        email = request.POST['email']


        if User.objects.filter(username=username).exists(): # check if username already exists
            messages.error(request, 'Username already exists')
            return render(request, 'base/register.html')
        
        if User.objects.filter(email=email).exists(): # check if email already exists
            messages.error(request, 'Email aleardy exists')
            return render(request, 'base/register.html')

        if(password != confirm_password): # check if password and confirm password are the same
            messages.error(request, 'Passwords do not match')
            return render(request, 'base/register.html')
        
        user = User.objects.create_user(username=username, email=email, password=password) # create user
        user.save()
        messages.success(request, 'Registration Successfull, Please Login')
        return redirect('login')

    else:
        return render(request, 'base/register.html')



def login(request):

    if request.user.is_authenticated:
        return redirect('roomDisplay')

    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password) # authenticate user

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Welcome, {username}!")
            return redirect('roomDisplay')
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'base/login.html')

    return render(request, 'base/login.html')


def logout(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('roomDisplay')



def blog_page(request):
    blogs = blog.objects.all()
    return render(request, 'base/blog.html', {"blogs":blogs})

@login_required(login_url='login')
def Createblog(request):
    if request.user.is_authenticated:
        if request.method == 'POST':    
            forms = BlogForm(request.POST)
            if forms.is_valid():
                forms.save()
                return render(request, 'base/blog-form.html', {"forms": forms})
    return render(request, 'base/blog-form.html')


def about(request):
    return render(request, 'base/aboutme.html')