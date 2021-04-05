from .forms import *
from .models import *
from django.contrib.auth.decorators import login_required
from registr.forms import UserEditForm
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import View, ListView


# Create your views here.
def post_list(request):
    post_list = Post.objects.all()

    paginator = Paginator(post_list, 6)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    if page is None:
        start_index = 0
        end_index = 5
    else:
        (start_index, end_index) = proper_pagination(posts, index=4)

    page_range = list(paginator.page_range)[start_index:end_index]

    context = {'post': posts, 'page_range': page_range}
    return render(request, 'blog/post_list.html', context)


class GlobalSearch(ListView):
    model = Post
    template_name = "blog/global_search.html"
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super(GlobalSearch, self).get_context_data(**kwargs)

        query = self.request.GET.get('q')
        if query == '':
            post_list = Post.objects.all()

        else:
            post_list = Post.objects.filter(
                Q(title__icontains=query) |
                Q(author__username=query) |
                Q(body__icontains=query)
            )

        paginator = Paginator(post_list, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            result = paginator.page(page)
        except PageNotAnInteger:
            result = paginator.page(1)
        except EmptyPage:
            result = paginator.page(paginator.num_pages)

        if page is None:
            start_index = 0
            end_index = 5
        else:
            (start_index, end_index) = proper_pagination(result, index=4)

        page_range = list(paginator.page_range)[start_index:end_index]


        context['result'] = result
        context['page_range'] = page_range
        context['query'] = query
        return context


def post_detail(request, id, slug):
    post = get_object_or_404(Post, id=id, slug=slug)
    comments = Comment.objects.filter(post=post, reply=None).order_by('-id')
    is_like = True if post.likes.filter(id=request.user.id).exists() else False
    post.views = int(post.views) + 1
    post.save()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            content = request.POST.get('content')
            reply_id = request.POST.get('comment_id')
            comment_qs = None
            if reply_id:
                comment_qs = Comment.objects.get(id=reply_id)
            comment = Comment.objects.create(
                post=post,
                content=content,
                user=request.user,
                reply=comment_qs
            )
            return redirect(post.get_absolute_url())
    else:
        comment_form = CommentForm
    context = {
        'post': post,
        'is_like': is_like,
        'total_likes': post.total_likes(),
        'comment_form': comment_form,
        'comments': comments,
    }
    return render(request, 'blog/post_detail.html', context)


def proper_pagination(posts, index):
    start_index = 0
    end_index = 5
    if posts.number > index:
        start_index = posts.number - index
        end_index = start_index + end_index
    return start_index, end_index


def like_post(request):
    post = get_object_or_404(Post, id=request.POST.get('post_id'))
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return redirect(post.get_absolute_url())


class PostCreate(CreateView):
    model = Post
    fields = ['title', 'body', 'status']
    template_name = 'blog/post_create.html'
    success_url = "/"

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.info(self.request, f"Пост {form.instance.title} был опубликован")
        return super().form_valid(form)


class PostEdit(UpdateView):
    model = Post
    fields = ['title', 'body', 'status']
    template_name = 'blog/post_edit.html'
    success_url = "/"

    def form_valid(self, form):
        messages.success(self.request, f"Пост {form.instance.title} был успешно изменен")
        return super().form_valid(form)


class PostDelete(SuccessMessageMixin, DeleteView):
    model = Post
    template_name = 'blog/post_delete.html'
    success_url = "/"
    warning_message = "Пост %(title)s был удален"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.warning(self.request, self.warning_message % obj.__dict__)
        return super(PostDelete, self).delete(request, *args, **kwargs)


@login_required
def edit_profile(request):
    form = ProfileForm
    if request.method == 'POST':
        user_form = UserEditForm(data=request.POST or None, instance=request.user)
        profile_form = ProfileForm(
            data=request.POST or None,
            instance=request.user.profile,
            files=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('post_list')
        else:
            context = {
                'user_form': user_form,
                'profile_form': profile_form,
            }
            return render(request, 'blog/edit_profile.html')
    else:
        user_form = UserEditForm(instance=request.user)
        try:
            profile_form = ProfileForm(instance=request.user.profile)
        except User.profile.RelatedObjectDoesNotExist:
            Profile.objects.create(user=request.user)
            profile_form = ProfileForm(instance=request.user.profile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
        }
        return render(request, 'blog/edit_profile.html', context)