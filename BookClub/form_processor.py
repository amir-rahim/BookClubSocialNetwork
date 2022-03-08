from BookClub.forms import CreateForumCommentForm, CreatePostForm


def ForumPostForm(request):
    return {
        "forum_post_form" : CreatePostForm(),
        "forum_comment_form" : CreateForumCommentForm(),
    }