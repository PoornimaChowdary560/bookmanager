# books/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book
from .forms import RegisterForm, LoginForm, BookForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created. Please login.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'books/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # stores session
            messages.success(request, f'Welcome, {user.username}!')
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'books/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

def book_list(request):
    books = Book.objects.all()
    paginator = Paginator(books, 6)  # 6 books per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'books/book_list.html', {'page_obj': page_obj})

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'books/book_detail.html', {'book': book})

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.owner = request.user
            book.save()
            messages.success(request, 'Book added successfully.')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'books/book_form.html', {'form': form, 'create': True})

@login_required
def book_edit(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.owner != request.user:
        return HttpResponseForbidden("You are not allowed to edit this book.")
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated.')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    return render(request, 'books/book_form.html', {'form': form, 'create': False})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if book.owner != request.user:
        return HttpResponseForbidden("You are not allowed to delete this book.")
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted.')
        return redirect('dashboard')
    return render(request, 'books/book_confirm_delete.html', {'book': book})

@login_required
def dashboard(request):
    user_books = request.user.books.all()
    paginator = Paginator(user_books, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'books/dashboard.html', {'page_obj': page_obj})
