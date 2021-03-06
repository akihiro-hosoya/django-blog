from django.shortcuts import render

# Create your views here.
'''
○ビューの機能
    フォームに処理を依頼
    モデルにデータベースの操作を依頼
    テンプレートにHTMLの生成を依頼
    画面遷移先の判断
'''

'''
○ビューの種類
    ・クラスベース汎用ビュー
        すでにビューとしての機能をdjango.views.genericに備えていて、importで継承して使用
        簡単にViewを作成することができる
    ・関数ベースビュー
        ビューで必要なレスポンスを返すreturn処理まで記述する必要がある
'''

'''
○クラスベース汎用ビューの種類
    TemplateView : テンプレートを使用して、何かを表示する汎用ビュー
    ListView : 一覧を表示する汎用ビュー
    DetailView : 詳細ページを表示する汎用ビュー
    CreateView : 新しくデータを追加するフォームを提供する汎用ビュー
    UpdateView : データを更新するフォームを提供する汎用ビュー
    DeleteView : データを削除する汎用ビュー
    RedirectView : リダイレクトに特化した汎用ビュー
    FormView : フォームを処理する汎用ビュー
'''

'''
設定した変数を使用したい場合には、汎用ビューで定義されている関数をオーバーライドする

普段はデフォルト値を使用して、変更したい時だけ値をオーバーライドする
○オーバーライドするクラス変数
    template_name : 
    model : 
    paginate_by : 
    queryset : 
    form_class : 
    success_url : 
    fields : 

○オーバーライドするメソッド
    get_context_data : 
    get_queryset : 
    form_valid : 
    form_invalid : 
    get_success_url : 
    delete : 
    get : 
    post : 
'''

from django.utils import timezone
from blog.models import Post, Comment, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from blog.forms import PostForm, CommentForm
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)

class CategoryView(ListView):
    model = Post
    template_name = 'blog/post_list.html'

    def get_queryset(self):
        category = Category.objects.get(name=self.kwargs['category'])
        queryset = Post.objects.order_by('-id').filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_key'] = self.kwargs['category']
        return context


class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    pagemate_by = 3

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
    # filter関数を使用して、公開順に投稿を並べるように指定

class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"

class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    template_name = 'blog/post_form.html'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    template_name = "blog/post_form.html"
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post


class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    template_name = 'blog/post_draft_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')



@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.publish()
    return redirect('post_detail', pk=pk)



class PostDeleteView(DeleteView):
    model = Post
    template_name = "blog/post_confirm_delete.html"
    success_url = reverse_lazy('post_list')

@login_required
def post_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/post_comment.html', {'form': form})

@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)

@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.delete()
    return redirect('post_detail', pk=comment.post.pk)

class AboutView(TemplateView):
    template_name = 'page/about.html'


'''
動的に変わるデータはViewで処理する
そして、get_queryset関数でテンプレートにクエリセットを渡す

「クエリ」＝「SQL文」：データベースに命令するもの
                    もしくは、検索キーワードのこと
＊「SQL」（言語）≠「クエリ（SQL文）」（命令文）

「クエリセット」＝クエリの実行結果
'''
