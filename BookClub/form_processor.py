from BookClub.forms import CreateForumCommentForm, CreatePostForm
from BookClub.models import BookList

def ForumPostForm(request):
    return {
        "forum_post_form" : CreatePostForm(),
        "forum_comment_form" : CreateForumCommentForm(),
    }


def BooklistContext(request):
    if request.user.is_authenticated:
        booklists = BookList.objects.filter(creator=request.user)
        return {
            'lists': booklists
        }

    return {}
